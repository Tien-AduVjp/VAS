from odoo.tests.common import Form, tagged

from odoo.addons.to_account_asset.tests.asset_common import AssetCommon


@tagged('post_install', '-at_install')
class TestFunctional(AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref='l10n_vn.vn_template')

        cls.product_a.write({'asset_category_id': cls.asset_category.id})
        cls.product_b.write({'asset_category_id': False})

    def test_01_create_invoice_from_so(self):
        """Case 1:
        Input:
            - set asset category on product A
            - SO that have SO line of product A
        Action:
            - Create invoice from SO
        Output:
            - Invoice line contains fixed_assets tag
        """
        so = self._create_so()
        so.action_confirm()

        move = so._create_invoices()
        self.assertEqual(move.invoice_line_ids.analytic_tag_ids,
                         self.env.ref('l10n_vn_c200.analytic_tag_fixed_assets')
                         )

    def test_02_create_invoice_from_so(self):
        """Case 2:
        Input:
            - no set asset category on product B
            - SO that have SO line of product b
        Action:
            - Create invoice from SO
        Output:
            - Invoice line doesn't contains fixed_assets tag
        """
        so = self._create_so(product=self.product_b)
        so.action_confirm()

        move = so._create_invoices()
        self.assertFalse(move.invoice_line_ids.analytic_tag_ids)

    def _create_so(self, partner=False, product=False, price_unit=100000, qty=1):
        so = Form(self.env['sale.order'])
        so.partner_id = partner or self.partner_a
        with so.order_line.new() as so_line:
            so_line.product_id = product or self.product_a
            so_line.product_uom_qty = qty
            so_line.price_unit = price_unit
        so = so.save()
        return so
