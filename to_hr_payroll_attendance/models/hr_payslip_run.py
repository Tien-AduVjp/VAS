from odoo import fields, models, api


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    attendance_ids = fields.Many2many('hr.attendance', 'hr_payslip_run_hr_attendance_rel', 'payslip_batch_id', 'attendance_id',
                                      string='Attendances',
                                      compute='_compute_attendance_ids', compute_sudo=True)
    attendance_count = fields.Integer(string='Attendance Entries Count', compute='_compute_attendance_ids', compute_sudo=True)

    def _compute_attendance_ids(self):
        for r in self:
            attendance_entries = r.slip_ids.attendance_ids
            r.attendance_ids = [(6, 0, attendance_entries.ids)]
            r.attendance_count = len(attendance_entries)

    def action_view_attendance(self):
        result = self.env["ir.actions.act_window"]._for_xml_id('to_hr_payroll_attendance.hr_attendance_action_pivot')

        # override the context to get rid of the default filtering
        result['context'] = {}
        result['domain'] = "[('id', 'in', %s)]" % str(self.attendance_ids.ids)
        return result
