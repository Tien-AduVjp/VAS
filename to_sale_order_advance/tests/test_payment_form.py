from odoo.tests.common import Form, tagged

from .payment_common import PaymentCommon


@tagged('post_install', '-at_install')
class TestPaymentForm(PaymentCommon):
    @classmethod
    def setUpClass(self, chart_template_ref=None):
        super(TestPaymentForm, self).setUpClass(chart_template_ref=chart_template_ref)

        self.so1 = self._create_so(self, price_unit=10000000)
        self.so2 = self._create_so(self, price_unit=20000000)

    def test_01_change_partner_type_on_payment(self):
        """Case 1:
        Input:
            - Payment:
                - link to 2 SO
                - partner_type as customer
        Output:
            - When changing partner_type to vendor, SO on payment is set null
        """
        payment_form = Form(self.env['account.payment'])
        payment_form.partner_type = 'customer'
        payment_form.sale_order_ids.add(self.so1)
        payment_form.sale_order_ids.add(self.so2)
        self.assertEqual(payment_form.sale_order_ids._get_ids(), (self.so1 | self.so2).ids)

        payment_form.partner_type = 'supplier'
        self.assertEqual(payment_form.sale_order_ids._get_ids(), [])

    def test_02_change_partner_on_payment(self):
        """Case 2:
        Input:
            - Payment:
                - link to 2 SO that have been linked to partner_a
        Output:
            - When changing partner to partner_b, SO on payment is set null
        """
        payment_form = Form(self.env['account.payment'])
        payment_form.partner_type = 'customer'
        payment_form.sale_order_ids.add(self.so1)
        payment_form.sale_order_ids.add(self.so2)

        payment_form.partner_id = self.partner_b
        self.assertEqual(payment_form.sale_order_ids._get_ids(), [])

    def test_03_add_or_remove_so_on_payment(self):
        payment_form = Form(self.env['account.payment'])
        payment_form.partner_type = 'customer'
        """
        Case 3.1:
            Input:
                - add SO1 to payment
            Output: payment.amount == SO1.amount_total
        """
        payment_form.sale_order_ids.add(self.so1)
        self.assertEqual(payment_form.amount, self.so1.amount_total)

        """
        Case 3.2:
            Input:
                - add SO1, SO2 to payment
            Output: payment.amount == SO1.amount_total + SO2.amount_total
        """
        payment_form.sale_order_ids.add(self.so2)
        self.assertEqual(payment_form.amount, self.so1.amount_total + self.so2.amount_total)

        """
        Case 3.3:
            Input:
                - remove SO2 from payment
            Output: payment.amount == SO1.amount_total
        """
        payment_form.sale_order_ids.remove(id=self.so2.id)
        self.assertEqual(payment_form.amount, self.so1.amount_total)
