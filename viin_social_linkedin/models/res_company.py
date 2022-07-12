from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    linkedin_app_id = fields.Char(string='Linkedin App ID')
    linkedin_client_secret = fields.Char(string='Linkedin Client Secret')
