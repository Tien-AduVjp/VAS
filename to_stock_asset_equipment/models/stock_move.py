from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        self.ensure_one()

        if self.picking_id.picking_type_id.code == 'asset_allocation':
            # Return a stock picking that contains assets that is in draft state
            if self._is_in() and self.origin_returned_move_id:
                equipments = self.origin_returned_move_id.move_line_ids.sudo().filtered(
                    lambda line: line.account_asset_asset_id and line.lot_id.equipment_id).mapped('lot_id.equipment_id')
                equipments.write(equipments._prepare_equipment_assignment_vals(asset_status=False))

        return super(StockMove, self)._get_accounting_data_for_valuation()
