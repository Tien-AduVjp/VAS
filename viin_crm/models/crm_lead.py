from datetime import datetime, time

from odoo import api, fields, models

DAYS = 24 * 60 * 60


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    days_exceeding_closing = fields.Float(string='Exceeded Closing Days', compute='_compute_days_exceeding_closing', store=True)
    days_to_convert = fields.Float(string='Days To Convert', compute='_compute_days_to_convert', store=True)
    won_status = fields.Selection([
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('pending', 'Pending'),
    ], string='Is Won', compute='_compute_won_status', store=True)

    @api.depends('date_deadline', 'date_closed')
    def _compute_days_exceeding_closing(self):
        for r in self:
            r.days_exceeding_closing = 0
            if r.date_deadline and r.date_closed:
                delta = datetime.combine(r.date_deadline, time.min) - r.date_closed
                r.days_exceeding_closing = delta.total_seconds() / DAYS

    @api.depends('date_conversion', 'create_date')
    def _compute_days_to_convert(self):
        for r in self:
            r.days_to_convert = 0
            if r.date_conversion:
                delta = r.date_conversion - r.create_date
                r.days_to_convert = delta.total_seconds() / DAYS

    @api.depends('active', 'probability')
    def _compute_won_status(self):
        for r in self:
            r.won_status = 'pending'
            if r.active and r.stage_id.is_won:
                r.won_status = 'won'
            elif not r.active and r.probability == 0:
                r.won_status = 'lost'

    @api.model
    def _get_cohort_data(self, start_date, stop_date, measure, interval, domain, mode, timeline):
        """
        Override to include lost leads into the analysis
        """
        return super(CRMLead, self.with_context(active_test=False))._get_cohort_data(
            start_date=start_date,
            stop_date=stop_date,
            measure=measure,
            interval=interval,
            domain=domain,
            mode=mode,
            timeline=timeline
            )
