from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _prepare_picking_vals(self, partner, picking_type, location_id, location_dest_id):
        res = super(StockPicking, self)._prepare_picking_vals(
            partner,
            picking_type,
            location_id,
            location_dest_id,
        )
        if self._context.get('force_carrier_id', False):
            res['carrier_id'] = self._context['force_carrier_id']
        return res

    def _prepare_stock_move_vals(self, first_line, order_lines):
        res = super(StockPicking, self)._prepare_stock_move_vals(first_line, order_lines)
        if self._context.get('force_delivery_date', False):
            res['date'] = res['date_deadline'] = self._context['force_delivery_date']
        return res

    def _action_done(self):
        if self._context.get('ignore_action_done', False):
            return False
        return super(StockPicking, self)._action_done()
