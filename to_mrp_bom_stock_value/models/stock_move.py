from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_price_unit(self):
        price_unit = super(StockMove, self)._get_price_unit()

        check_unbuild = self._context.get('is_unbuild', False)
        unbuild = self.unbuild_id
        if check_unbuild and unbuild.consume_line_ids:
            # When unbuilding a manufacturing BoM:
            #    the unit_cost of produce product will always be updated according to
            #    the manufacturing cost by using the percentage on the BoM
            bom_line = self.bom_line_id or unbuild.mo_id.bom_id.bom_line_ids.filtered(lambda bl: bl.product_id == self.product_id)[:1]
            bom_line_percent = bom_line.price_percent

            svls = unbuild.consume_line_ids.stock_valuation_layer_ids
            consume_move_prod_unbuild = unbuild.consume_line_ids.filtered(lambda l: l.product_id == unbuild.product_id)[:1]

            comsume_move_prod_qty = consume_move_prod_unbuild.product_uom._compute_quantity(
                consume_move_prod_unbuild.product_uom_qty,
                consume_move_prod_unbuild.product_id.uom_id
            )
            prod_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)

            price_unit = (abs(sum(svls.mapped('unit_cost'))) * comsume_move_prod_qty * bom_line_percent) / (100 * prod_qty)

        return price_unit
