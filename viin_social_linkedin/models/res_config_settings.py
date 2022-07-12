from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    linkedin_app_id = fields.Char(string='Linkedin App ID', related='company_id.linkedin_app_id', readonly=False)
    linkedin_client_secret = fields.Char(string='Linkedin Client Secret', related='company_id.linkedin_client_secret', readonly=False)
