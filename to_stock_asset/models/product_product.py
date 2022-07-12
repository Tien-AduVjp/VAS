from odoo import models
from odoo.tools.float_utils import float_is_zero


class ProductProduct(models.Model):
    _inherit = 'product.product'


    def _run_fifo(self, quantity, company):
        self.ensure_one()

        lot_id = self._context.get('lot_id', False)
        if lot_id:
            # Find back incoming stock valuation layers (called candidates here) to value `quantity`.
            qty_to_take_on_candidates = quantity
            candidates = self.env['stock.valuation.layer'].sudo().with_context(active_test=False).search([
                ('product_id', '=', self.id),
                ('remaining_qty', '>', 0),
                ('company_id', '=', company.id),
            ])

            candidates = candidates.sorted(reverse=True)

            new_standard_price = 0
            tmp_value = 0  # to accumulate the value taken on the candidates
            for candidate in candidates:
                if lot_id in candidate.stock_move_id.mapped('move_line_ids.lot_id').ids:
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

            # Update the standard price with the price of the last used candidate, if any.
            if new_standard_price and self.cost_method == 'fifo':
                self.sudo().with_company(company).standard_price = new_standard_price

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
                last_fifo_price = new_standard_price or self.standard_price
                negative_stock_value = last_fifo_price * -qty_to_take_on_candidates
                tmp_value += abs(negative_stock_value)
                vals = {
                    'remaining_qty': -qty_to_take_on_candidates,
                    'value': -tmp_value,
                    'unit_cost': last_fifo_price,
                }
            return vals

        return super(ProductProduct, self)._run_fifo(quantity, company)
