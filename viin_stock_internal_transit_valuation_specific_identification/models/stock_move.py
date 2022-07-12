from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _create_internal_transit_svl(self, forced_quantity=None):
        specs_moves = self.filtered(lambda m: m.product_id.cost_method == 'specific_identification')

        res = super(StockMove, (self - specs_moves))._create_internal_transit_svl(forced_quantity=forced_quantity)

        svl_vals_list = []
        for move in specs_moves:
            valued_move_lines = move._get_internal_transit_move_lines()

            internal_transit_vals = dict(move._prepare_common_svl_vals(), remaining_qty=0)
            for line in valued_move_lines:
                if line.location_id.usage == 'internal' and line.location_dest_id.usage == 'transit':
                    out_svl_vals = line.product_id.with_context(lot_id=line.lot_id.id)._prepare_out_svl_vals(line.qty_done, line.company_id)
                    internal_transit_vals.update(out_svl_vals)

                elif line.location_id.usage == 'transit' and line.location_dest_id.usage == 'internal':
                    if move.move_orig_ids:
                        unit_cost = move.move_orig_ids.stock_valuation_layer_ids.filtered(lambda svl: svl.lot_id == line.lot_id).unit_cost
                    else:
                        unit_cost = abs(move._get_price_unit())
                    in_svl_vals = line.product_id._prepare_in_svl_vals(line.qty_done, unit_cost)
                    internal_transit_vals.update(in_svl_vals)

                svl_vals_list.append(dict(internal_transit_vals,
                                          lot_id=line.lot_id.id,
                                          description=internal_transit_vals['description'] + ' (%s)' % line.lot_id.name))

        return self.env['stock.valuation.layer'].sudo().create(svl_vals_list) | res
