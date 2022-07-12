from datetime import date

from odoo.exceptions import ValidationError, UserError
from odoo.tests.common import tagged

from . import asset_common


@tagged('post_install', '-at_install')
class TestAssetMethod(asset_common.AssetCommon):

    def test_01_asset_has_first_depreciation_date_lt_date(self):
        asset = self._create_asset()
        with self.assertRaises(ValidationError):
            asset.write({'first_depreciation_date': date(2020, 8, 8)})

    def test_02_unlink_asset_that_has_been_depreciated(self):
        asset = self._create_asset()
        asset.validate()
        asset.depreciation_line_ids[0].create_move()
        self.assertRaises(UserError, asset.unlink)
