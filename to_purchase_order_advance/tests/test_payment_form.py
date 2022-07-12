from odoo.tests.common import Form, tagged

from .payment_common import PaymentCommon


@tagged('post_install', '-at_install')
class TestPaymentForm(PaymentCommon):
    @classmethod
    def setUpClass(self, chart_template_ref=None):
        super(TestPaymentForm, self).setUpClass(chart_template_ref=chart_template_ref)

        self.po1 = self._create_po(self, price_unit=10000000)
        self.po2 = self._create_po(self, price_unit=20000000)

    def test_01_change_partner_type_on_payment(self):
        """Case 1:
        Input:
            - Payment:
                - link to 2 PO
                - partner_type as vendor
        Output:
            - When changing partner_type to customer, PO on payment is set null
        """
        payment_form = Form(self.env['account.payment'])
        payment_form.partner_type = 'supplier'
        payment_form.purchase_order_ids.add(self.po1)
        payment_form.purchase_order_ids.add(self.po2)
        self.assertEqual(payment_form.purchase_order_ids._get_ids(), (self.po1 | self.po2).ids)

        payment_form.partner_type = 'customer'
        self.assertEqual(payment_form.purchase_order_ids._get_ids(), [])

    def test_02_change_partner_on_payment(self):
        """Case 2:
        Input:
            - Payment:
                - link to 2 PO that have been linked to partner_a
        Output:
            - When changing partner to partner_b, PO on payment is set null
        """
        payment_form = Form(self.env['account.payment'])
        payment_form.partner_type = 'supplier'
        payment_form.purchase_order_ids.add(self.po1)
        payment_form.purchase_order_ids.add(self.po2)

        payment_form.partner_id = self.partner_b
        self.assertEqual(payment_form.purchase_order_ids._get_ids(), [])

    def test_03_add_or_remove_po_on_payment(self):
        payment_form = Form(self.env['account.payment'])
        payment_form.partner_type = 'supplier'
        """
        Case 3.1:
            Input:
                - add PO1 to payment
            Output: payment.amount == PO1.amount_total
        """
        payment_form.purchase_order_ids.add(self.po1)
        self.assertEqual(payment_form.amount, self.po1.amount_total)

        """
        Case 3.2:
            Input:
                - add PO1, PO2 to payment
            Output: payment.amount == PO1.amount_total + PO2.amount_total
        """
        payment_form.purchase_order_ids.add(self.po2)
        self.assertEqual(payment_form.amount, self.po1.amount_total + self.po2.amount_total)

        """
        Case 3.3:
            Input:
                - remove PO2 from payment
            Output: payment.amount == PO1.amount_total
        """
        payment_form.purchase_order_ids.remove(id=self.po2.id)
        self.assertEqual(payment_form.amount, self.po1.amount_total)
