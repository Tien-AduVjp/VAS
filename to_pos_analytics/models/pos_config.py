from odoo import fields, models, api


class PosConfig(models.Model):
    _inherit = 'pos.config'

    analytics_account_id = fields.Many2one('account.analytic.account', string='Analytics Account')
    auto_create_analytics_account = fields.Boolean(string='Create Analytics Account', default=True,
                                                   help="Check this and leave the field Analytics Account empty to get a new Analytics Account"
                                                   " created for this PoS.")

    @api.model
    def create(self, vals):
        res = super(PosConfig, self).create(vals)
        if res.auto_create_analytics_account and not res.analytics_account_id:
            analytics_account_id = self.env['account.analytic.account'].create({'name': res.name})
            res.write({'analytics_account_id': analytics_account_id.id})
        return res

