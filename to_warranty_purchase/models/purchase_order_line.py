from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    warranty_policy_ids = fields.Many2many('warranty.policy', string="Warranty Policy", readonly=True)
