from odoo import models, fields


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    return_reason_id = fields.Many2one('product.return.reason', string='Return Reason', ondelete='restrict')

