from odoo.tests.common import tagged

from odoo.addons.to_account_asset.tests.asset_common import AssetCommon


@tagged('post_install', '-at_install')
class TestAssetFromInvoice(AssetCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.product_a = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'tracking': 'serial',
            'asset_category_id': cls.asset_category.id,
        })

    def test_01_asset_created_from_invoice(self):
        """No create the asset if Product Type as Stockrable."""
        products = self.product_a | self.product_b
        invoice = self.init_invoice('in_invoice', products=products)

        invoice.invoice_line_ids[0].write({'product_id': self.product_a.id,
                                           'asset_category_id': self.asset_category.id,
                                           })
        invoice._post()

        assets = self.env['account.asset.asset'].search([('invoice_line_id', '=', invoice.invoice_line_ids[0].id)])
        self.assertEqual(0, len(assets), "Asset has been created from invoice!")
