from odoo import models, _
from odoo.tools import float_is_zero


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_price_unit(self):
        """Returns the unit price to value this stock move """
        res = super(StockMove, self)._get_price_unit()

        lot_id = self.env.context.get('force_lot_id', False)
        if lot_id and self.product_id.cost_method == 'specific_identification':
            if self.origin_returned_move_id:
                svls = self.origin_returned_move_id.sudo().stock_valuation_layer_ids.filtered(lambda svl: svl.lot_id.id == lot_id)
                if svls:
                    return svls[-1].unit_cost
            svls = self.sudo().stock_valuation_layer_ids.filtered(lambda svl: svl.lot_id.id == lot_id)
            if svls:
                return svls[-1].unit_cost
        return res

    def _create_in_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        specs_moves = self.filtered(lambda m: m.product_id.cost_method == 'specific_identification')

        res = super(StockMove, (self - specs_moves))._create_in_svl(forced_quantity=forced_quantity)

        svl_vals_list = []
        for move in specs_moves:
            move = move.with_company(move.company_id.id)
            valued_move_lines = move._get_in_move_lines()
            if forced_quantity and not valued_move_lines:
                valued_move_lines = move.move_line_ids
            for valued_move_line in valued_move_lines:
                if forced_quantity != None and float_is_zero(forced_quantity, precision_rounding=move.product_id.uom_id.rounding):
                    break
                valued_quantity = valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
                unit_cost = abs(move.with_context(forced_quantity=forced_quantity, force_lot_id=valued_move_line.lot_id.id)._get_price_unit())  # May be negative (i.e. decrease an out move).
                svl_vals = move.product_id.with_context(lot_id=valued_move_line.lot_id.id)._prepare_in_svl_vals(forced_quantity or valued_quantity, unit_cost)
                svl_vals.update(move._prepare_common_svl_vals())
                svl_vals.update({'lot_id': valued_move_line.lot_id.id})
                if forced_quantity:
                    forced_quantity -= svl_vals.get('quantity', 0)
                    svl_vals['description'] = _('Correction of %s (modification of past move)') % move.picking_id.name or move.name
                svl_vals_list.append(svl_vals)
        if svl_vals_list:
            stock_valuation_layers = self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
            res |= stock_valuation_layers
            specs_moves._account_entry_move_for_specific_identification(stock_valuation_layers)
        return res

    def _create_out_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        specs_moves = self.filtered(lambda m: m.product_id.cost_method == 'specific_identification')

        res = super(StockMove, (self - specs_moves))._create_out_svl(forced_quantity=forced_quantity)

        svl_vals_list = []
        for move in specs_moves:
            move = move.with_company(move.company_id.id)
            valued_move_lines = move._get_out_move_lines()
            if forced_quantity and not valued_move_lines:
                valued_move_lines = move.move_line_ids
            for valued_move_line in valued_move_lines:
                if forced_quantity != None and float_is_zero(forced_quantity, precision_rounding=move.product_id.uom_id.rounding):
                    break
                valued_quantity = valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
                if float_is_zero(valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                    continue
                svl_vals = move.product_id.with_context(lot_id=valued_move_line.lot_id.id)._prepare_out_svl_vals(forced_quantity or valued_quantity, move.company_id)
                svl_vals.update(move.with_context(lot_name=valued_move_line.lot_id.name)._prepare_common_svl_vals())
                if forced_quantity:
                    forced_quantity += svl_vals.get('quantity', 0)
                    svl_vals['description'] = _('Correction of %s (modification of past move)') % move.picking_id.name or move.name
                svl_vals['description'] += svl_vals.pop('rounding_adjustment', '')

                svl_vals_list.append(svl_vals)
        if svl_vals_list:
            res |= self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
        return res

    def _create_dropshipped_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        specs_moves = self.filtered(lambda m: m.product_id.cost_method == 'specific_identification')

        res = super(StockMove, (self - specs_moves))._create_dropshipped_svl(forced_quantity=forced_quantity)

        svl_vals_list = []
        for move in specs_moves:
            move = move.with_company(move.company_id.id)
            valued_move_lines = move.move_line_ids
            if forced_quantity and not valued_move_lines:
                valued_move_lines = move.move_line_ids
            for valued_move_line in valued_move_lines:
                valued_quantity = valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
                quantity = forced_quantity or valued_quantity

                unit_cost = move._get_price_unit()

                common_vals = dict(move.with_context(lot_name=valued_move_line.lot_id.name)._prepare_common_svl_vals(), remaining_qty=0)

                # create the in
                in_vals = {
                    'lot_id': valued_move_line.lot_id.id,
                    'unit_cost': unit_cost,
                    'value': unit_cost * quantity,
                    'quantity': quantity,
                }
                in_vals.update(common_vals)
                svl_vals_list.append(in_vals)

                # create the out
                out_vals = {
                    'lot_id': valued_move_line.lot_id.id,
                    'unit_cost': unit_cost,
                    'value': unit_cost * quantity * -1,
                    'quantity': quantity * -1,
                }
                out_vals.update(common_vals)
                svl_vals_list.append(out_vals)
        if svl_vals_list:
            res |= self.env['stock.valuation.layer'].sudo().create(svl_vals_list)
        return res

    def _prepare_common_svl_vals(self):
        """When a `stock.valuation.layer` is created from a `stock.move`, we can prepare a dict of
        common vals.

        :returns: the common values when creating a `stock.valuation.layer` from a `stock.move`
        :rtype: dict
        """
        res = super(StockMove, self)._prepare_common_svl_vals()
        lot_name = self.env.context.get('lot_name', False)
        if lot_name and self.product_id.cost_method == 'specific_identification':
            res['description'] += ' (%s)' % lot_name
        return res

    def _account_entry_move_for_specific_identification(self, stock_valuation_layers):
        """ Accounting Valuation Entries for specific identification method"""
        for r in self:
            if r.product_id.valuation != 'real_time':
                continue
            slvs = stock_valuation_layers.filtered(lambda svl: svl.stock_move_id.id == r.id and not svl.currency_id.is_zero(svl.value))
            if slvs:
                stock_valuation_layers -= slvs
                r.with_context(skip_accounting_valuation_entries=False)._account_entry_move(sum(slvs.mapped('quantity')), slvs[0].description, slvs[0].id, sum(slvs.mapped('value')))

                slvs -= slvs[0]
                if slvs and r.account_move_ids[-1]:
                    r.account_move_ids[-1].write({
                        'stock_valuation_layer_ids': [(4, slv.id, 0) for slv in slvs],
                        })
        return True

    def _account_entry_move(self, qty, description, svl_id, cost):
        """ Accounting Valuation Entries """
        self.ensure_one()
        if self.product_id.cost_method != 'specific_identification' or not self._is_in() or not self.env.context.get('skip_accounting_valuation_entries', True):
            return super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)
