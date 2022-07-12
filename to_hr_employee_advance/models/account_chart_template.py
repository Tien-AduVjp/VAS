from odoo import models, api


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(acc_template_ref, company, journals_dict)
        journal_data.append(company._prepare_employee_advance_journal_data())
        return journal_data
    
    @api.model
    def generate_journals(self, acc_template_ref, company, journals_dict=None):
        res = super(AccountChartTemplate, self).generate_journals(acc_template_ref, company, journals_dict=journals_dict)
        # Because advance journals created with type is 'general', so they need update type to 'cash' after created.
        company._update_employee_advance_journal_if_exists()
        return res
