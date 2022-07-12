from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    turn_off_affiliate_page_warning = fields.Boolean(string='Turn Off Affiliate Page Warning')
