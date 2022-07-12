from odoo import models, fields


class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    # TODO: remove me in master/15+
    vat_ctp_account_id = fields.Many2one('account.account', string='VAT Counterpart Account',
                                         help='This provides default value for VAT Counterpart Account on the tax form')
