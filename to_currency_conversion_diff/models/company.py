# -*- coding: utf-8 -*-
from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    currency_conversion_diff_journal_id = fields.Many2one('account.journal', string="Currency Conversion Difference Journal", domain=[('type', '=', 'general')])
    income_currency_conversion_diff_account_id = fields.Many2one('account.account', related='currency_conversion_diff_journal_id.default_credit_account_id', readonly=False,
        string="Gain Currency Conversion Account", domain="[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', id)]")
    expense_currency_conversion_diff_account_id = fields.Many2one('account.account', related='currency_conversion_diff_journal_id.default_debit_account_id', readonly=False,
        string="Loss Currency Conversion Account", domain="[('internal_type', '=', 'other'), ('deprecated', '=', False), ('company_id', '=', id)]")

    def _prepare_currency_conversion_journal_data(self):
        return {
            'name': _('Currency Conversion Difference'),
            'code': 'CCDJ',
            'type': 'general',
            'company_id': self.id,
            'show_on_dashboard': False,
        }

    def create_currency_conversion_difference_journal_if_not_exists(self):
        Journal = self.env['account.journal']
        for company in self.env['res.company'].search([('chart_template_id', '!=', False)]):
            journal_id = Journal.search([('code', '=', 'CCDJ'), ('company_id', '=', company.id)], limit=1)
            if not journal_id:
                journal_id = Journal.create(company._prepare_currency_conversion_journal_data())
            company.write({'currency_conversion_diff_journal_id': journal_id.id})
