from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rotating_token_life = fields.Float(related='company_id.rotating_token_life', readonly=False)
