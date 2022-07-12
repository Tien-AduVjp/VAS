from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    check_unique_vat = fields.Boolean(related='company_id.check_unique_vat', readonly=False)
