from odoo import models, api


class AccountFinancialDynamicReport(models.Model):
    _inherit = "account.financial.dynamic.report"

    @api.model
    def get_options(self, previous_options=None):
        self.filter_show_ignored_entries = True
        return super(AccountFinancialDynamicReport, self).get_options(previous_options)

