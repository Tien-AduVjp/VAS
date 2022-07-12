from odoo import models, fields, api


class AbstractOvertimePlanLineMatch(models.AbstractModel):
    _name = 'abstract.overtime.plan.line.match'
    _description = "Abstract Overtime Plan Line Match"
    _order = 'date_start DESC, date_end DESC, id DESC'

    overtime_plan_line_id = fields.Many2one('hr.overtime.plan.line', string='Overtime Plan Line',
                                                      readonly=True, required=True, ondelete='cascade')
    overtime_plan_id = fields.Many2one('hr.overtime.plan', string='Overtime Plan',
                                                      readonly=True, required=True, ondelete='cascade')
    date_start = fields.Datetime(string='Start Date', readonly=True, required=True)
    date_end = fields.Datetime(string='End Date', readonly=True, required=True)
    matched_hours = fields.Float(string='Match Hours', compute='_compute_matched_hours', store=True,
                                 help="Actual worked hours that match the planned.")
    unmatched_hours = fields.Float(string='Unmatched Hours', compute='_compute_unmatched_hours', store=True,
                                   help="Actual worked hours that did NOT match the planned.")

    @api.depends('date_start', 'date_end')
    def _compute_matched_hours(self):
        for r in self:
            diff = r.date_end - r.date_start
            r.matched_hours = diff.total_seconds() / 3600
    
    def _compute_unmatched_hours(self):
        """
        Hooking method for inheritance to implement
        """
        pass

    def _get_matched_interval(self, start, end):

        def _get_qualified_date(record, given_datetime):
            if given_datetime <= record.date_start:
                given_datetime = record.date_start
            elif given_datetime >= record.date_end:
                given_datetime = record.date_end
            return given_datetime

        if not self:
            return start, end

        self = self.sorted('date_start')
        start = _get_qualified_date(self[0], start)
        end = _get_qualified_date(self[-1], end)
        if end < start:
            end = start
        return start, end
