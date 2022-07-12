from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"
    
    vat_ctp_account_id = fields.Many2one('account.account', string='VAT Counterpart Account',
                                         help="In some cases where we do not have a counterpart account for a tax entry,"
                                         " the account set here as a counterpart account might help.\n"
                                         "For example, according to Vietnam Accounting Standards, the account code 33312"
                                         " (VAT on imported goods) requires the account 1331 (VAT on purchase of goods"
                                         " and services - Deducted VAT) for a counterpart of its.")

    @api.onchange('id')
    def _onchange_tax_group_id(self):
        if self.tax_id:
            if self.tax_id.tax_group_id:
                if self.tax_id.tax_group_id.vat_ctp_account_id:
                    self.vat_ctp_account_id = self.tax_id.tax_group_id.vat_ctp_account_id

    @api.constrains('invoice_tax_id', 'refund_tax_id', 'vat_ctp_account_id')
    def _check_is_vat_vat_ctp_account_id(self):
        for r in self:
            if not r.tax_id.is_vat and r.vat_ctp_account_id:
                raise ValidationError(_('This tax is not a VAT, hence, its counterpart account must be removed'))