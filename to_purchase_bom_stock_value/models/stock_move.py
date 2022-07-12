# -*- coding: utf-8 -*-
from odoo import models

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_phantom_move_values(self, bom_line, quantity, quantity_done):
        vals = super(StockMove, self)._prepare_phantom_move_values(bom_line, quantity, quantity_done)
        if self.purchase_line_id:
            if self.product_id.cost_method == 'standard':
                price_unit = self.product_id.standard_price
            else:
                line_price_unit = self.purchase_line_id._get_stock_move_price_unit()
                price_unit = (line_price_unit * self.purchase_line_id.product_uom._compute_quantity(self.purchase_line_id.product_qty, self.product_id.uom_id) * \
                              bom_line.price_percent) / (100 * self.env['uom.uom'].browse(vals.get('product_uom'))._compute_quantity(quantity, self.product_id.uom_id))
            vals['price_unit'] = price_unit
        return vals
            

