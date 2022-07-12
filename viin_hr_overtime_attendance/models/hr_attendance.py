# -*- coding: utf-8 -*-

from odoo import models, fields


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    attendance_match_ids = fields.One2many('overtime.plan.line.attendance.match', 'attendance_id', readonly=True,
                                           help="Technical field to store matching records which map the current attendance record"
                                           " with the related matched overtime plan lines")
    overtime_plan_line_ids = fields.Many2many('hr.overtime.plan.line', 'hr_overtime_plan_line_hr_attendance_rel', 'attendance_id', 'overtime_plan_line_id',
                                              string='Overtime Plan Lines', readonly=True,
                                              help="Technical field to store the overtime plan lines that match / cross this attendance.")
    overtime_plan_ids = fields.Many2many('hr.overtime.plan', 'overtime_plan_hr_attendance_rel', 'attendance_id', 'overtime_plan_id',
                                         string='Overtime Plans', readonly=True)

    def _get_fields_to_trigger_attendance_match_update(self):
        return ['employee_id', 'check_in', 'check_out']

    def _get_related_overtime_plan_lines_domain(self):
        sorted_attendances = self.sorted('check_in')
        return [
            ('employee_id', 'in', sorted_attendances.with_context(active_test=False).mapped('employee_id').ids),
            ('date_start', '<', sorted_attendances[-1:].check_out),
            ('date_end', '>', sorted_attendances[:1].check_in),
            ]

    def _get_related_overtime_plan_lines(self):
        return self.env['hr.overtime.plan.line'].search(self._get_related_overtime_plan_lines_domain())

    def _match_overtime_plan_lines(self):
        plan_lines = self._get_related_overtime_plan_lines()
        plan_lines._match_attendances()
        return self.attendance_match_ids
