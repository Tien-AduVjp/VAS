from odoo.tests.common import SavepointCase, tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestToPaymentTransactionProtection(SavepointCase):

    def setUp(self):
        super(TestToPaymentTransactionProtection, self).setUp()
        bank_journal_usd = self.env['account.journal'].create({
            'name': 'Bank US',
            'type': 'bank',
            'code': 'BNK68',
            'currency_id': self.env.ref('base.USD').id
        })
        inbound_payment_method = self.env['account.payment.method'].create({
            'name': 'inbound',
            'code': 'IN',
            'payment_type': 'inbound',
        })
        self.transaction = self.env['payment.transaction'].create({
            'amount': 1.95,
            'acquirer_id': self.env.ref('payment.payment_acquirer_buckaroo').id,
            'currency_id': self.env.ref('base.USD').id,
            'reference': 'test_ref_',
            'partner_name': 'Norbert Buyer'
        })
        self.payment = self.env['account.payment'].create({
            'payment_method_id': inbound_payment_method.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'journal_id': bank_journal_usd.id,
            'date': '2018-06-04',
            'amount': 666,
        })

    def test_01_unlink_payment_transaction(self):
        # case 1:
        self.transaction.payment_id = self.payment
        with self.assertRaises(UserError):
            self.transaction.unlink()

    def test_02_unlink_payment_transaction(self):
        # case 2:
        self.transaction.payment_id = self.payment
        self.transaction.with_context(force_delete_transaction=True).unlink()
        self.assertFalse(self.transaction.exists())

    def test_03_unlink_payment_transaction(self):
        # case 3:
        self.transaction.unlink()
        self.assertFalse(self.transaction.exists())
