from odoo import models, fields, api


class ProductReturnReason(models.Model):
    _inherit = 'product.return.reason'

    stock_move_ids = fields.One2many('stock.move', 'return_reason_id', string='Stock Moves', help="Stock Moves that concern this return reason")

    @api.depends('stock_move_ids')
    def _compute_product_ids(self):
        for r in self:
            r.product_ids = [(6, 0, r.stock_move_ids.product_id.ids)]
