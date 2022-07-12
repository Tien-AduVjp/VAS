from odoo import fields
from odoo.tests.common import tagged

from odoo.addons.to_account_asset.tests.asset_common import AssetCommon


@tagged('post_install', '-at_install')
class TestMethods(AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref='l10n_vn.vn_template')

        cls.asset_category.write({'method_number': 2})

    def test_01_compute_date_on_asset(self):
        """Case 1:
        Input:
            - Asset date: 10/08/2020
        Output:
            - Day as 10
            - Month as 08
            - Year as 2020
        """
        asset_expected_vals = [{
            'day': '10',
            'month': '08',
            'year': '2020',
            }]
        asset = self._create_asset()
        self.assertRecordValues(asset, asset_expected_vals)

        depr_expected_vals = [
            {
                'day': '18',
                'month': '08',
                'year': '2020',
                },
            {
                'day': '18',
                'month': '09',
                'year': '2020',
                }]
        self.assertRecordValues(asset.depreciation_line_ids, depr_expected_vals)
        """Case 1:
        Input:
            - Asset date: 18/08/2020
        Output:
            - Day as 18
            - Month as 08
            - Year as 2020
        """
        asset_expected_vals = [{
            'day': '18',
            'month': '08',
            'year': '2020',
            }]
        asset.date = fields.Date.to_date('2020-08-18')
        asset.action_compute_depreciation_board()

        self.assertRecordValues(asset, asset_expected_vals)
        self.assertRecordValues(asset.depreciation_line_ids, depr_expected_vals)
