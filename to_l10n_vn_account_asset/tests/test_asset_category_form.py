from odoo.tests.common import tagged

from odoo.addons.to_account_asset.tests.asset_common import AssetCommon


@tagged('post_install', '-at_install')
class TestAssetCategoryForm(AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref='l10n_vn.vn_template')
        
        cls.env.user.write({'groups_id': [
            (4, cls.env.ref('analytic.group_analytic_tags').id),
            (4, cls.env.ref('analytic.group_analytic_accounting').id),
            ]})

    def test_01_create_new_asset_category(self):
        """Case 1:
        Action:
            - Create new asset category
        Output:
            - analytic_tag_ids as analytic_tag_fixed_assets
        """
        self.assertEqual(self.asset_category.analytic_tag_ids,
                         self.env.ref('l10n_vn_c200.analytic_tag_fixed_assets'))
