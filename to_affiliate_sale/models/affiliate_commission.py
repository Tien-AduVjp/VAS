from odoo import fields, models


class AffiliateCommission(models.Model):
    _inherit = 'affiliate.commission'

    order_id = fields.Many2one('sale.order', string="Sales Order", readonly=True,
                               states={'draft': [('readonly', False)]})
