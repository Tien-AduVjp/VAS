# -*- coding: utf-8 -*-
from pytz import utc
from datetime import datetime, time
from itertools import chain

from odoo import models, fields, _
from odoo.exceptions import ValidationError

from odoo.addons.resource.models.resource_mixin import timezone_datetime


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    def _get_resource_calendar(self):
        self.ensure_one()
        return self.resource_calendar_id or self.employee_id.resource_calendar_id or self.company_id.resource_calendar_id
    
    def _get_resource_calendar_map(self, start=None, end=None):
        """
        get the right resource calendars applicable to the given start and end dates
        :return: dictionary of contract and calendar map in the format of
            {
                'hr.contract(1,)': [(start1, end1, resource_calendar1), (start2, end2, resource_calendar2)],
                'hr.contract(2,)': [(start3, end3, resource_calendar3), (start4, end4, resource_calendar4)],
                }
        :rtype: dict
        """
        today = fields.Date.today()
        start = start or today
        end = end or today
        calendar_map = {}
        for r in self:
            calendar_map[r] = r._get_resource_calendar_intervals(start, end)
        return calendar_map
    
    def _get_resource_calendar_intervals(self, start=None, end=None):
        """
        Hooking method for others to provide mean to get an appropriate resource calendar based on the given dates
        By default, this return the calendar specified on the contract

        :return: list of tuple of (start, end, resource_calendar). E.g. [(start1, end1, resource_calendar1), (start2, end2, resource_calendar2), ...]
        :rtype: list
        """
        self.ensure_one()
        today = fields.Date.today()
        start = start or today
        end = end or today
        qualified_start, qualified_end = self._qualify_interval(start, end)
        return [(qualified_start, qualified_end, self._get_resource_calendar())]

    def _qualify_interval(self, start, end):
        """
        Modify the given start and end to ensure that the start will not be earlier than the
        contract's start date and the date_to will not be later than the contract's end date
        
        :param start_dt: datetime | date
        :param end_dt: datetime | date

        :return: tuple of start_date and end_date in datetime or date (depending on the
            type of the given start and end) that match the contract
        :rtype: tuple
        
        :raise ValidationError: if The given start and end are not in the same type
        """

        def _get_applicable_date(contract, given_date):
            if isinstance(given_date, datetime):
                contract_date_start = datetime.combine(contract.date_start, time.min)
                contract_date_end = datetime.combine(contract.date_end, time.max) if contract.date_end else False
            else:
                contract_date_start = contract.date_start
                contract_date_end = contract.date_end

            if given_date < contract_date_start:
                given_date = contract_date_start
            if contract_date_end and given_date > contract_date_end:
                given_date = contract_date_end
            return given_date

        if not self:
            return start, end

        if type(start) != type(end):
            raise ValidationError(_("The given start and end passed into the method `_qualify_interval(start, end)`"
                                    " must be in the same type. This could be a programming error..."))

        self = self.sorted('date_start')
        start = _get_applicable_date(self[0], start)
        end = _get_applicable_date(self[-1], end)
        if end < start:
            end = start
        return start, end

    def _get_unavailable_intervals(self, start, end, naive_datetime=False):
        """
        Compute the intervals during which employee of the contract is unavailable with hour granularity between start and end
        :start: datetime naive datetime in UTC
        :end: datetime naive datetime in UTC
        :return: dict: {
            hr.contract(id,): {
                resource.calendar(id,): [(datetime.datetime(2021, 7, 19, 11, 0), datetime.datetime(2021, 7, 19, 15, 48, 59, 999999))],
                }
            }
        """
        if not isinstance(start, datetime):
            raise ValidationError(_("The given start must be `datetime` type but got `%s` (%s)") % (type(start).__name__, start))
        if not isinstance(end, datetime):
            raise ValidationError(_("The given end must be `datetime` type but got `%s` (%s)") % (type(end).__name__, end))
        res = {}
        resource_calendar_map = self._get_resource_calendar_map(start, end)
        for contract, calendar_map in resource_calendar_map.items():
            res.setdefault(contract, {})
            for start_dt, end_dt, res_calendar in calendar_map:
                res[contract].setdefault(res_calendar, [])
                if not start_dt or not end_dt:
                    continue
                start_datetime = timezone_datetime(start_dt)
                end_datetime = timezone_datetime(end_dt)
                
                resource_work_intervals = res_calendar._work_intervals_batch(start_datetime, end_datetime)[False]
                resource_work_intervals = [(start, stop) for start, stop, meta in resource_work_intervals]
                # start + flatten(intervals) + end
                resource_work_intervals = [start_datetime] + list(chain.from_iterable(resource_work_intervals)) + [end_datetime]
                # put it back to UTC
                resource_work_intervals = list(map(lambda dt: dt.astimezone(utc), resource_work_intervals))
                # pick groups of two
                resource_work_intervals = list(zip(resource_work_intervals[0::2], resource_work_intervals[1::2]))
                # remove intervals that have same start and end and convert to naive datetime if required
                if naive_datetime:
                    resource_work_intervals = [
                        (interval[0].replace(tzinfo=None), interval[1].replace(tzinfo=None)) 
                        for interval in resource_work_intervals if interval[0] != interval[1]
                        ]
                else:
                    resource_work_intervals = [interval for interval in resource_work_intervals if interval[0] != interval[1]]
                res[contract][res_calendar] += resource_work_intervals

        return res
