from odoo import api, models
from odoo.tools import float_is_zero
from odoo.tools.float_utils import float_compare


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _prepare_in_svl_vals(self, quantity, unit_cost):
        """Prepare the values for a stock valuation layer created by a receipt.

        :param quantity: the quantity to value, expressed in `self.uom_id`
        :param unit_cost: the unit cost to value `quantity`
        :return: values to use in a call to create
        :rtype: dict
        """
        vals = super(ProductProduct, self)._prepare_in_svl_vals(quantity, unit_cost)

        if self.cost_method == 'specific_identification':
            vals['remaining_qty'] = quantity
            vals['remaining_value'] = vals['value']
        return vals

    def _prepare_out_svl_vals(self, quantity, company):
        """Prepare the values for a stock valuation layer created by a delivery.

        :param quantity: the quantity to value, expressed in `self.uom_id`
        :return: values to use in a call to create
        :rtype: dict
        """
        vals = super(ProductProduct, self)._prepare_out_svl_vals(quantity, company)

        lot_id = self.env.context.get('lot_id', False)
        if lot_id and self.cost_method == 'specific_identification':
            specs_vals = self._run_specific_identification(lot_id, abs(quantity), company)
            vals.update(specs_vals, **{'lot_id': lot_id})
        return vals

    def _run_specific_identification(self, lot_id, quantity, company):
        self.ensure_one()
        # Find back incoming stock valuation layers (called candidates here) to value `quantity`.
        qty_to_take_on_candidates = quantity
        candidates = self.env['stock.valuation.layer'].sudo().with_context(active_test=False).search([
            ('product_id', '=', self.id),
            ('lot_id', '=', lot_id),
            ('remaining_qty', '>', 0),
            ('company_id', '=', company.id),
        ])
        new_standard_price = 0
        tmp_value = 0  # to accumulate the value taken on the candidates
        for candidate in candidates:
            qty_taken_on_candidate = min(qty_to_take_on_candidates, candidate.remaining_qty)

            candidate_unit_cost = candidate.remaining_value / candidate.remaining_qty
            new_standard_price = candidate_unit_cost
            value_taken_on_candidate = qty_taken_on_candidate * candidate_unit_cost
            value_taken_on_candidate = candidate.currency_id.round(value_taken_on_candidate)
            new_remaining_value = candidate.remaining_value - value_taken_on_candidate

            candidate_vals = {
                'remaining_qty': candidate.remaining_qty - qty_taken_on_candidate,
                'remaining_value': new_remaining_value,
            }

            candidate.write(candidate_vals)

            qty_to_take_on_candidates -= qty_taken_on_candidate
            tmp_value += value_taken_on_candidate
            if float_is_zero(qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding):
                break

        # If there's still quantity to value but we're out of candidates, we fall in the
        # negative stock use case. We chose to value the out move at the price of the
        # last out and a correction entry will be made once `_fifo_vacuum` is called.
        vals = {}
        if float_is_zero(qty_to_take_on_candidates, precision_rounding=self.uom_id.rounding):
            vals = {
                'value': -tmp_value,
                'unit_cost': tmp_value / quantity,
            }
        else:
            assert qty_to_take_on_candidates > 0
            last_price = new_standard_price or self.standard_price
            negative_stock_value = last_price * -qty_to_take_on_candidates
            tmp_value += abs(negative_stock_value)
            vals = {
                'remaining_qty': -qty_to_take_on_candidates,
                'value': -tmp_value,
                'unit_cost': last_price,
            }
        return vals
