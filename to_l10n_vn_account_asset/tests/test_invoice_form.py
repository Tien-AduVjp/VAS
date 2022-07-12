from odoo import fields
from odoo.tests.common import Form, tagged

from odoo.addons.to_account_asset.tests.asset_common import AssetCommon


@tagged('post_install', '-at_install')
class TestInvoiceForm(AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref='l10n_vn.vn_template')

        cls.env.user.write({'groups_id': [
            (4, cls.env.ref('analytic.group_analytic_tags').id),
            (4, cls.env.ref('analytic.group_analytic_accounting').id),
            ]})

        cls.asset_category.write({
            'analytic_tag_ids': [(6, 0, [cls.env.ref('l10n_vn_common.account_analytic_tag_fixed_assets').id])]
            })
        cls.product_a.write({'asset_category_id': cls.asset_category.id})
        cls.product_b.write({'asset_category_id': False})

    def test_01_change_product_on_invoice(self):
        """Case 2:
        Input:
            - Set asset category on product A
            - No set asset category on product B

        Action:
            - Create vendor invoice that have contains invoice line of product A
        Output:
            - Invoice line of product A contains analytic_tag_fixed_assets tag
        Then, change product on invoice line to product B
        Output:
            - Analytic_tag_fixed_assets tag is removed on invoice line
        """
        move_form = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.invoice_date = fields.Date.from_string('2019-01-01')
        move_form.partner_id = self.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_a
            self.assertEqual(line_form.analytic_tag_ids._get_ids(), self.asset_category.analytic_tag_ids.ids)
            # Change product on invoice line to product B
            # Tags are not changed
            line_form.product_id = self.product_b
            self.assertEqual(line_form.analytic_tag_ids._get_ids(), self.asset_category.analytic_tag_ids.ids)

    def test_02_change_asset_category_on_invoice(self):
        """Case 3:
        Input:
            - Set asset category on invoice line
        Output:
            - Invoice line contains analytic_tag_fixed_assets tag
        Then, remove asset category on invoice line
        Output:
            - Analytic_tag_fixed_assets tag is removed on invoice line
        """
        move_form = Form(self.env['account.move'].with_context(default_move_type='in_invoice'))
        move_form.invoice_date = fields.Date.from_string('2019-01-01')
        move_form.partner_id = self.partner_a
        with move_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_b
            line_form.asset_category_id = self.asset_category
            self.assertEqual(line_form.analytic_tag_ids._get_ids(), self.asset_category.analytic_tag_ids.ids)
            # Remove asset category on invoice line
            # Tags are not changed
            line_form.asset_category_id = self.env['account.asset.category']
            self.assertEqual(line_form.analytic_tag_ids._get_ids(), self.asset_category.analytic_tag_ids.ids)
