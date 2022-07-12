from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pricelist_id = fields.Many2one(tracking=True)
