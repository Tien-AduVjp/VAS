from odoo import models, fields, api


class HrOvertimePlan(models.Model):
    _inherit = 'hr.overtime.plan'

    recognition_mode = fields.Selection(selection_add=[('attendance', 'Attendance')], ondelete={'attendance': lambda self:self.reason_id.recognition_mode})
    attendance_match_ids = fields.One2many('overtime.plan.line.attendance.match', 'overtime_plan_id', readonly=True)
    attendance_ids = fields.Many2many('hr.attendance', 'overtime_plan_hr_attendance_rel', 'overtime_plan_id', 'attendance_id',
                                      string='Related Attendances', compute='_compute_attendance_ids', store=True)
    matched_attendance_hours = fields.Float(string='Matched Attendance Hours', compute='_compute_matched_attendance_hours', store=True)

    @api.depends('line_ids.matched_attendance_hours')
    def _compute_matched_attendance_hours(self):
        for r in self:
            r.matched_attendance_hours = sum(r.line_ids.mapped('matched_attendance_hours'))

    @api.depends('attendance_match_ids.overtime_plan_id')
    def _compute_attendance_ids(self):
        for r in self:
            r.attendance_ids = [(6, 0, r.attendance_match_ids.mapped('attendance_id').ids)]

    def _match_attendances(self):
        self.line_ids._match_attendances()

    def action_match_attendances(self):
        self._match_attendances()

    def _recognize_actual_overtime(self):
        super(HrOvertimePlan, self)._recognize_actual_overtime()
        self._match_attendances()
