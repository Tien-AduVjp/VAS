from odoo import models

class AccountAcount(models.Model):
    _inherit = 'account.account'
    
    def _get_vat_counterpart_account(self, company):
        """
        Return VAT counterpart account for company
        """
        return self.browse()
