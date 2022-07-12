from odoo import models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _get_einvoices_to_issue_domain(self):
        res = super(AccountJournal, self)._get_einvoices_to_issue_domain()
        if self.company_einvoice_provider == 'sinvoice' and self.company_id.sinvoice_start:
            res.append(('invoice_date', '>', self.company_id.sinvoice_start))
        return res

