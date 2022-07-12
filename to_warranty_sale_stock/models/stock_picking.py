from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for ml in self.sudo().mapped('move_lines.move_line_ids').filtered(lambda l: l.lot_id and l.move_id.sale_line_id):
            ml.lot_id.write({
                'warranty_start_date': ml.move_id.date,
                'sale_order_id': ml.move_id.sale_line_id.order_id.id})
        return res

