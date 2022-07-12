from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    return_reason_id = fields.Many2one('product.return.reason', string='Return Reason', readonly=True, ondelete='restrict')
