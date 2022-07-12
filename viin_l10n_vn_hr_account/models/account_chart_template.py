from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _load_template(self, company, code_digits=None, account_ref=None, taxes_ref=None):
        account_ref, taxes_ref = super(AccountChartTemplate, self)._load_template(company, code_digits, account_ref, taxes_ref)
        company._apply_vietnam_empoloyee_payable_account()
        return account_ref, taxes_ref
