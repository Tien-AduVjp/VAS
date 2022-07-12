from odoo import models,fields


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'
    
    allow_process_exceeded_demand_qty = fields.Boolean(string="Allow process exceeded demand quantity", default=True,
            help="If you not checked, when making stock picking the system will check the quantity 'Done' and quantity 'Initial Demand'.\n"
            "If user input a quantity of 'Done' greater than the 'Initial Demand' quantity column, then user will not be able to validate it")

