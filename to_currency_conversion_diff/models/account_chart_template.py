from odoo import api, models, _


class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"

    @api.model
    def generate_journals(self, acc_template_ref, company, journals_dict=None):
        res = super(AccountChartTemplate, self).generate_journals(acc_template_ref, company, journals_dict)
        cdj_journal = self.env['account.journal'].search([
            ('type', '=', 'general'),
            ('code', '=', 'CCDJ'),
            ('company_id', '=', company.id)], limit=1)
        if cdj_journal:
            ccd_income_account, ccd_expense_account = company._get_currency_conversion_diff_accounts()
            company.write({
                'currency_conversion_diff_journal_id': cdj_journal.id,
                'income_currency_conversion_diff_account_id': ccd_income_account.id,
                'expense_currency_conversion_diff_account_id': ccd_expense_account.id,
                })
        return res

    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(
            acc_template_ref=acc_template_ref,
            company=company,
            journals_dict=journals_dict
            )
        currency_conversion_journal_data = company._prepare_currency_conversion_journal_data()
        journal_data.append(currency_conversion_journal_data)
        return journal_data
