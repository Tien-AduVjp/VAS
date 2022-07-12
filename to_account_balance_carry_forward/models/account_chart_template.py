from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(acc_template_ref, company, journals_dict)
        journal_data.append(company._prepare_balance_carry_forward_journal_data())
        return journal_data

    def _load_template(self, company, code_digits=None, account_ref=None, taxes_ref=None):
        self.ensure_one()
        account_ref, taxes_ref = super(AccountChartTemplate, self)._load_template(company, code_digits, account_ref, taxes_ref)
        company._assign_balance_carry_forward_journal()

        return account_ref, taxes_ref
