# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountChartTemplate(models.Model):
    _inherit = "account.chart.template"
    
    income_currency_conversion_diff_account_id = fields.Many2one('account.account.template',
        string="Income Currency Conversion Account", domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    expense_currency_conversion_diff_account_id = fields.Many2one('account.account.template',
        string="Expense Currency Conversion Account", domain=[('internal_type', '=', 'other'), ('deprecated', '=', False)])
    
    @api.model
    def generate_journals(self, acc_template_ref, company, journals_dict=None):
        res = super(AccountChartTemplate, self).generate_journals(acc_template_ref, company, journals_dict)
        cdj_journal_id = self.env['account.journal'].search([
            ('type', '=', 'general'),
            ('code', '=', 'CCDJ'),
            ('company_id', '=', company.id)], limit=1)
        if cdj_journal_id:
            company.write({'currency_conversion_diff_journal_id': cdj_journal_id.id})
        return res
    
    def _prepare_all_journals(self, acc_template_ref, company, journals_dict=None):
        journal_data = super(AccountChartTemplate, self)._prepare_all_journals(
            acc_template_ref=acc_template_ref,
            company=company,
            journals_dict=journals_dict
            )
        journal_data.append({
            'name': _('Currency Conversion Difference'),
            'type': 'general',
            'code': 'CCDJ',
            'show_on_dashboard': False,
            'sequence': 11,
            'company_id': company.id,
            'default_debit_account_id': acc_template_ref.get(self.income_currency_conversion_diff_account_id.id),
            'default_credit_account_id': acc_template_ref.get(self.expense_currency_conversion_diff_account_id.id),
            })
        return journal_data


