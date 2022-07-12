# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    timesheet_match_ids = fields.One2many('overtime.plan.line.timesheet.match', 'timesheet_id', readonly=True, string='Timesheet Match',
                                           help="Technical field to store matching records which map the current timesheet entry"
                                           " with the related matched overtime plan lines")
    overtime_plan_line_ids = fields.Many2many('hr.overtime.plan.line', 'hr_overtime_plan_line_timesheet_rel', 'timesheet_id', 'overtime_plan_line_id',
                                              string='Overtime Plan Lines', readonly=True,
                                              help="Technical field to store the overtime plan lines that match / cross this timesheet.")
    overtime_plan_ids = fields.Many2many('hr.overtime.plan', 'overtime_plan_hr_timesheet_rel', 'timesheet_id', 'overtime_plan_id',
                                         string='Overtime Plans', readonly=True)

    def _get_fields_to_trigger_timesheet_match_update(self):
        return ['employee_id', 'date_start', 'date_end']

    def _get_related_overtime_plan_lines_domain(self):
        valid_timesheet_entries = self.filtered(lambda l: l.project_id and l.employee_id and l.date_start and l.date_end and not l.holiday_id)
        valid_timesheet_entries = valid_timesheet_entries.sorted('date_start')
        return [
            ('employee_id', 'in', valid_timesheet_entries.with_context(active_test=False).mapped('employee_id').ids),
            ('date_start', '<', valid_timesheet_entries[-1:].date_end),
            ('date_end', '>', valid_timesheet_entries[:1].date_start),
            ]

    def _get_related_overtime_plan_lines(self):
        return self.env['hr.overtime.plan.line'].search(self._get_related_overtime_plan_lines_domain())

    def _match_overtime_plan_lines(self):
        plan_lines = self._get_related_overtime_plan_lines()
        plan_lines._match_timesheet_entries()
        return self.timesheet_match_ids
