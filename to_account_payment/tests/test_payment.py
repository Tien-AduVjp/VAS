from odoo.exceptions import UserError
from odoo.tests import Form, tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestPayment(TestCommon):

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
        #           label =                   credit = 0.0         debit = 35000.0
        payment = self._create_payment('inbound')
        payment.action_post()
        self.assertRecordValues(payment.move_id.line_ids, [
            {'account_id': self.journal_test.payment_debit_account_id.id, 'credit': 0.0, 'debit': 35000.0},
            {'account_id': self.account_test.id, 'credit': 30000.0, 'debit': 0.0, 'name': 'Label 01'},
            {'account_id': self.account_test.id, 'credit': 5000.0, 'debit': 0.0, 'name': 'Label 02'},
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
        #           label =                  debit = 0.0         credit = 35000.0
        payment = self._create_payment('outbound')
        payment.action_post()
        self.assertRecordValues(payment.move_id.line_ids, [
            {'account_id': self.journal_test.payment_credit_account_id.id, 'debit': 0.0, 'credit': 35000.0},
            {'account_id': self.account_test.id, 'debit': 30000.0, 'credit': 0.0, 'name': 'Label 01'},
            {'account_id': self.account_test.id, 'debit': 5000.0, 'credit': 0.0, 'name': 'Label 02'},
        ])

    def _create_account_move(self, move_type):
        demo_partner = self.env.ref('base.partner_demo')
        account_move = self.env['account.move'].create({
            'invoice_date': '2021-09-30',
            'partner_id': demo_partner.id,
            'move_type': move_type,
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

    def test_change_journal_in_payment(self):
        journal_test_1 = self.env['account.journal'].create({
            'name': 'CASH JOURNAL',
            'code': 'CASHTEST',
            'type': 'cash',
        })
        payment = self._create_payment('inbound')
        payment.journal_id = journal_test_1
        self.assertEqual(payment.journal_id, journal_test_1)
        
    def test_reconcile_suggested_payment_lines(self):
        self._create_account_move('in_invoice')
        form = Form(self.env['account.payment'])
        form.payment_type = 'outbound'
        form.partner_type = 'customer'
        form.partner_id = self.env.ref('base.partner_demo')
        form.journal_id = self.journal_test
        form.suggest_lines = True
        payment = form.save()
        payment.action_post()
        self.assertTrue(payment.account_payment_line_ids[0].move_line_ids[0].reconciled)
        
    def test_unreconcile_suggested_payment_lines(self):    
        self._create_account_move('in_invoice')
        form = Form(self.env['account.payment'])
        form.payment_type = 'outbound'
        form.partner_type = 'customer'
        form.partner_id = self.env.ref('base.partner_demo')
        form.journal_id = self.journal_test
        form.suggest_lines = True
        form.account_payment_line_ids._records[0]['amount'] = 30000
        form.amount = 30000
        payment = form.save()
        payment.action_post()
        self.assertFalse(payment.account_payment_line_ids[0].move_line_ids[0].reconciled)

    def test_edit_to_add_extra_payment_line(self):
        payment = self._create_payment('inbound')
        try:
            with Form(payment) as payment_form:
                with payment_form.account_payment_line_ids.new() as line:
                    line.name = 'Label 03'
                    line.account_id = self.account_test
                    line.amount = 40000
        except Exception:
            self.fail("Could not create extra account payment line")
