from odoo import models, fields


class AccountTaxRepartitionLineTemplate(models.Model):
    _inherit = "account.tax.repartition.line.template"
    
    vat_ctp_account_id = fields.Many2one('account.account', string='VAT Counterpart Account',
                                         help="In some cases where we do not have a counterpart account for a tax entry,"
                                         " the account set here as a counterpart account might help.\n"
                                         "For example, according to Vietnam Accounting Standards, the account code 33312"
                                         " (VAT on imported goods) requires the account 1331 (VAT on purchase of goods"
                                         " and services - Deducted VAT) for a counterpart of its.")
