from odoo import models, fields, api


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"

    vat_ctp_account_id = fields.Many2one('account.account', string='VAT Counterpart Account',
                                         compute='_compute_vat_ctp_account_id', readonly=False, store=True,
                                         help="In some cases where we do not have a counterpart account for a tax entry,"
                                         " the account set here as a counterpart account might help.\n"
                                         "For example, according to Vietnam Accounting Standards, the account code 33312"
                                         " (VAT on imported goods) requires the account 1331 (VAT on purchase of goods"
                                         " and services - Deducted VAT) for a counterpart of its.")

    @api.depends('tax_id')
    def _compute_vat_ctp_account_id(self):
        for r in self:
            if r.tax_id and r.tax_id.company_id.property_vat_ctp_account_id:
                r.vat_ctp_account_id = r.company_id.property_vat_ctp_account_id
            else:
                r.vat_ctp_account_id = r.vat_ctp_account_id
