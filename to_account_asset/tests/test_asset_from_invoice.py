from odoo.tests.common import tagged

from . import asset_common


@tagged('post_install', '-at_install')
class TestAssetFromInvoice(asset_common.AssetCommon):

    def test_01_asset_created_from_invoice(self):
        self.asset_category.open_asset = False
        products = self.product_a | self.product_b
        invoice = self.init_invoice('in_invoice', products=products)

        invoice.invoice_line_ids[0].asset_category_id = self.asset_category.id
        invoice._post()

        asset = self.env['account.asset.asset'].search([('invoice_line_id', '=', invoice.invoice_line_ids[0].id)], limit=1)
        self.assertTrue(asset)
        self.assertEqual(asset.value, invoice.invoice_line_ids[0].balance, "Value on asset should be equal to the balance of invoice line")

        self.assertEqual(0,
                         self.env['account.asset.asset'].search_count([('invoice_line_id', '=', invoice.invoice_line_ids[1].id)]),
                         "Asset has been created from invoice!")

        # Remove the asset when invoice is in cancel state
        invoice.button_cancel()
        self.assertFalse(asset.active)
        # Re-posted invoice => recreate a asset
        invoice.button_draft()
        invoice._post()
        asset = self.env['account.asset.asset'].search([('invoice_line_id', '=', invoice.invoice_line_ids[0].id)], limit=1)
        self.assertTrue(asset)
