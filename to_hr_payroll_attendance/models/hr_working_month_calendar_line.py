import logging
import pytz

from datetime import datetime, time, timedelta

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HrWorkingMonthCalendarLine(models.Model):
    _inherit = 'hr.working.month.calendar.line'

    attendance_ids = fields.Many2many('hr.attendance', 'working_month_calendar_line_hr_attendance_rel', 'working_month_calendar_line_id', 'attendance_id',
                                      string='Attendances',
                                      compute='_compute_attendance_ids', store=True)
    total_attendance_hours = fields.Float(string='Total Attendance Hours', compute='_compute_total_attendance_hours', compute_sudo=True)
    late_attendance_hours = fields.Float(string='Late Coming Hours', compute='_compute_attendance_params', compute_sudo=True)
    early_leave_hours = fields.Float(string='Early Leave Hours', compute='_compute_attendance_params', compute_sudo=True)
    late_attendance_count = fields.Integer(string='Late Coming Count', compute='_compute_attendance_params', compute_sudo=True)
    early_leave_count = fields.Integer(string='Early Leave Count', compute='_compute_attendance_params', compute_sudo=True)
    valid_attendance_hours = fields.Float(string='Valid Attendance Hours', compute='_compute_attendance_params', compute_sudo=True)
    missing_checkout_count = fields.Integer('Missing Check-out', compute='_compute_attendance_params', compute_sudo=True,
                                            help="Number of attendance entries that have missing checkout or auto-checkout")
    paid_rate = fields.Float(help="The rate which is computed by the following formula:\n"
                             "* If contract is on day rate basis: (Duty Working Days - Unpaid Leave Days) / Working Days in Full Month;\n"
                             "* If contract is on hour rate basis: (Duty Working Hours - Unpaid Leave Hours) / Working Hours in Full Month;\n"
                             "* If contract is on attendance entries and day basis: (Valid Attendance Hours / Average Hour per Day) / Working Days in Full Month;\n"
                             "* If contract is on attendance entries and hours basis: Valid Attendance Hours / Working Hours in Full Month")


    @api.depends('working_month_calendar_id',
                 'working_month_calendar_id.payslip_id',
                 'working_month_calendar_id.payslip_id.employee_id',
                 'resource_calendar_id',
                 'date_from', 'date_to')
    def _compute_attendance_ids(self):
        related_attendances = self.env['hr.attendance'].search_read(
            self._prepare_attendance_domain(),
            ['employee_id', 'check_in', 'check_out']
            )
        default_tz = pytz.utc
        for r in self:
            resource_calendar_tz = pytz.timezone(r.resource_calendar_id.tz)
            slip_dt_start = resource_calendar_tz.localize(datetime.combine(r.date_from, time.min)).astimezone(default_tz).replace(tzinfo=None)
            slip_dt_end = resource_calendar_tz.localize(datetime.combine(r.date_to, time.max)).astimezone(default_tz).replace(tzinfo=None)
            employee = r.working_month_calendar_id.payslip_id.employee_id
            attendance_ids = []
            if r.contract_id:
                attendances = filter(
                    lambda att: att['employee_id'][0] == employee.id \
                    and att['check_in'] >= slip_dt_start \
                    and att['check_out'] <= slip_dt_end,
                    related_attendances
                    )
                for attendance in attendances:
                    attendance_ids.append(attendance['id'])
            r.attendance_ids = [(6, 0, attendance_ids)]

    def _compute_total_attendance_hours(self):
        for r in self:
            r.total_attendance_hours = sum(r.attendance_ids.mapped('worked_hours'))

    def _compute_attendance_params(self):
        for r in self:
            late_attendance_count = 0
            late_attendance_hours = 0.0
            early_leave_count = 0
            early_leave_hours = 0.0
            valid_attendance_hours = 0.0
            missing_checkout_count = 0
            for attendance in r.attendance_ids:
                if attendance.late_attendance_hours > 0.0:
                    late_attendance_count += 1
                if attendance.early_leave_hours > 0.0:
                    early_leave_count += 1
                if not attendance.check_out or attendance.auto_checkout:
                    missing_checkout_count += 1
                late_attendance_hours += attendance.late_attendance_hours
                early_leave_hours += attendance.early_leave_hours
                valid_attendance_hours += attendance.valid_worked_hours
            r.late_attendance_count = late_attendance_count
            r.late_attendance_hours = late_attendance_hours
            r.early_leave_count = early_leave_count
            r.early_leave_hours = early_leave_hours
            r.valid_attendance_hours = valid_attendance_hours
            r.missing_checkout_count = missing_checkout_count

    def _compute_worked_days_hours(self):
        super(HrWorkingMonthCalendarLine, self)._compute_worked_days_hours()
        for r in self.filtered(lambda l: l.contract_id.salary_attendance_computation_mode == 'attendance'):
            r.worked_days = r.valid_attendance_hours / r.resource_calendar_id.hours_per_day
            r.worked_hours = r.valid_attendance_hours

    def _compute_paid_rate(self):
        super(HrWorkingMonthCalendarLine, self)._compute_paid_rate()
        for r in self.filtered(lambda l: l.contract_id.salary_attendance_computation_mode == 'attendance'):
            if r.salary_computation_mode == 'day_basis':
                if r.calendar_working_days != 0.0 and r.duty_working_days != 0.0:
                    r.paid_rate = (r.valid_attendance_hours / r.resource_calendar_id.hours_per_day) / r.working_month_calendar_id.month_working_days
            else:
                if r.calendar_working_hours != 0.0 and r.duty_working_hours != 0.0:
                    r.paid_rate = r.valid_attendance_hours / r.working_month_calendar_id.month_working_hours

    def _prepare_attendance_domain(self):
        self = self.sorted('date_from')
        return [
            ('employee_id', 'in', self.with_context(active_test=False).mapped('working_month_calendar_id.payslip_id.employee_id').ids),
            ('check_in', '>=', datetime.combine(self[:1].date_from, time.min) + timedelta(days=-1)),
            ('check_out', '<=', datetime.combine(self[-1:].date_to, time.max) + timedelta(days=1)),
            ]
