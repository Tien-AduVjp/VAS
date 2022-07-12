from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _prepare_stock_move_vals(self, first_line, order_lines):
        val = super(StockPicking, self)._prepare_stock_move_vals(first_line, order_lines)
        if first_line.return_reason_id:
            val.update({'return_reason_id': first_line.return_reason_id.id})
        return val

    def _create_move_from_pos_order_lines(self, lines):
        self.ensure_one()
        super(StockPicking, self)._create_move_from_pos_order_lines(lines)
        self.return_reason_ids = lines.mapped('return_reason_id')
