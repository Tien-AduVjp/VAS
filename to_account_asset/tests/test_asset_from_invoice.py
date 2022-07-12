from odoo.tests.common import tagged

from . import asset_common


@tagged('post_install', '-at_install')
class TestAssetFromInvoice(asset_common.AssetCommon):

    def test_01_asset_created_from_invoice(self):
        invoice = self.init_invoice('in_invoice')

        invoice.invoice_line_ids[0].asset_category_id = self.asset_category.id
        invoice.post()

        assets = self.env['account.asset.asset'].search([('invoice_line_id', '=', invoice.invoice_line_ids[0].id)])
        self.assertEqual(1, len(assets), "Asset has not been created from invoice!")
        self.assertEqual(assets.value, invoice.invoice_line_ids[0].balance, "Value on asset should be equal to the balance of invoice line")

        self.assertEqual(0,
                         self.env['account.asset.asset'].search_count([('invoice_line_id', '=', invoice.invoice_line_ids[1].id)]),
                         "Asset has been created from invoice!")
