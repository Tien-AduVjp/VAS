from odoo import api, fields, models
from odoo.tools.float_utils import float_compare, float_round


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    price_unit = fields.Monetary('Unit Price', currency_field='currency_id',
                                 groups='stock.group_stock_manager',
                                 help="Cost price is in the company currency")

    diff_float_compared = fields.Float('Difference', compute='_compute_diff_float_compared',
                                  help="Technical field to show/hide the price_unit.")
    cost_method = fields.Selection(related="product_id.categ_id.property_cost_method", readonly=True)

    @api.depends('inventory_quantity', 'quantity')
    def _compute_diff_float_compared(self):
        for r in self:
            rounding = r.product_id.uom_id.rounding
            if rounding:
                diff = float_round(r.inventory_quantity - r.quantity, precision_rounding=rounding)
                r.diff_float_compared = float_compare(diff, 0, precision_rounding=rounding)
            else:
                r.diff_float_compared = 0

    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        res = super(StockQuant, self)._get_inventory_fields_create() + ['price_unit']
        return res

    @api.model
    def _get_inventory_fields_write(self):
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        res = super(StockQuant, self)._get_inventory_fields_write() + ['price_unit']
        return res

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        """ Called when user manually set a new quantity (via `inventory_quantity`)
        just before creating the corresponding stock move.

        :param location_id: `stock.location`
        :param location_dest_id: `stock.location`
        :param out: boolean to set on True when the move go to inventory adjustment location.
        :return: dict with all values needed to create a new `stock.move` with its move line.
        """
        res = super(StockQuant, self)._get_inventory_move_values(qty, location_id, location_dest_id, out=out)

        if self.diff_float_compared > 0:
            res['price_unit'] = self.price_unit
        return res
