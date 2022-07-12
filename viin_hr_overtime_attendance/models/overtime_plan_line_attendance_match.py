from odoo import models, fields, api


class OvertimePlanLineAttendanceMatch(models.Model):
    _name = 'overtime.plan.line.attendance.match'
    _inherit = 'abstract.overtime.plan.line.match'
    _description = 'Overtime Plan Line Attendance Match'

    attendance_id = fields.Many2one('hr.attendance', string='Attendance Log', readonly=True, required=True, ondelete='cascade')

    @api.depends('date_start', 'date_end', 'attendance_id.check_in', 'attendance_id.check_out')
    def _compute_unmatched_hours(self):
        for r in self:
            unmatched = 0.0
            if r.attendance_id.check_in < r.date_start:
                unmatched += (r.date_start - r.attendance_id.check_in).total_seconds() / 3600
            if r.attendance_id.check_out and r.attendance_id.check_out > r.date_end:
                unmatched += (r.attendance_id.check_out - r.date_end).total_seconds() / 3600
            r.unmatched_hours = unmatched
