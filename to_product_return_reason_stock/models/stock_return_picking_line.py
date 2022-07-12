from odoo import models, fields


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    return_reason_id = fields.Many2one('product.return.reason', string='Return Reason', ondelele='cascade')
