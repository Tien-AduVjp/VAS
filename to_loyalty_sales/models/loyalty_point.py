from odoo import fields, models


class LoyaltyPoint(models.Model):
    _inherit = 'loyalty.point'

    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', related='sale_order_line_id.order_id', readonly=False, store=True)
