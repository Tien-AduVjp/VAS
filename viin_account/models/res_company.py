from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    property_vat_ctp_account_id = fields.Many2one('account.account', string='VAT Counterpart Account')
