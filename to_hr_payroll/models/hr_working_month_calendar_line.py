import logging

from pytz import timezone, UTC
from datetime import datetime
from datetime import time as datetime_time

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrWorkingMonthCalendarLine(models.Model):
    _name = 'hr.working.month.calendar.line'
    _description = "Working Month Calendar Line"
    _order = 'date_from'

    working_month_calendar_id = fields.Many2one('hr.working.month.calendar', string='Working Month Calendar',
                                                auto_join=True, required=True, ondelete='cascade', readonly=True)
    payslip_id = fields.Many2one(related='working_month_calendar_id.payslip_id', compute_sudo=True)
    employee_id = fields.Many2one(related='working_month_calendar_id.payslip_id.employee_id', compute_sudo=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', readonly=True)
    salary_computation_mode = fields.Selection([
        ('hour_basis', 'Hour Basis'),
        ('day_basis', 'Day Basis')
        ], compute='_compute_salary_computation_mode', store=True)
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)

    calendar_working_hours = fields.Float(string='Calendar Working Hours', compute='_compute_calendar_working_hours', store=True,
                                          help="Total working days (excl. global leaves) according to the corresponding resource calendar"
                                          " and the Date From and Date To.")
    calendar_working_days = fields.Float(string='Calendar Working Days', compute='_compute_calendar_working_days', store=True,
                                         help="Total working hours (excl. global leaves) according to the corresponding resource calendar"
                                         " and the Date From and Date To.")

    duty_working_hours = fields.Float(string='Duty Working Hours', compute='_compute_duty_working_hours', store=True,
                                           help="The working hours that the employee of the payslip has to work that takes payslip dates into account.")
    duty_working_days = fields.Float(string='Duty Working Days', compute='_compute_duty_working_days', store=True,
                                          help="The working days that the employee of the payslip has to work that takes payslip dates into account.")
    leave_ids = fields.One2many('payslip.leave.interval', 'working_month_calendar_line_id', string='Time Off', compute='_compute_leaves', store=True)
    leave_days = fields.Float(string='Total Leave Days', compute='_compute_leave_days_hours',
                              help="Total leave days excluding global leaves")
    leave_hours = fields.Float(string='Total Leave Hours', compute='_compute_leave_days_hours',
                               help="Total leave hours excluding global leaves")
    unpaid_leave_days = fields.Float(string='Unpaid Leave Days', compute='_compute_unpaid_leave_days_hours')
    unpaid_leave_hours = fields.Float(string='Unpaid Leave Hours', compute='_compute_unpaid_leave_days_hours')
    worked_days = fields.Float(string='Worked Days', compute='_compute_worked_days_hours')
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_days_hours')
    paid_rate = fields.Float(string='Paid Rate', compute='_compute_paid_rate',
                             compute_sudo=True,
                             help="The rate which is computed by the following formula:\n"
                             "* If contract is on day rate basis: (Duty Working Days - Unpaid Leave Days) / Working Days in Full Month;\n"
                             "* If contract is on hour rate basis: (Duty Working Hours - Unpaid Leave Hours) / Working Hours in Full Month")

    def _get_resource_calendar(self):
        return self.resource_calendar_id or self.contract_id.resource_calendar_id

    def _get_duty_date_from_and_date_to(self):
        # pick payslip's date_from if it is greater than the line's date from
        # for example, Payslip's date_from is Jun 10 and Line's date_from is Jun 1, Jun 10 will be picked.
        if not self.contract_id:
            return None, None

        if self.working_month_calendar_id.payslip_id.date_from and self.working_month_calendar_id.payslip_id.date_from > self.date_from:
            date_from = self.working_month_calendar_id.payslip_id.date_from
        else:
            date_from = self.date_from

        # pick line's date_to if it is earlier than the payslip's date_to
        if self.working_month_calendar_id.payslip_id.date_to and self.working_month_calendar_id.payslip_id.date_to > self.date_to:
            date_to = self.date_to
        else:
            date_to = self.working_month_calendar_id.payslip_id.date_to or self.date_to

        # if dates out of contract period
        if date_to < self.contract_id.date_start or (self.contract_id.date_end and date_from > self.contract_id.date_end):
            return None, None

        date_from, date_to = self.contract_id._qualify_interval(date_from, date_to)
        # convert date to datetime
        date_from = datetime.combine(date_from, datetime_time.min)
        date_to = datetime.combine(date_to, datetime_time.max)

        return date_from, date_to

    def _get_calendar_date_from_and_date_to(self):
        date_from = datetime.combine(self.date_from, datetime_time.min)
        date_to = datetime.combine(self.date_to, datetime_time.max)
        return date_from, date_to

    def _prepare_payslip_leave_interval_vals(self, date, hours, leave, tz=None):
        tz = tz or timezone(leave.calendar_id.tz)
        resource_calendar = self._get_resource_calendar()
        work_hours = resource_calendar.get_work_hours_count(
            tz.localize(datetime.combine(date, datetime_time.min)),
            tz.localize(datetime.combine(date, datetime_time.max)),
            compute_leaves=True,  # take global leaves into account
        )
        days = hours / work_hours if work_hours else 0.0
        return {
            'working_month_calendar_line_id': self.id,
            'leave_id': leave.id,
            'holiday_id': leave.holiday_id.id,
            'holiday_status_id': leave.holiday_id.holiday_status_id.id,
            'unpaid': leave.holiday_id.holiday_status_id.unpaid,
            'date': date,
            'hours': hours,
            'days': days,
        }

    @api.depends('working_month_calendar_id.payslip_id.date_from', 'working_month_calendar_id.payslip_id.date_to',
                 'contract_id', 'resource_calendar_id', 'date_from', 'date_to')
    def _compute_duty_working_hours(self):
        for r in self:
            date_from, date_to = r._get_duty_date_from_and_date_to()
            resource_calendar = r._get_resource_calendar()
            if resource_calendar and date_from and date_to:
                duty_working_hours = resource_calendar.get_work_hours_count(date_from, date_to, compute_leaves=True)
                r.duty_working_hours = duty_working_hours
            else:
                r.duty_working_hours = 0.0

    @api.depends('working_month_calendar_id.payslip_id.date_from', 'working_month_calendar_id.payslip_id.date_to',
                 'contract_id', 'resource_calendar_id', 'date_from', 'date_to')
    def _compute_duty_working_days(self):
        for r in self:
            date_from, date_to = r._get_duty_date_from_and_date_to()
            resource_calendar = r._get_resource_calendar()
            if resource_calendar and date_from and date_to:
                duty_data = resource_calendar.get_work_duration_data(date_from, date_to, compute_leaves=True, domain=None)
                r.duty_working_days = duty_data['days']
            else:
                r.duty_working_days = 0.0

    @api.depends('contract_id', 'resource_calendar_id', 'date_from', 'date_to')
    def _compute_calendar_working_hours(self):
        for r in self:
            date_from, date_to = r._get_calendar_date_from_and_date_to()
            resource_calendar = r._get_resource_calendar()
            if resource_calendar and date_from and date_to:
                r.calendar_working_hours = resource_calendar.get_work_hours_count(date_from, date_to, compute_leaves=True)
            else:
                r.calendar_working_hours = 0.0

    @api.depends('contract_id', 'resource_calendar_id', 'date_from', 'date_to')
    def _compute_calendar_working_days(self):
        for r in self:
            date_from, date_to = r._get_calendar_date_from_and_date_to()
            resource_calendar = r._get_resource_calendar()
            if resource_calendar and date_from and date_to:
                calendar_data = resource_calendar.get_work_duration_data(date_from, date_to, compute_leaves=True, domain=None)
                r.calendar_working_days = calendar_data['days']
            else:
                r.calendar_working_days = 0.0

    @api.depends('contract_id', 'resource_calendar_id', 'date_from', 'date_to', 'working_month_calendar_id.payslip_id.employee_id')
    def _compute_leaves(self):
        convert_utc_to_local = self.env['to.base'].convert_utc_time_to_tz
        for r in self:
            cmd = [(3, leave.id) for leave in r.leave_ids]
            resource_calendar = r._get_resource_calendar()
            if r.date_from and r.date_to and resource_calendar and r.working_month_calendar_id:
                date_from, date_to = r._get_duty_date_from_and_date_to()
                if date_from and date_to:
                    intervals = resource_calendar._get_leave_intervals(
                        date_from.replace(tzinfo=UTC),
                        date_to.replace(tzinfo=UTC),
                        domain=[],
                        resource=r.working_month_calendar_id.payslip_id.employee_id.resource_id,
                        )
                    date_to_date = date_to.date()
                    date_from_date = date_from.date()
                    for start, end, rs_leaves in intervals:
                        # Process leaves in 1 day or many days (by payslip period)
                        for rs_leave in rs_leaves:
                            new_date_from = convert_utc_to_local(rs_leave.date_from, rs_leave.calendar_id.tz)
                            new_date_to = convert_utc_to_local(rs_leave.date_to, rs_leave.calendar_id.tz)
                            new_start = start if start > new_date_from else new_date_from
                            new_end = end if end < new_date_to else new_date_to
                            leave_intervals = r.working_month_calendar_id.payslip_id.employee_id.list_leaves(
                                new_start,
                                new_end,
                                calendar=rs_leave.calendar_id,
                                domain=[]
                            )
                            for leave_date, leave_hours, minor_leave in leave_intervals:
                                # ignore leave time outside the date_from and date_to
                                if leave_date < date_from_date or leave_date > date_to_date:
                                    continue
                                vals = r._prepare_payslip_leave_interval_vals(leave_date, leave_hours, minor_leave)
                                cmd.append((0, 0, vals))
            r.leave_ids = cmd

    @api.depends('contract_id', 'working_month_calendar_id.payslip_id.contract_id')
    def _compute_salary_computation_mode(self):
        for r in self:
            contract = r.contract_id or r.working_month_calendar_id.payslip_id.contract_id
            r.salary_computation_mode = contract.salary_computation_mode

    def _compute_paid_rate(self):
        for r in self:
            if r.salary_computation_mode == 'day_basis':
                if r.calendar_working_days == 0.0 or r.duty_working_days == 0.0:
                    r.paid_rate = 0.0
                else:
                    r.paid_rate = (r.duty_working_days - r.unpaid_leave_days) / r.working_month_calendar_id.month_working_days
            else:
                if r.calendar_working_hours == 0.0 or r.duty_working_hours == 0.0:
                    r.paid_rate = 0.0
                else:
                    r.paid_rate = (r.duty_working_hours - r.unpaid_leave_hours) / r.working_month_calendar_id.month_working_hours

    @api.depends('leave_ids', 'leave_ids.days', 'leave_ids.hours')
    def _compute_leave_days_hours(self):
        self.flush()
        all_ps_leave_intervals = self.env['payslip.leave.interval'].search_read(
            [('working_month_calendar_line_id', 'in', self.ids),
             ('leave_id.time_type', '=', 'leave')],
            ['working_month_calendar_line_id', 'days', 'hours']
            )
        for r in self:
            ps_leave_intervals = filter(
                lambda l: l['working_month_calendar_line_id'][0] == r.id,
                all_ps_leave_intervals
                )
            # cast iterator to list so that we can use it more than once
            ps_leave_intervals = list(ps_leave_intervals)
            r.leave_days = sum([leave_interval['days'] for leave_interval in ps_leave_intervals])
            r.leave_hours = sum([leave_interval['hours'] for leave_interval in ps_leave_intervals])

    @api.depends('leave_ids.holiday_status_id', 'leave_ids.days', 'leave_ids.hours')
    def _compute_unpaid_leave_days_hours(self):
        self.flush()
        all_ps_leave_intervals = self.env['payslip.leave.interval'].search_read(
            [('working_month_calendar_line_id', 'in', self.ids),
             ('leave_id.time_type', '=', 'leave'),
             ('unpaid', '=', True)],
            ['working_month_calendar_line_id', 'days', 'hours']
            )
        for r in self:
            ps_leave_intervals = filter(
                lambda l: l['working_month_calendar_line_id'][0] == r.id,
                all_ps_leave_intervals
                )
            # cast iterator to list so that we can use it more than once
            ps_leave_intervals = list(ps_leave_intervals)
            r.unpaid_leave_days = sum([leave_interval['days'] for leave_interval in ps_leave_intervals])
            r.unpaid_leave_hours = sum([leave_interval['hours'] for leave_interval in ps_leave_intervals])

    def _compute_worked_days_hours(self):
        for r in self:
            r.worked_days = r.duty_working_days - r.leave_days
            r.worked_hours = r.duty_working_hours - r.leave_hours

    @api.constrains('contract_id', 'date_from', 'date_to')
    def _check_contract(self):
        for r in self:
            if r.contract_id and r.date_from and r.date_to:
                if r.date_to < r.contract_id.date_start or (r.contract_id.date_end and r.date_from > r.contract_id.date_end):
                    msg = _("The contract '%s' that was assigned to the Working Month Calendar Line '%s' of the payslip '%s'"
                            " does not match the line period. This is usually caused by discrepancy"
                            " between the payslip dates and the contract dates.") % (
                                r.contract_id.display_name,
                                r.payslip_id.display_name,
                                r.display_name
                                )
                    if r._context.get('post_contract_discrepancy_error', False):
                        r.payslip_id.message_post(body=msg)
                        if r._context.get('log_contract_discrepancy_error', False):
                            _logger.error(msg)
                    else:
                        raise ValidationError(msg)
