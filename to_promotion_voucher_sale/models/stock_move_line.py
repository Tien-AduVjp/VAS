from odoo import models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _action_done(self):
        super(StockMoveLine, self)._action_done()
        for r in self.exists():
            if r.sudo().voucher_id and r.move_id.sale_line_id:
                r.voucher_id.write({'sale_order_line_id': r.move_id.sale_line_id.id})

