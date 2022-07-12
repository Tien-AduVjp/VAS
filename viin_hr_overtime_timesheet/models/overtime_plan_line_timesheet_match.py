from odoo import models, fields, api


class OvertimePlanLineTimesheetMatch(models.Model):
    _name = 'overtime.plan.line.timesheet.match'
    _inherit = 'abstract.overtime.plan.line.match'
    _description = 'Overtime Plan Line Timesheet Match'

    timesheet_id = fields.Many2one('account.analytic.line', string='Timesheet Entry', readonly=True, required=True, ondelete='cascade')

    @api.depends('date_start', 'date_end', 'timesheet_id.date_start', 'timesheet_id.date_end')
    def _compute_unmatched_hours(self):
        for r in self:
            unmatched = 0.0
            if r.timesheet_id.date_start < r.date_start:
                unmatched += (r.date_start - r.timesheet_id.date_start).total_seconds() / 3600
            if r.timesheet_id.date_end and r.timesheet_id.date_end > r.date_end:
                unmatched += (r.timesheet_id.date_end - r.date_end).total_seconds() / 3600
            r.unmatched_hours = unmatched
