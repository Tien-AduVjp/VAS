from odoo import models, fields, api


class HrOvertimePlanLine(models.Model):
    _inherit = 'hr.overtime.plan.line'
    
    recognition_mode = fields.Selection(selection_add=[('attendance', 'Attendance')])
    attendance_ids = fields.Many2many('hr.attendance', 'hr_overtime_plan_line_hr_attendance_rel', 'overtime_plan_line_id', 'attendance_id',
                                      string='Related Attendance', readonly=True)
    attendance_match_ids = fields.One2many('overtime.plan.line.attendance.match', 'overtime_plan_line_id',
                                           string='Attendance Match', compute='_compute_attendance_match_ids', store=True)
    matched_attendance_hours = fields.Float(string='Matched Attendance Hours', compute='_compute_matched_attendance_hours', store=True)
    unmatched_attendance_hours = fields.Float(string='Unmatched Attendance Hours', compute='_compute_unmatched_attendance_hours', store=True)

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        records = super(HrOvertimePlanLine, self).create(vals_list)
        records._match_attendances()
        return records

    def write(self, vals):
        res = super(HrOvertimePlanLine, self).write(vals)
        if any(f in vals for f in self._get_fields_to_trigger_attendance_match_update()):
            self._match_attendances()
        return res

    def _get_fields_to_trigger_attendance_match_update(self):
        return ['employee_id', 'date_start', 'date_end']

    @api.depends('attendance_ids', 'attendance_ids.check_in', 'attendance_ids.check_out')
    def _compute_attendance_match_ids(self):
        for r in self:
            cmd = [(3, line.id) for line in r.attendance_match_ids]
            vals_list = r._prepare_attendance_match_vals_list()
            cmd += [(0, 0, vals) for vals in vals_list]
            r.attendance_match_ids = cmd

    @api.depends('attendance_match_ids.matched_hours')
    def _compute_matched_attendance_hours(self):
        for r in self:
            r.matched_attendance_hours = sum(r.attendance_match_ids.mapped('matched_hours'))

    @api.depends('attendance_match_ids.unmatched_hours')
    def _compute_unmatched_attendance_hours(self):
        for r in self:
            r.unmatched_attendance_hours = sum(r.attendance_match_ids.mapped('unmatched_hours'))

    @api.depends('matched_attendance_hours')
    def _compute_actual_hours(self):
        super(HrOvertimePlanLine, self)._compute_actual_hours()
        for r in self:
            if r.recognition_mode == 'attendance':
                r.actual_hours = r.matched_attendance_hours

    def _match_attendances(self):
        related_attendances = self._get_related_hr_attendance()
        for r in self:
            matched_attendance = related_attendances.filtered(
                lambda att: att.employee_id == r.employee_id \
                and att.check_in < r.date_end \
                and att.check_out > r.date_start
                )
            r.attendance_ids = [(6, 0, matched_attendance.ids)]

    def _get_related_hr_attendance(self):
        return self.env['hr.attendance'].search(self._get_related_hr_attendance_domain())

    def _get_related_hr_attendance_domain(self):
        sorted_lines = self.sorted('date_start')
        return [
            ('employee_id', 'in', sorted_lines.with_context(active_test=False).mapped('employee_id').ids),
            ('check_in', '<', sorted_lines[-1:].date_end),
            ('check_out', '>', sorted_lines[:1].date_start)
            ]
    
    def action_match_attendances(self):
        self._match_attendances()

    def _prepare_attendance_match_vals_list(self):
        vals_list = []
        for r in self:
            for attendance in r.attendance_ids:
                date_start, date_end = r._get_match_intervals(attendance.check_in, attendance.check_out)
                if not date_start or not date_end:
                    continue
                vals_list.append({
                    'attendance_id': attendance.id,
                    'overtime_plan_line_id': r.id,
                    'overtime_plan_id': r.overtime_plan_id.id,
                    'date_start': date_start,
                    'date_end': date_end
                    })
        return vals_list
        
