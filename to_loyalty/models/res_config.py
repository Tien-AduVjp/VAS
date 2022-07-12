from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_to_loyalty_pos = fields.Boolean(string='Loyalty Programs for Point of Sales')
    module_to_loyalty_sales = fields.Boolean(string='Loyalty Programs for Sales Management')
