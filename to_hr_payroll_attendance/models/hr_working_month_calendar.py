from odoo import models, fields, api


class HrWorkingMonthCalendar(models.Model):
    _inherit = 'hr.working.month.calendar'

    attendance_ids = fields.Many2many('hr.attendance', 'working_month_calendar_hr_attendance_rel', 'working_month_calendar_id', 'attendance_id',
                                      string='Attendances',
                                      compute='_compute_attendance_ids', compute_sudo=True)
    attendance_count = fields.Integer(string='Attendance Entries Count', compute='_compute_attendance_ids', compute_sudo=True)
    total_attendance_hours = fields.Float(string='Total Attendance Hours', compute='_compute_total_attendance_hours', compute_sudo=True)
    late_attendance_hours = fields.Float(string='Total Late Coming Hours', compute='_compute_attendance_params', compute_sudo=True)
    early_leave_hours = fields.Float(string='Total Early Leave Hours', compute='_compute_attendance_params', compute_sudo=True)
    late_attendance_count = fields.Integer(string='Late Coming Count', compute='_compute_attendance_params', compute_sudo=True)
    early_leave_count = fields.Integer(string='Early Leave Count', compute='_compute_attendance_params', compute_sudo=True)
    valid_attendance_hours = fields.Float(string='Total Valid Attendance Hours', compute='_compute_attendance_params', compute_sudo=True)
    missing_checkout_count = fields.Integer('Missing Check-out', compute='_compute_attendance_params', compute_sudo=True,
                                            help="Number of attendance entries that have missing checkout or auto-checkout")

    paid_rate = fields.Float(help="The rate which is computed by the following formula:\n"
                             "* If contract is on day rate basis: (Duty Working Days - Unpaid Leave Days) / Working Days in Full Month;\n"
                             "* If contract is on hour rate basis: (Duty Working Hours - Unpaid Leave Hours) / Working Hours in Full Month;\n"
                             "* If contract is on attendance entries and day basis: (Valid Attendance Hours / 8) / Working Days in Full Month;\n"
                             "* If contract is on attendance entries and hours basis: Valid Attendance Hours / Working Hours in Full Month")
    def _compute_attendance_ids(self):
        for r in self:
            attendance_entries = r.line_ids.attendance_ids
            r.attendance_ids = [(6, 0, attendance_entries.ids)]
            r.attendance_count = len(attendance_entries)

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

    def _compute_paid_rate(self):
        super(HrWorkingMonthCalendar, self)._compute_paid_rate()
        for r in self.filtered(lambda l: l.payslip_id.contract_id.salary_attendance_computation_mode == 'attendance'):
            if r.payslip_id.contract_id.salary_computation_mode == 'day_basis':
                if r.month_working_days != 0.0:
                    # TODO: 8 is hard coded as hours per day and will need to find another way to find the correct one
                    r.paid_rate = (r.valid_attendance_hours / 8) / r.month_working_days
            else:
                if r.month_working_hours != 0.0:
                    r.paid_rate = r.valid_attendance_hours / r.month_working_hours

    def action_recompute_attendances(self):
        self.line_ids._compute_attendance_ids()
