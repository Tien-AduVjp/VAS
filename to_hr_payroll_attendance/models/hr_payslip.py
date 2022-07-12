from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    attendance_ids = fields.Many2many('hr.attendance', 'hr_payslip_hr_attendance_rel', 'payslip_id', 'attendance_id',
                                      string='Attendances',
                                      compute='_compute_attendance_ids', compute_sudo=True)
    attendance_count = fields.Integer(string='Attendance Entries Count', compute='_compute_attendance_ids', compute_sudo=True)
    total_attendance_hours = fields.Float(string='Total Attendance Hours', compute='_compute_total_attendance_hours', compute_sudo=True)
    late_attendance_hours = fields.Float(string='Late Coming Hours', compute='_compute_attendance_params', compute_sudo=True)
    early_leave_hours = fields.Float(string='Early Leave Hours', compute='_compute_attendance_params', compute_sudo=True)
    late_attendance_count = fields.Integer(string='Late Comings', compute='_compute_attendance_params', compute_sudo=True)
    early_leave_count = fields.Integer(string='Early Leaves', compute='_compute_attendance_params', compute_sudo=True)
    valid_attendance_hours = fields.Float(string='Valid Attendance Hours', compute='_compute_attendance_params', compute_sudo=True)
    missing_checkout_count = fields.Integer('Missing Check-outs', compute='_compute_attendance_params', compute_sudo=True,
                                            help="Number of attendance entries that have missing checkout or auto-checkout"
                                            " (filled automatically by the software)")

    def _compute_attendance_ids(self):
        for r in self:
            attendance_entries = r.working_month_calendar_ids.attendance_ids
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

    def action_recompute_attendances(self):
        self.working_month_calendar_ids.action_recompute_attendances()

    def action_view_attendance(self):
        result = self.env["ir.actions.act_window"]._for_xml_id('to_hr_payroll_attendance.hr_attendance_action_pivot')
        # override the context to get rid of the default filtering
        result['context'] = {}
        result['domain'] = "[('id', 'in', %s)]" % str(self.attendance_ids.ids)
        return result
