from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    check_unique_product_default_code = fields.Boolean(related='company_id.check_unique_product_default_code', readonly=False)
