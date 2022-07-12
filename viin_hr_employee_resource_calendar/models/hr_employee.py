# -*- coding: utf-8 -*-
import threading
import logging

from pytz import utc, timezone
from datetime import date, datetime

from odoo import models, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import relativedelta
from odoo.addons.resource.models.resource_mixin import timezone_datetime

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_contracts(self, date_from, date_to, states=['open'], kanban_state=False):
        """
        Returns the contracts of the employee between date_from and date_to with option to include/exclude trial contract using given context
        """
        contracts = super(HrEmployee, self)._get_contracts(date_from=date_from, date_to=date_to, states=states, kanban_state=kanban_state)
        if not self._context.get('include_trial_contracts', True):
            trial_contracts = contracts.filtered(lambda c: c.trial_date_end and c.trial_date_end >= c.date_start)
            contracts = contracts - trial_contracts
        return contracts

    def _get_contracts_of_year(self, year):
        contracts = self.contract_ids.filtered(
            lambda c: c.state in ('open', 'close') \
                and c.date_start.year <= year
                and (not c.date_end or c.date_end.year >= year)
            )
        return contracts.sorted('date_start')

    def _get_non_contract_resource_calendar(self):
        self.ensure_one()
        return self.resource_calendar_id or self.company_id.resource_calendar_id
    
    def _get_non_contract_resource_calendar_intervals(self, date_start=None, date_end=None):
        """
        Return non-contracted intervals with corresponding resource calendar.
        :return: {
                hr.employee(1,): [(date_start1, date_end1, resource.calendar(1,)), (date_start2, date_end2, resource.calendar(2,))],
                hr.employee(2,): [(date_start3, date_end3, resource.calendar(3,)), (date_start4, date_end4, resource.calendar(4,))]
                }
        :rtype: dict
        """
        res = {}
        for r in self:
            res[r] = [(date_start, date_end, r._get_non_contract_resource_calendar())]
        return res

    def _get_resource_calendar_intervals(self, date_start=None, date_end=None):
        """
        Return both contracted and non-contracted intervals with corresponding resource calendar, include the moments of the given date_start and date_end
        :param date_start: datetime | date The returned intervals are expressed in either datetime or date
        :param date_end: datetime | date The returned intervals are expressed in either datetime or date
        :return: {
                hr.employee(1,):{
                                hr.contract(1,): [(date_start1, date_end1, resource.calendar(1,)), (date_start2, date_end2, resource.calendar(2,))],
                                hr.contract(2,): [(date_start3, date_end3, resource.calendar(3,)), (date_start4, date_end4, resource.calendar(4,))]
                                }
                hr.employee(2,):{
                                hr.contract(3,): [(date_start1, date_end1, resource.calendar(1,)), (date_start2, date_end2, resource.calendar(2,))],
                                hr.contract(4,): [(date_start3, date_end3, resource.calendar(3,)), (date_start4, date_end4, resource.calendar(4,))]
                                }
                }
        :rtype: dict
        """

        def _get_calculation_date(given_date, nums):
            if isinstance(given_date, datetime):
                given_date = given_date + relativedelta(microseconds=nums)
            else:
                given_date = given_date + relativedelta(days=nums)
            return given_date
        
        # ensure if either of date_start and date_end is passed, no inconsistent type error will be raised
        today = fields.Date.today()
        now = fields.Datetime.now()
        if not date_start and not date_end:
            date_start = today
            date_end = today
        elif not date_end:
            if isinstance(date_start, datetime):
                date_end = now
            else:
                date_end = today
            # ensure date_start will not later than date_end
            if date_start > date_end:
                date_start = date_end
        elif not date_start:
            if isinstance(date_end, datetime):
                date_start = now
            else:
                date_start = today
            # ensure date_start will not later than date_end
            if date_start > date_end:
                date_start = date_end

        # ensure both date_start and date_end must be in the same type
        if type(date_start) != type(date_end):
            raise ValidationError(_("The given date_start and date_end passed into the method `_get_resource_calendar_intervals(start, end)`"
                                    " must be in the same type. This could be a programming error..."))
            
        if date_start > date_end:
            raise ValidationError(_("The given date_start must be earlier than the given date_end. There could be programming error calling"
                                    " the method `_get_resource_calendar_intervals()` of the model `hr.employee`."))

        all_contracts = self._get_contracts(
            date_start,
            date_end,
            states=['open', 'close'],
            ).sorted(lambda c: (c.date_start, c.date_end or c.trial_date_end or date(9999, 12, 31)))
        res = {}
        for employee in self:
            res[employee] = {}
            contracts = all_contracts.filtered(lambda c: c.employee_id.id == employee.id)

            for contract in contracts:
                res[employee].setdefault(contract, [])
                res[employee][contract] += contract._get_resource_calendar_map(date_start, date_end)[contract]
            
            # if no contract found, fall back to employee's or company's calendar
            if not contracts:
                res[employee].setdefault(False, [])
                res[employee][False] += employee._get_non_contract_resource_calendar_intervals(date_start, date_end)[employee]
                continue
            else:
                # merging contracted and non contacted intervals
                new_res = {False: []}
                new_res.setdefault(False, [])
                last_date_start = date_start
                for contract, intervals in res[employee].items():
                    new_res.setdefault(contract, [])
                    for interval in intervals:
                        if last_date_start < interval[0]:
                            new_res[False] += employee._get_non_contract_resource_calendar_intervals(last_date_start, _get_calculation_date(interval[0], -1))[employee]
                        new_res[contract] += [interval]
                        last_date_start = _get_calculation_date(interval[1], 1)
                if interval[1] < date_end:
                    new_res[False] += employee._get_non_contract_resource_calendar_intervals(_get_calculation_date(interval[1], 1), date_end)[employee]
                if not new_res[False]:
                    del(new_res[False])
                res[employee] = new_res
        return res
    
    def _get_work_intervals(self, date_start, date_end, naive_datetime=False, global_leaves=True, employee_leaves=True, global_attendances_only=False):
        """
        Get effective work intervals of the employee between the given date_start and date_end while respecting time-off.

        :param start: datetime
        :param end: datetime
        :param global_leaves: boolean if False, global leaves will not be taken into account
        :param employee_leaves: boolean if False, employee time-off will not be taken into account
        :param global_attendances_only: indicate if only calendar's global attendance are taken into account. It's useful when we want to know the normal working days/hours

        :return: Return dictionary of employees as keys and tuples of start date and end date and resource.calendar.attendance as values
            {
            'employee1_id': [(date_start1, date_end1, resource.calendar.attendance(1,)), (date_start2, date_end2, resource.calendar.attendance(2,))],
            'employee2_id': [(date_start3, date_end3, resource.calendar.attendance(3,)), (date_start4, date_end4, resource.calendar.attendance(4,))]
            }
        :rtype: dict
        """
        assert isinstance(date_start, datetime) and isinstance(date_end, datetime)

        resource_mapping = {}
        all_resource_calendar_intervals = self._get_resource_calendar_intervals(date_start, date_end)
        for employee in self:
            resource_mapping[employee.id] = []
            for intervals in all_resource_calendar_intervals[employee].values():
                for start_dt, end_dt, res_calendar in intervals:
                    if global_leaves:
                        method = '_work_intervals_batch'
                    else:
                        method = '_attendance_intervals_batch'
                    intervals_batch = sorted(
                        getattr(res_calendar, method)(
                            timezone_datetime(start_dt),
                            timezone_datetime(end_dt),
                            employee.resource_id if employee_leaves else None,
                            domain=[('date_from', '=', False), ('date_to', '=', False)] if global_attendances_only and not global_leaves else None
                        )[employee.resource_id.id if employee_leaves else False],
                        key=lambda x: x[0])
                    if intervals_batch:
                        if naive_datetime:
                            intervals_batch = [
                                        (start.astimezone(utc).replace(tzinfo=None), end.astimezone(utc).replace(tzinfo=None), cal_attendance)
                                        for start, end, cal_attendance in intervals_batch
                                        ]                        
                        resource_mapping[employee.id] += intervals_batch
            if resource_mapping[employee.id]:
                resource_mapping[employee.id] = sorted(resource_mapping[employee.id], key=lambda x: x[0])
        return resource_mapping

    def _get_leave_intervals(self, date_start, date_end):
        """
        Get leave intervals of the employee between the given date_start and date_end.

        :param start: datetime
        :param end: datetime

        :return: Return dictionary of employees as keys and tuples of start date and end date and resource.calendar.leaves records as values
            {
            'employee1_id': [(date_start1, date_end1, resource.calendar.leaves(1,)), (date_start2, date_end2, resource.calendar.leaves(2,3))],
            'employee2_id': [(date_start3, date_end3, resource.calendar.leaves(4,)), (date_start4, date_end4, resource.calendar.leaves(5,))]
            }
        :rtype: dict
        """
        # TODO: remove this method in 15

        # we don't want warning in test mode
        if not getattr(threading.currentThread(), 'testing', False):
            _logger.warning("""The method `_get_leave_intervals(date_start, date_end)`
                was marked as deprecated. Please consider to use the method
                `list_leaves_intervals(date_start, date_end, domain=None, group_by_date=False)` instead""")
        assert isinstance(date_start, datetime) and isinstance(date_end, datetime)
        res = {}
        res_cal_intervals = self._get_resource_calendar_intervals(date_start, date_end)
        for employee, contract_intervals in res_cal_intervals.items():
            res.setdefault(employee.id, [])
            for list_intervals in contract_intervals.values():
                for start, end, res_cal in list_intervals:
                    intervals = res_cal._get_leave_intervals(
                        start.astimezone(timezone(res_cal.tz)),
                        end.astimezone(timezone(res_cal.tz)),
                        employee.resource_id
                        )
                    for tz_aware_start, tz_aware_end, leaves in intervals:
                        res[employee.id].append((
                            tz_aware_start.astimezone(utc).replace(tzinfo=None),
                            tz_aware_end.astimezone(utc).replace(tzinfo=None),
                            leaves
                            ))
        return res

    def list_leaves_intervals(self, date_start, date_end, domain=None, group_by_date=False, naive=False):
        """
        List leave intervals related to the employee in self

        :param domain: domain used in order to recognize the leaves to take,
            None means default value ('time_type', '=', 'leave')
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.
        :param group_by_date: if False, a date could have more than one interval
            (e.g. 8am~12am and 13pm~17pm)
            if True, only one single intervale for a single day
        :param naive: if True, the return datetime will be timzone unaware and considered as UTC

        :return: Returns a dictionary of {
            employee_id: list of tuples (start, stop, hours, resource.calendar.leaves)
            } list of tuples (start, stop, hours, resource.calendar.leaves)
        :rtype: dict
        """
        assert isinstance(date_start, datetime) and isinstance(date_end, datetime)
        res = {}
        res_cal_intervals = self._get_resource_calendar_intervals(date_start, date_end)
        for employee, contract_intervals in res_cal_intervals.items():
            res.setdefault(employee.id, [])
            for list_intervals in contract_intervals.values():
                for dt_from, dt_to, res_cal in list_intervals:
                    # naive datetimes are made explicit in UTC
                    if not dt_from.tzinfo:
                        dt_from = dt_from.replace(tzinfo=utc)
                    if not dt_to.tzinfo:
                        dt_to = dt_to.replace(tzinfo=utc)
                    attendances = res_cal._attendance_intervals_batch(dt_from, dt_to, employee.resource_id)[employee.resource_id.id]
                    leaves = res_cal._leave_intervals_batch(dt_from, dt_to, employee.resource_id, domain)[employee.resource_id.id]
                    result = []
                    for start, stop, leave in (leaves & attendances):
                        if naive:
                            start = start.astimezone(utc).replace(tzinfo=None)
                            stop = stop.astimezone(utc).replace(tzinfo=None)
                        hours = (stop - start).total_seconds() / 3600
                        if not group_by_date:
                            result.append([start, stop, hours, leave])
                        else:
                            if not result:
                                result.append([start, stop, hours, leave])
                            else:
                                result[-1]
                                if result[-1][0].date() == start.date() and result[-1][3] == leave:
                                    result[-1][1] = stop
                                    result[-1][2] += hours
                                else:
                                    result.append([start, stop, hours, leave])
                    res[employee.id] += [tuple(it) for it in result]
        return res
        
