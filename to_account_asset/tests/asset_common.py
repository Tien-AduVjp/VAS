from datetime import date

from odoo.tests import common

from odoo.addons.account.tests.test_account_move_in_invoice import AccountTestInvoicingCommon


class AssetCommon(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        cls.group_asset_manager = cls.env.ref('to_account_asset.group_asset_manager')
        cls.env.user.write({'groups_id': [(4, cls.group_asset_manager.id)]})

        cls.asset_account = cls.env['account.account'].create({
            'code': 'ASSET_ACCOUNT',
            'name': 'Asset - (test)',
            'user_type_id': cls.env.ref('account.data_account_type_fixed_assets').id,
            })

        cls.expense_account = cls.env['account.account'].create({
            'code': 'EXPENSE_ACCOUNT',
            'name': 'Expenses - (test)',
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
            'tag_ids': [(6, 0, cls.env.ref('account.account_tag_operating').ids)],
            })

        cls.expense_journal = cls.env['account.journal'].create({
            'code': 'EXPENSE_JOURNAL',
            'name': 'Expense journal - Test',
            'type': 'purchase',
            'default_debit_account_id': cls.expense_account.id,
            'default_credit_account_id': cls.expense_account.id,
            'refund_sequence': True,
            })

        cls.asset_category = cls.env['account.asset.category'].create(cls._prepare_asset_category_vals(cls))

    def _create_asset(self, method='linear', method_progress_factor=False, currency=False, date_first_depreciation='manual'):
        asset_form = common.Form(self.env['account.asset.asset'])
        asset_form.name = 'ASSET 1'
        asset_form.category_id = self.asset_category
        asset_form.value = 100000000
        asset_form.date = date(2020, 8, 10)
        asset_form.date_first_depreciation = date_first_depreciation
        asset_form.first_depreciation_date = date(2020, 8, 18)
        asset_form.method = method
        if method_progress_factor:
            asset_form.method_progress_factor = method_progress_factor
        if currency:
            asset_form.currency_id = self.currency_vnd
        asset_form.prorata = False
        return asset_form.save()

    def _prepare_asset_category_vals(self):
        return {
            'name': 'Fixed Assets Category',
            'journal_id': self.expense_journal.id,
            'method_number': 12,
            'method_period': 1,
            'asset_account_id': self.asset_account.id,
            'depreciation_account_id': self.asset_account.id,
            'depreciation_expense_account_id': self.expense_account.id,
            'revaluation_increase_account_id': self.asset_account.id,
            'revaluation_decrease_account_id': self.expense_account.id,
            'open_asset': True,
            }
