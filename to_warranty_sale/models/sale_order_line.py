from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    warranty_policy_ids = fields.Many2many('warranty.policy', string='Warranty Policy', readonly=True)
