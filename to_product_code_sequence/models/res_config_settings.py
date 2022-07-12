from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    auto_product_default_code_generation = fields.Boolean(related='company_id.auto_product_default_code_generation', readonly=False)
