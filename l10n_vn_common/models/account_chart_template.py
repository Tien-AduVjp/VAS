from odoo import fields, models, api, _


class AccountChartTemplate(models.Model):
    _inherit = 'account.chart.template'

    circular_code = fields.Char(string='Circular Code')
    account_journal_cash_suspense_account_id = fields.Many2one('account.account.template', string='Journal Cash Suspense Account')
    default_unemployment_insurance_account_id = fields.Many2one('account.account.template', string='Unemployment Insurance account')
    property_vat_ctp_account_id = fields.Many2one('account.account.template', string='VAT Counterpart Account')

    @api.model
    def _create_liquidity_journal_cash_suspense_account(self, company, code_digits):
        return self.env['account.account'].create({
            'name': _('Cash Suspense Account'),
            'code': self.env['account.account']._search_new_account_code(company, code_digits, company.cash_account_code_prefix or ''),
            'user_type_id': self.env.ref('account.data_account_type_current_assets').id,
            'company_id': company.id,
        })

    def _load(self, sale_tax_rate, purchase_tax_rate, company):
        res = super(AccountChartTemplate, self)._load(sale_tax_rate, purchase_tax_rate, company)
        # Set default cash difference account on company
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if company.chart_template_id.id in vn_charts.ids:
            if not company.account_journal_cash_suspense_account_id:
                company.account_journal_cash_suspense_account_id = self._create_liquidity_journal_cash_suspense_account(company, self.code_digits)
            cash_journals = self.env['account.journal'].search([('company_id', '=', company.id), ('type', '=', 'cash')])
            cash_journals.suspense_account_id = company.account_journal_cash_suspense_account_id
        return res

    def _load_company_accounts(self, account_ref, company):
        # Set the default accounts on the company
        res = super(AccountChartTemplate, self)._load_company_accounts(account_ref, company)
        vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if company.chart_template_id.id in vn_charts.ids:
            accounts = {
                'account_journal_cash_suspense_account_id': self.account_journal_cash_suspense_account_id.id,
                'unemployment_insurance_account_id': self.default_unemployment_insurance_account_id.id,
            }
            values = {}
            # The loop is to avoid writing when we have no values, thus avoiding erasing the account from the parent
            for key, account in accounts.items():
                if account_ref.get(account):
                    values[key] = account_ref.get(account)

            company.write(values)
        return res

    @api.model
    def _get_installed_vietnam_coa_templates(self):
        return self.env.ref('l10n_vn.vn_template')
