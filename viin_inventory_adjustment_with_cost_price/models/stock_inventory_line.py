from odoo import api, fields, models


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    cost_price = fields.Monetary('Cost Price', currency_field='currency_id', help="Cost price is in the company currency")
    currency_id = fields.Many2one('res.currency', 'Currency', related='company_id.currency_id', readonly=True, store=True)
    cost_method = fields.Selection(related="categ_id.property_cost_method", readonly=True)

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        if self.difference_qty <= 0:
            self.cost_price = 0

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        res = super(InventoryLine, self)._get_move_values(qty, location_id, location_dest_id, out)
        # found more than expected
        if self.difference_qty > 0 and self.cost_price:
            res['price_unit'] = self.cost_price
        return res
