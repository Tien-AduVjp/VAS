from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    facebook_app_id = fields.Char(string='Facebook App ID')
    facebook_client_secret = fields.Char(string='Facebook Client Secret')
