from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_to_stock_barcode = fields.Boolean("Inventory Barcode Scanner")