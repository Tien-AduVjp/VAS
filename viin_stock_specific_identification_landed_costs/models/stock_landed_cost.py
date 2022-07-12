from collections import defaultdict

from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def button_validate(self):
        self._check_can_validate()
        cost_without_adjusment_lines = self.filtered(lambda c: not c.valuation_adjustment_lines)
        if cost_without_adjusment_lines:
            cost_without_adjusment_lines.compute_landed_cost()

        specs_costs = self.filtered(lambda c: c.valuation_adjustment_lines\
                                    and all([l.move_id.product_id.categ_id.property_cost_method == 'specific_identification'\
                                             for l in c.valuation_adjustment_lines]))

        res = super(StockLandedCost, self - specs_costs).button_validate()
        account_moves = self.env['account.move'].sudo().search([('ref', 'in', self.mapped('name'))])
        for r in self:
            valuation_layer_ids = []
            move_lines = []
            move = account_moves.filtered(lambda m: m.ref == r.name)
            if not move:
                move_vals = {
                    'journal_id': r.account_journal_id.id,
                    'date': r.date,
                    'ref': r.name,
                    'line_ids': [],
                    'move_type': 'entry',
                }
            cost_to_add_byproduct = defaultdict(lambda: 0.0)
            for line in r.valuation_adjustment_lines.filtered(lambda line: line.move_id.product_id.cost_method\
                                                              == 'specific_identification'):
                line.write({'move_id': line.move_id.id})
                # Prorate the value at what's still in stock
                svl = line.stock_valuation_layer_id
                cost_to_add = 0
                if svl.quantity != 0:
                    cost_to_add = (svl.remaining_qty / svl.quantity) * line.additional_landed_cost
                if not r.company_id.currency_id.is_zero(cost_to_add):
                    valuation_layer = self.env['stock.valuation.layer'].create({
                        'value': cost_to_add,
                        'unit_cost': 0,
                        'quantity': 0,
                        'remaining_qty': 0,
                        'stock_valuation_layer_id': svl.id,
                        'description': r.name,
                        'stock_move_id': line.move_id.id,
                        'product_id': line.move_id.product_id.id,
                        'stock_landed_cost_id': r.id,
                        'company_id': r.company_id.id,
                        'lot_id': svl.lot_id.id,
                    })
                    svl.remaining_value += cost_to_add
                    valuation_layer_ids.append(valuation_layer.id)
                # `remaining_qty` is negative if the move is out and delivered proudcts that were not
                # in stock.
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = svl.quantity - svl.remaining_qty
                elif line.move_id._is_out():
                    qty_out = svl.quantity
                move_lines.extend(line.with_context(landed_cost_lot_name=svl.lot_id.name)._create_accounting_entries(move, qty_out))

            # batch standard price computation avoid recompute quantity_svl at each iteration
            products = self.env['product.product'].browse(p.id for p in cost_to_add_byproduct.keys())
            for product in products:  # iterate on recordset to prefetch efficiently quantity_svl
                if not float_is_zero(product.quantity_svl, precision_rounding=product.uom_id.rounding):
                    product.with_company(r.company_id).sudo().standard_price += cost_to_add_byproduct[product] / product.quantity_svl

            move_vals_to_write = {}
            if move_lines:
                move_lines.insert(0, (6, 0, move.line_ids.ids))
                move_vals_to_write['line_ids'] = move_lines
            if valuation_layer_ids:
                if move:
                    move_vals_to_write['stock_valuation_layer_ids'] = [(4, svl_id, 0) for svl_id in valuation_layer_ids]
                else:
                    move_vals_to_write['stock_valuation_layer_ids'] = [(6, None, valuation_layer_ids)]

            if move_vals_to_write:
                if move:
                    move.button_draft()
                    move.write(move_vals_to_write)
                else:
                    move_vals.update(move_vals_to_write)
                    move = move.create(move_vals)
                    r.write({'state': 'done', 'account_move_id': move.id})
                move._post()

            if r.vendor_bill_id and r.vendor_bill_id.state == 'posted' and r.company_id.anglo_saxon_accounting:
                all_amls = r.vendor_bill_id.line_ids | r.account_move_id.line_ids
                for product in r.cost_lines.product_id:
                    accounts = product.product_tmpl_id.get_product_accounts()
                    input_account = accounts['stock_input']
                    all_amls.filtered(lambda aml: aml.account_id == input_account and not aml.full_reconcile_id).reconcile()
        return res

    def get_valuation_lines(self):
        """
        Overide to support specific identification method by generating layers for for the products
        that is configure with specific identification then append the super's result
        """
        lines = []

        # find moves with real time valuation and specific identification costing method
        specific_identification_method_moves = self.picking_ids.move_lines.filtered(
            lambda m: m.product_id.valuation == 'real_time' \
            and m.product_id.cost_method == 'specific_identification' \
            and m.state != 'cancel'
            )
        # generate stock valuation layers vals
        for move in specific_identification_method_moves:
            for svl in move.stock_valuation_layer_ids.filtered(lambda svl: not svl.stock_landed_cost_id):
                vals = {
                    'product_id': move.product_id.id,
                    'move_id': move.id,
                    'stock_valuation_layer_id': svl.id,
                    'quantity': svl.quantity,
                    'former_cost': svl.value,
                    'weight': move.product_id.weight * svl.quantity,
                    'volume': move.product_id.volume * svl.quantity,
                }
                lines.append(vals)

        try:
            lines.extend(super(StockLandedCost, self).get_valuation_lines())
        except UserError as e:
            # bypass the super's exception
            target_model_descriptions = dict(self._fields['target_model']._description_selection(self.env))
            error = (_("You cannot apply landed costs on the chosen %s(s). Landed costs can only be applied for products with FIFO or average costing method.", target_model_descriptions[self.target_model]))
            if error == e.args[0]:
                if lines:
                    return lines
                raise UserError(_("You cannot apply landed costs on the chosen %s(s). Landed costs can only be applied for products with FIFO or average or specific identification costing method.", target_model_descriptions[self.target_model]))
            else:
                raise
        return lines
