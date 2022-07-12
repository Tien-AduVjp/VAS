from odoo import models


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'
    
    def compute_landed_cost(self):
        """
        Override to get adjustment lines to respect currency's rounding to avoid missing value when rounding. For example
            - Assume:
                - We have 3 items
                - Total landed cost to allocated for the whole 3 items is 100
                - The given currency's decimal places is 0
            - Before overriding,
                - adjustment lines may look like
                    - item 1: 33.34
                    - item 2: 33.34
                    - item 3: 33.32
                - and the account move will round them all to say 99 in total since the currency's decimal place is 0. Hence, we lost 1 in accounting
            - After this overriding
                - adjustment lines will look like
                    - item 1: 33
                    - item 2: 33
                    - item 3: 34
                - and the account move will round them all to say 100 in total. Nothing lost here
        """
        super(LandedCost, self).compute_landed_cost()
        # Process landed cost in a currency that has decimal places less than the precision digits of the Product Price
        digits = self.env['decimal.precision'].precision_get('Product Price')
        for r in self.filtered(lambda rec: rec.valuation_adjustment_lines and rec.currency_id.decimal_places < digits):
            adjustment_lines_updated_cmd = []
            for cost_line in r.cost_lines:
                matched_adjustment_lines = r.valuation_adjustment_lines.filtered(lambda al: al.cost_line_id.id == cost_line.id)
                if not matched_adjustment_lines:
                    continue
                # round the additional_landed_cost to the corresponding currency's decimal places
                currency_rounded_adjustment_line_values = matched_adjustment_lines.mapped(
                    lambda line: r.currency_id.round(line.additional_landed_cost)
                    )
                # difference between cost line's cost and the rounded adjustment lines' value
                diff = cost_line.price_unit - sum(currency_rounded_adjustment_line_values)
                # compensate the diff to the last line
                currency_rounded_adjustment_line_values[-1] += diff
                for adj_line, value in zip(matched_adjustment_lines, currency_rounded_adjustment_line_values):
                    adjustment_lines_updated_cmd += [(1, adj_line.id, {'additional_landed_cost': value})]

            if adjustment_lines_updated_cmd:
                r.valuation_adjustment_lines = adjustment_lines_updated_cmd
