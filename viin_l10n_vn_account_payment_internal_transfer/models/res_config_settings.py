from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_intermediary_account = fields.Boolean(string='Use Intermediary Account', related='company_id.use_intermediary_account')
