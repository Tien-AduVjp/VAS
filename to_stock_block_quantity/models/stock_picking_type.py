from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    allow_process_exceeded_demand_qty = fields.Boolean(string="Allow validating stock picking on exceeded demand quantity", default=True,
                                                        help="If unselected, the system will not allow a user to "
                                                                "make validation on a stock picking with "
                                                                "'Done' quantity greater than 'Initial Demand'.")
