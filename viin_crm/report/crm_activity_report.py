from odoo import fields, models


class CRMActivityReport(models.Model):
    _inherit = 'crm.activity.report'

    referred = fields.Char('Referred By', readonly=True)
    won_status = fields.Selection([
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('pending', 'Pending'),
    ], string='Is Won', readonly=True)
    lost_reason = fields.Many2one('crm.lost.reason', readonly=True)
    days_to_convert = fields.Float('Days To Convert', readonly=True)
    days_exceeding_closing = fields.Float('Exceeded Closing Days', readonly=True)
    
    def _select(self):
        res = super(CRMActivityReport, self)._select()
        res += ', l.referred, l.won_status, l.lost_reason, l.days_to_convert, l.days_exceeding_closing'
        return res
