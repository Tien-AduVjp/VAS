import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def _fix_vietnam_coa(self):
        """
        This method is safe for calling multiple times.
        It may take long time for the first run, depending on how large the number of affected journal items is.
        The second time and on may cost a few seconds only.
        """
        vn_chart = self.env.ref('l10n_vn.vn_template')
        companies = self.env['res.company'].with_context(active_test=False).search([('chart_template_id', '=', vn_chart.id)])
        # Prefetching
        template_taxes = self.env['account.tax.template'].search([('chart_template_id', '=', vn_chart.id)])
        template_taxes.read(['id', 'name', 'type_tax_use', 'amount_type', 'amount', 'description', 'tax_group_id'])
        template_accounts = self.env['account.account.template'].search([('chart_template_id', '=', vn_chart.id)])
        template_accounts.read(['code'])
        all_cash_journals = self.env['account.journal'].search([('company_id', 'in', companies.ids), ('type', '=', 'cash')])
        all_old_profit_loss_accounts = all_cash_journals.profit_account_id + all_cash_journals.loss_account_id
        all_accounts = self.env['account.account'].search([('company_id', 'in', companies.ids), ('code', 'in', ('711', '811', '132', '131'))])
        no_tag_all_accounts = self.env['account.account'].search([('company_id', 'in', companies.ids), ('tag_ids', '=', False)])

        for company in companies:
            # Fix taxes
            account_ref = {}
            taxes_ref = {}
            account_template_ref = vn_chart.generate_account(taxes_ref, account_ref, vn_chart.code_digits, company)
            account_ref.update(account_template_ref)
            generated_tax_res = template_taxes._generate_tax(company)
            taxes_ref.update(generated_tax_res['tax_template_to_tax'])

            # Writing account values after creation of accounts
            for key, value in generated_tax_res['account_dict']['account.tax'].items():
                if value['cash_basis_transition_account_id']:
                    self.env['account.tax'].browse(key).write({
                        'cash_basis_transition_account_id': account_ref.get(value['cash_basis_transition_account_id'], False),
                    })
            for key, value in generated_tax_res['account_dict']['account.tax.repartition.line'].items():
                if value['account_id']:
                    self.env['account.tax.repartition.line'].browse(key).write({
                        'account_id': account_ref.get(value['account_id']),
                    })

            company_vals = {}
            journal_vals = {}
            for account in all_accounts:
                if account.company_id.id != company.id:
                    continue
                # Replace account 132 to 131 for default pos receivable account in the company
                if account.code == '131':
                    company_vals.update({
                        'account_default_pos_receivable_account_id': account.id,
                    })
                # Replace account 999* to 711 for default cash difference income account in the company
                elif account.code == '711':
                    company_vals.update({
                        'default_cash_difference_income_account_id': account.id,
                    })
                    journal_vals.update({
                        'profit_account_id': account.id,
                    })
                # Replace account 999* to 811 for default cash difference expense account in the company
                elif account.code == '811':
                    company_vals.update({
                        'default_cash_difference_expense_account_id': account.id,
                    })
                    journal_vals.update({
                        'loss_account_id': account.id,
                    })
            company.write(company_vals)

            # Replace profit account and loss account in cash journal
            # In Cash Journal:
            #     Profit Account: 999* Cash Difference Gain => 711 Other Income
            #     Loss Account: 999* Cash Difference Loss => 811 Other Expenses
            cash_journals = all_cash_journals.filtered(lambda c: c.company_id.id == company.id)
            if journal_vals.get('profit_account_id', False) and journal_vals.get('loss_account_id', False):
                cash_journals.write(journal_vals)

            # Fill cash suspense account for cash journal
            # In Cash Journal:
            #     Suspense Account: 112* Bank Suspense Account => 111* Cash Suspense Account
            cash_suspense_account = self.env['account.chart.template']._create_liquidity_journal_cash_suspense_account(
                company, self.env.ref('l10n_vn.vn_template').code_digits
            )
            cash_journals.suspense_account_id = cash_suspense_account
            company.account_journal_cash_suspense_account_id = cash_suspense_account

            # Set company stock accounts
            vn_chart.generate_properties(account_template_ref, company)
            # Update company default account
            company.write({'unemployment_insurance_account_id': account_ref.get(company.chart_template_id.default_unemployment_insurance_account_id.id, False)})

            # Mark the accounts (132, 999*) as deprecated
            account_132 = all_accounts.filtered(lambda a: a.code == '132' and a.company_id.id == company.id)
            old_profit_loss_accounts = all_old_profit_loss_accounts.filtered(lambda a: a.code.startswith('999') and a.company_id.id == company.id)
            deprecated_accounts = account_132 + old_profit_loss_accounts
            deprecated_accounts.deprecated = True

            # Fill account tag for the account if not specified.
            no_tag_accounts = no_tag_all_accounts.filtered(lambda c: c.company_id.id == company.id)
            no_tag_accounts._fill_account_tag_for_vn_coa()
