import logging

from odoo import models, api

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def fix_vietnam_coa(self):
        """
        This method is safe for calling multiple times.
        It may take long time for the first run, depending on how large the number of affected journal items is.
        The second time and on may cost a few seconds only.
        """
        vn_chart_id = self.env.ref('l10n_vn.vn_template')

        AccountTaxObj = self.env['account.tax']
        template_taxes = self.env['account.tax.template'].search([('chart_template_id', '=', vn_chart_id.id)])
        # prefetching
        template_taxes.read(['id', 'name', 'type_tax_use', 'amount_type', 'amount', 'description', 'tax_group_id'])

        template_accounts = self.env['account.account.template'].search([('chart_template_id', '=', vn_chart_id.id)])
        template_accounts.read(['code'])

        for company in self.with_context(active_test=False).search([('chart_template_id', '=', vn_chart_id.id)]):
            # FIX TAXES
            account_ref = {}
            taxes_ref = {}

            account_template_ref = vn_chart_id.generate_account(taxes_ref, account_ref, vn_chart_id.code_digits, company)
            account_ref.update(account_template_ref)

            generated_tax_res = template_taxes._generate_tax(company)
            taxes_ref.update(generated_tax_res['tax_template_to_tax'])

            # writing account values after creation of accounts
            for key, value in generated_tax_res['account_dict']['account.tax'].items():
                if value['cash_basis_transition_account_id'] or value['cash_basis_base_account_id']:
                    AccountTaxObj.browse(key).write({
                        'cash_basis_transition_account_id': account_ref.get(value['cash_basis_transition_account_id'], False),
                        'cash_basis_base_account_id': account_ref.get(value['cash_basis_base_account_id'], False),
                    })

            AccountTaxRepartitionLineObj = self.env['account.tax.repartition.line']
            for key, value in generated_tax_res['account_dict']['account.tax.repartition.line'].items():
                if value['account_id']:
                    AccountTaxRepartitionLineObj.browse(key).write({
                        'account_id': account_ref.get(value['account_id']),
                    })
                    
            # set company stock accounts
            vn_chart_id.generate_properties(account_template_ref, company)
