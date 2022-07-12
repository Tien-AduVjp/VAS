from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    return_reason_ids = fields.Many2many('product.return.reason', 'stock_picking_return_reason_rel', 'picking_id', 'return_reason_id',
                                         string='Return Reasons', compute='_compute_return_reason_ids', store=True)

    @api.depends('move_lines', 'move_lines.return_reason_id')
    def _compute_return_reason_ids(self):
        for r in self:
            r.return_reason_ids = r.move_lines.mapped('return_reason_id')
