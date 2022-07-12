from odoo import models, fields


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    access_user_ids = fields.Many2many('res.users', string='Accessing Users',
                                       help="The users who have access to this warehouse and the warehouse's concerning operations."
                                       " If this field is left empty, all stock users will be able to do operations concerning this warehouse.")
