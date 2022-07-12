from odoo.exceptions import UserError
from odoo.tests import Form, tagged

from odoo.addons.account.tests.account_test_classes import AccountingTestCase
from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestPayment(TestCommon, AccountingTestCase):

    def test_compute_amount_with_payment_lines__receive_money(self):
        # Input: - payment type = Receive Money
        #        - add lines payment details with amount
        # Output: the value of amount is changed according to the sum of the payment details lines amount
        payment = self._create_payment('inbound')
        self.assertEqual(payment.amount, 35000)

    def test_compute_amount_with_payment_lines__send_money(self):
        # Input: - payment type = Send Money
        #        - add lines payment details with amount
        # Output: the value of amount is changed according to the sum of the payment details lines amount
        payment = self._create_payment('outbound')
        self.assertEqual(payment.amount, 35000)

    def test_payment_amount_not_equal_payment_lines_amount(self):
        # Input: - change amount payment other than payment line amount
        #        - Save
        # Output: UserError
        with self.assertRaises(UserError):
            payment = self._create_payment('inbound')
            payment.amount = 4300

    def test_confirm_payment_receive_money(self):
        # Input: - Payment type: Receive Money
        #        - add lines payment details with values:
        #           label = Label 01        amount = 30000.0        account_id = account_test
        #           label = Label 02        amount = 5000.0         account_id = account_test
        #        - Confirm
        # Output: - Journal Item Values:
        #           label = Label 02,         credit = 5000.0      debit = 0.0         account_id = account_test
        #           label = Label 01,         credit = 30000.0     debit = 0.0         account_id = account_test
        #           label = payment.name      credit = 0.0         debit = 35000.0
        payment = self._create_payment('inbound')
        payment.post()
        self.assertRecordValues(payment.move_line_ids, [
            {'account_id': self.account_test.id, 'credit': 5000.0, 'debit': 0.0, 'name': 'Label 02'},
            {'account_id': self.account_test.id, 'credit': 30000.0, 'debit': 0.0, 'name': 'Label 01'},
            {'account_id': self.journal_test.default_debit_account_id.id, 'credit': 0.0, 'debit': 35000.0, 'name': payment.name}
        ])

    def test_confirm_payment_send_money(self):
        # Input: - Payment type: Send Money
        #        - add lines payment details with values:
        #           label = Label 01        amount = 30000.0        account_id = account_test
        #           label = Label 02        amount = 5000.0         account_id = account_test
        #        - Confirm
        # Output: - Journal Item Values:
        #           label = Label 02         debit = 5000.0      credit = 0.0         account_id = account_test
        #           label = Label 01         debit = 30000.0     credit = 0.0         account_id = account_test
        #           label = payment name     debit = 0.0         credit = 35000.0
        payment = self._create_payment('outbound')
        payment.post()
        self.assertRecordValues(payment.move_line_ids, [
            {'account_id': self.account_test.id, 'debit': 5000.0, 'credit': 0.0, 'name': 'Label 02'},
            {'account_id': self.account_test.id, 'debit': 30000.0, 'credit': 0.0, 'name': 'Label 01'},
            {'account_id': self.journal_test.default_debit_account_id.id, 'debit': 0.0, 'credit': 35000.0, 'name': payment.name}
        ])

    def _create_account_move(self, move_type):
        demo_partner = self.env.ref('base.partner_demo')
        account_move = self.env['account.move'].create({
            'partner_id': demo_partner.id,
            'type': move_type,
            'invoice_line_ids': [(0, 0, {'quantity': 1, 'price_unit': 40000, 'tax_ids': False})]
        })
        account_move.action_post()
        return account_move

    def _test_suggest_lines(self, payment_type, move):
        form = Form(self.env['account.payment'])
        form.payment_type = payment_type
        form.partner_type = 'customer'
        form.partner_id = self.env.ref('base.partner_demo')
        form.journal_id = self.journal_test
        form.suggest_lines = True
        self.assertEqual(form.account_payment_line_ids._records[0]['amount'], 40000)
        self.assertEqual(form.amount, form.account_payment_line_ids._records[0]['amount'])

    def test_suggest_lines_payment_receive_money(self):
        # Input: Payment type: receive money => add partner => check suggest lines
        # Output: detailed payment lines are added
        invoice = self._create_account_move('out_invoice')
        self._test_suggest_lines('inbound', invoice)

    def test_suggest_lines_payment_send_money(self):
        # Input: Payment type: send money => add partner => check suggest lines
        # Output: detailed payment lines are added
        bill = self._create_account_move('in_invoice')
        self._test_suggest_lines('outbound', bill)
