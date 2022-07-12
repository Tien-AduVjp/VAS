from odoo import models, api


class AccountTax(models.Model):
    _inherit = 'account.tax'
        
    @api.onchange('tax_group_id')
    def _onchange_tax_group_id(self):
        if self.tax_group_id:
            if self.tax_group_id.vat_ctp_account_id:
                for line in self.invoice_repartition_line_ids:
                    line.vat_ctp_account_id = self.tax_group_id.vat_ctp_account_id
                for line in self.refund_repartition_line_ids:
                    line.vat_ctp_account_id = self.tax_group_id.vat_ctp_account_id