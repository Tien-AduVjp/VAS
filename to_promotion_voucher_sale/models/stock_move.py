from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_done(self):
        result = super(StockMove, self).action_done()

        sale_order_lines = self.filtered(lambda move: move.procurement_id.sale_line_id and move.product_id.expense_policy == 'no').mapped('procurement_id.sale_line_id')
        for line in sale_order_lines:
            if line.product_id.is_promotion_voucher:
                lot_ids = self.lot_ids.filtered(lambda x: x.product_id.id == line.product_id.id)
                if lot_ids:
                    vouchers = self.env['voucher.voucher'].search([('lot_id', 'in', lot_ids.ids)])
                    if vouchers:
                        vouchers.write({'sale_order_line_id': line.id})
        return result

