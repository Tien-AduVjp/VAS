 
from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _get_einvoices_to_issue_domain(self):
        res = super(AccountJournal, self)._get_einvoices_to_issue_domain()
        if self.company_einvoice_provider == 'vninvoice' and self.company_id.vninvoice_start_date:
            res.append(('invoice_date', '>', self.company_id.vninvoice_start_date))
        return res