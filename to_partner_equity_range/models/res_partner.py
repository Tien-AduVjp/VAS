from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    equity_range_id = fields.Many2one('res.partner.equity.range',
                                      string="Equity Range", ondelete='restrict',
                                      tracking=True, compute="_compute_equity_range_id",
                                      readonly=False, store=True)

    @api.depends('is_company')
    def _compute_equity_range_id(self):
        for r in self:
            r.equity_range_id = False if not r.is_company else r.equity_range_id
