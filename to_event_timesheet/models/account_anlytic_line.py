from odoo import models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.onchange('date')
    def onchange_date(self):
        res = {}
        event_id = self.env.context.get('event_id')
        if event_id:
            res['domain'] = {'project_id':[('event_id', '=', event_id)]}
        return res
