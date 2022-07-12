from odoo.exceptions import ValidationError
from odoo.tests.common import Form, tagged

from .payment_common import PaymentCommon


@tagged('post_install', '-at_install')
class TestPaymentFunctional(PaymentCommon):
    @classmethod
    def setUpClass(self, chart_template_ref=None):
        super(TestPaymentFunctional, self).setUpClass(chart_template_ref=chart_template_ref)

        self.so1 = self._create_so(self, partner=self.partner_a, price_unit=10000000)
        self.so2 = self._create_so(self, partner=self.partner_b, price_unit=20000000)

    def test_01_partner_on_payment(self):
        """Case 1:
        Input:
            - Payment:
                - link to SO1 that has been link partner a
                - partner as partner a
        Output:
            - When adding SO2 to payment, an error occur
        """
        payment_form = Form(self.env['account.payment'])
        payment_form.partner_type = 'customer'
        payment_form.payment_type = 'inbound'
        payment_form.sale_order_ids.add(self.so1)
        payment_form.journal_id = self.env.company.bank_journal_ids[:1]
        payment = payment_form.save()

        with self.assertRaises(ValidationError):
            payment.sale_order_ids = [(4, self.so2.id)]
