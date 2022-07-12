from odoo.tests import common

from . import asset_common


@common.tagged('post_install', '-at_install')
class TestAssetForm(asset_common.AssetCommon):

    def test_01_change_category_on_asset(self):
        asset_form = common.Form(self.env['account.asset.asset'])
        asset_form.name = 'ASSET 1'
        asset_form.category_id = self.asset_category
        asset = asset_form.save()

        self.assertRecordValues(asset.sudo(), [self._get_expected_asset_category_values(self.asset_category)])

    def test_02_asset_has_been_linked_to_invoice_line(self):
        invoice = self.init_invoice('in_invoice')

        asset_form = common.Form(self.env['account.asset.asset'])
        asset_form.name = 'ASSET 1'
        asset_form.category_id = self.asset_category
        asset_form.invoice_line_id = invoice.invoice_line_ids[0]
        asset = asset_form.save()

        self.assertEqual(asset.value, invoice.invoice_line_ids[0].balance, "Value on asset should be equal to the balance of invoice line")
        self.assertEqual(asset.invoice_id, invoice)

    def _get_expected_asset_category_values(self, asset_category):
        return {
                'method': asset_category.method,
                'method_number': asset_category.method_number,
                'method_time': asset_category.method_time,
                'method_period': asset_category.method_period,
                'method_progress_factor': asset_category.method_progress_factor,
                'method_end': asset_category.method_end,
                'prorata': asset_category.prorata,
                'date_first_depreciation': asset_category.date_first_depreciation,
                'analytic_account_id': asset_category.sudo().analytic_account_id.id,
                # skip check analytic_tag_ids
                # because Form test currently does not support autofill many2many fields
                # 'analytic_tag_ids': asset_category.sudo().analytic_tag_ids.ids,
                'depreciation_expense_account_id': asset_category.depreciation_expense_account_id.id,
                'revaluation_decrease_account_id': asset_category.revaluation_decrease_account_id.id,
                'revaluation_increase_account_id': asset_category.revaluation_increase_account_id.id,
                }
