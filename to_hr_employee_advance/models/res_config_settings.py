from odoo import fields, models


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    amount_double_validation = fields.Monetary(related='company_id.amount_double_validation', readonly=False)
