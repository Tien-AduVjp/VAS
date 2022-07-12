from odoo import models


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(acc_template_ref=acc_template_ref, company=company, journals_dict=journals_dict)
        journal_data.append(company._prepare_salary_journal_data())
        return journal_data
