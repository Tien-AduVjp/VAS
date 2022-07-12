from odoo import fields, tools
from odoo.tests import common
from odoo.modules.module import get_resource_path


@common.tagged('post_install', '-at_install')
class TestAccountAsset(common.TransactionCase):

    def _load(self, module, *args):
        tools.convert_file(self.cr, 'to_account_asset',
                           get_resource_path(module, *args),
                           {}, 'init', False, 'test', self.registry._assertion_report)

    def test_00_account_asset_asset(self):
        self._load('account', 'test', 'account_minimal_test.xml')
        self._load('to_account_asset', 'test', 'account_asset_demo_test.xml')

        # In order to test the process of Account Asset, I perform a action to confirm Account Asset.
        self.browse_ref("to_account_asset.account_asset_asset_vehicles_test0").validate()

        # I check Asset is now in Open state.
        self.assertEqual(self.browse_ref("to_account_asset.account_asset_asset_vehicles_test0").state, 'open',
            'Asset should be in Open state')

        # I compute depreciation lines for asset of CEOs Car.
        self.browse_ref("to_account_asset.account_asset_asset_vehicles_test0")._compute_depreciation_board()
        value = self.browse_ref("to_account_asset.account_asset_asset_vehicles_test0")
        self.assertEqual(value.method_number, len(value.depreciation_line_ids),
            'Depreciation lines not created correctly')

        # I create account move for all depreciation lines.
        ids = self.env['account.asset.depreciation.line'].search([('asset_id', '=', self.ref('to_account_asset.account_asset_asset_vehicles_test0'))])
        for line in ids:
            line.create_move()

        # I Check that After creating all the moves of depreciation lines the state "Close".
        self.assertEqual(self.browse_ref("to_account_asset.account_asset_asset_vehicles_test0").state, 'close',
            'State of asset should be close')

        # WIZARD
        # I create a record to change the duration of asset for calculating depreciation.
        account_asset_asset_office0 = self.browse_ref('to_account_asset.account_asset_asset_office_test0')
        asset_modify_number_0 = self.env['asset.modify'].create({
            'name': 'Test reason',
            'method_number': 10.0,
        }).with_context({'active_id': account_asset_asset_office0.id})
        # I change the duration.
        asset_modify_number_0.with_context({'active_id': account_asset_asset_office0.id}).modify()

        # I check the proper depreciation lines created.
        self.assertEqual(account_asset_asset_office0.method_number, len(account_asset_asset_office0.depreciation_line_ids))
        # I compute a asset on period.
        account_asset_asset_office0.compute_generated_entries(fields.Date.context_today(account_asset_asset_office0),
                                                              asset_type='sale')
