from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'
    
    vat_ctp_account_id = fields.Many2one('account.account', string='VAT Counterpart Account',
                                         help='This provides default value for VAT Counterpart Account on the tax form')
        
    @api.constrains('is_vat', 'vat_ctp_account_id')
    def _check_is_vat_vat_ctp_account_id(self):
        for r in self:
            if not r.is_vat and r.vat_ctp_account_id:
                raise ValidationError(_("This tax group is not for VAT, hence, its counterpart account must be removed"
                                        " before saving. Or, you have to check the field 'Is VAT'."))