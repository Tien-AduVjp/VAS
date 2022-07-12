from odoo.tests import tagged
from odoo.tests.common import TransactionCase, Form
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestPurchaseReceipt(TransactionCase):

    def setUp(self):
        super(TestPurchaseReceipt, self).setUp()

        # Create data for PO
        self.vendor = self.env.ref('base.res_partner_1')

        self.product = self.env['product.product'].create({
            'name': 'Product',
            'standard_price': 200.0,
            'list_price': 180.0,
            'type': 'consu',
            'purchase_method': 'purchase'
        })

        # Create data PO
        self.purchase_order = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
            'order_line': [(0, 0, {
                    'product_id': self.product.id,
                    'product_qty': 10
                })]
            })
        self.purchase_order.button_confirm()

    def _create_account_move_by_button(self, po):
        action = po.action_create_invoice()
        return self.env['account.move'].browse([action.get('res_id')])

    def create_receipt_by_button(self, po):
        return self._create_account_move_by_button(po.with_context(create_receipt=True))

    def create_invoice_by_button(self, po):
        return self._create_account_move_by_button(po.with_context(create_bill=True))

    def test_create_receipt_from_po(self):
        # Check type account_move created by button 'Create Receipt' on PO
        receipt = self.create_receipt_by_button(self.purchase_order)

        self.assertEqual(receipt.move_type, 'in_receipt', "Creating a Receipt from button on PO is failed!")

    def test_cant_create_invoice_if_receipt_exist(self):
        # Create receipt from PO
        self.create_receipt_by_button(self.purchase_order)
        self.purchase_order.invalidate_cache()

        # Button create invoice is hidden on PO
        self.assertGreater(self.purchase_order.count_receipt, 0, "Button create invoice on PO isn't hidden!")

        # Can't create invoice
        with self.assertRaises(ValidationError):
            self.create_invoice_by_button(self.purchase_order)

    def test_cant_create_receipt_if_invoice_exist(self):
        # Create invoice from PO
        self.create_invoice_by_button(self.purchase_order)
        self.purchase_order.invalidate_cache()

        # Button create receipt is hidden on PO
        self.assertGreater(self.purchase_order.count_invoice, 0, "Button create receipt on PO isn't hidden!")

        # Can't create receipt
        with self.assertRaises(ValidationError):
            self.create_receipt_by_button(self.purchase_order)

    def test_compute_billed_field_in_po(self):
        # Check value field Billed in PO after creating Receipt from button on PO
        self.create_receipt_by_button(self.purchase_order)

        # Export policy: on ordered quantity
        self.assertEqual(self.purchase_order.order_line.qty_invoiced, 10, "Billed field in PO compute fail when create receipt by button on PO!")
