from odoo.tests.common import tagged

from odoo.addons.to_account_asset.tests.asset_common import AssetCommon


@tagged('post_install', '-at_install')
class TestAssetFunctional(AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref='l10n_vn.vn_template')

        cls.env.user.write({'groups_id': [
            (4, cls.env.ref('analytic.group_analytic_tags').id),
            (4, cls.env.ref('analytic.group_analytic_accounting').id),
            ]})

        cls.expense_242_account = cls.env['account.account'].search([
            ('code', '=', '242'),
            ('company_id', '=', cls.env.company.id),
            ], limit=1)
        if not cls.expense_242_account:
            cls.expense_242_account = cls.env['account.account'].create({
                'code': '242',
                'name': 'Expenses 242 ss- (test)',
                'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
                'tag_ids': [(6, 0, cls.env.ref('account.account_tag_operating').ids)],
                })

        cls.asset_category.write({'depreciation_account_id': cls.expense_242_account.id,
                                  'method_number': 2,
                                  })
        cls.analytic_tag_long_term_prepaid_expense = cls.env.ref('l10n_vn_c200.analytic_tag_long_term_prepaid_expense')
        cls.analytic_tag_short_term_prepaid_expense = cls.env.ref('l10n_vn_c200.analytic_tag_short_term_prepaid_expense')

    def test_01_depreciation_entry(self):
        """ Case 1:
        Input:
            - Set depreciation_account_id as 242 on asset category
            - Asset:
                - that have been link to asset category above
                - set analytic_tag_ids as analytic_tag_long_term_prepaid_expense
        Output:
            - All depreciation entries contains analytic_tag_long_term_prepaid_expense tag
        """
        asset = self._create_asset()
        asset.sudo().write({'analytic_tag_ids': [(6, 0, [self.analytic_tag_long_term_prepaid_expense.id])]})
        asset.action_compute_depreciation_board()

        # Click the confirm button to confirm the asset
        asset.validate()
        # Create and post all depreciation entries
        asset.depreciation_line_ids.create_move()
        # Check that all depreciation entries contains analytic_tag_long_term_prepaid_expense tag
        for line in asset.depreciation_line_ids.move_id.line_ids:
            self.assertEqual(line.analytic_tag_ids, self.analytic_tag_long_term_prepaid_expense)

    def test_02_depreciation_entry(self):
        """ Case 1.1:
        Input:
            - Set depreciation_account_id as 242 on asset category
            - Asset:
                - that have been link to asset category above
                - set analytic_tag_ids as analytic_tag_short_term_prepaid_expense
        Output:
            - All depreciation entries contains analytic_tag_short_term_prepaid_expense tag
        """
        asset = self._create_asset()
        asset.sudo().write({'analytic_tag_ids': [(6, 0, [self.analytic_tag_short_term_prepaid_expense.id])]})
        asset.action_compute_depreciation_board()

        # Click the confirm button to confirm the asset
        asset.validate()
        # Create and post all depreciation entries
        asset.depreciation_line_ids.create_move()
        # Check that all depreciation entries contains analytic_tag_short_term_prepaid_expense tag
        for line in asset.depreciation_line_ids.move_id.line_ids:
            self.assertEqual(line.analytic_tag_ids,
                             self.analytic_tag_short_term_prepaid_expense
                             )

    def test_03_depreciation_grouped_entry(self):
        """ Case 1.1:
        Input:
            - Set depreciation_account_id as 242 on asset category
            - Asset:
                - that have been link to asset category above
                - set analytic_tag_ids as analytic_tag_short_term_prepaid_expense
        Output:
            - All depreciation entries contains analytic_tag_short_term_prepaid_expense tag
        """
        asset = self._create_asset()
        asset.sudo().write({'analytic_tag_ids': [(6, 0, [self.analytic_tag_short_term_prepaid_expense.id])]})
        asset.action_compute_depreciation_board()

        # Click the confirm button to confirm the asset
        asset.validate()
        # Create and post all depreciation entries
        asset.depreciation_line_ids.create_grouped_move()
        # Check that all depreciation entries contains analytic_tag_short_term_prepaid_expense tag
        for line in asset.depreciation_line_ids.move_id.line_ids:
            self.assertEqual(line.analytic_tag_ids,
                             self.analytic_tag_short_term_prepaid_expense
                             )
