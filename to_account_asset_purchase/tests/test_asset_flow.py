from odoo.tests.common import tagged

from .asset_purchase_common import TestAssetPurchaseCommon


@tagged('post_install', '-at_install')
class TestAccountAssetFlow(TestAssetPurchaseCommon):

    def test_01_create_invoice_from_po(self):
        po = self._make_purchase_order(self.product_product, self.partner_b)
        invoice = self._create_invoice_from_po(po)

        self.assertEqual(invoice.invoice_line_ids.asset_category_id, self.asset_category)
