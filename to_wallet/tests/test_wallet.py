import datetime

from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged
from .test_common import TestWalletCommon


@tagged('post_install', '-at_install')
class TestWallet(TestWalletCommon):

    def test_create_non_wallet_payment(self):
        payment = self.create_payment(amount=100000, wallet=False)
        receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(receivable_move_line, [
            {
                'wallet': False,
                'wallet_amount': 0,
                'wallet_amount_currency': 0,
                'wallet_amount_residual': 0,
                'wallet_amount_residual_currency': 0,
                'non_wallet_amount_residual':-100000,
                'non_wallet_amount_residual_currency': -100000
            }
        ])
        self.assertItemsEqual(self.partner.commercial_partner_id.mapped('wallet_ids'), [])

    def test_create_wallet_payment(self):
        payment = self.create_payment(amount=100000, wallet=True)
        receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(receivable_move_line, [
            {
                'wallet': True,
                'wallet_amount': 100000,
                'wallet_amount_currency': 100000,
                'wallet_amount_residual':-100000,
                'wallet_amount_residual_currency': -100000,
                'non_wallet_amount_residual': 0,
                'non_wallet_amount_residual_currency': 0
            }
        ])
        self.assertRecordValues(self.partner.commercial_partner_id.wallet_ids, [
            {
                'currency_id': self.currency_usd.id,
                'amount': 100000
            }
        ])

    def test_wallet_payment_invalid_wallet_amount(self):
        self.assertRaises(
            ValidationError,
            self.create_payment, amount=100000, wallet=True, wallet_amount=-50000
            )
        self.assertRaises(
            ValidationError,
            self.create_payment, amount=100000, wallet=True, wallet_amount=100001
            )
        self.assertRaises(
            ValidationError,
            self.create_payment, amount=100000.00, wallet=True, wallet_amount=100000.01, currency_id=self.currency_usd.id
            )

    def test_create_wallet_payment_currency(self):
        payment = self.create_payment(amount=100, wallet=True, currency_id=self.currency_eur.id)
        receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(receivable_move_line, [
            {
                'wallet': True,
                'wallet_amount': 110,
                'wallet_amount_currency': 100,
                'wallet_amount_residual': -110,
                'wallet_amount_residual_currency': -100,
                'non_wallet_amount_residual': 0,
                'non_wallet_amount_residual_currency': 0
            }
        ])
        self.assertRecordValues(self.partner.commercial_partner_id.wallet_ids, [
            {
                'currency_id': self.currency_eur.id,
                'amount': 100
            }
        ])

    def test_create_mix_wallet_payment(self):
        payment = self.create_payment(amount=300000, wallet=True, wallet_amount=200000)
        receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(receivable_move_line, [
            {
                'wallet': True,
                'wallet_amount': 200000,
                'wallet_amount_currency': 200000,
                'wallet_amount_residual':-200000,
                'wallet_amount_residual_currency': -200000,
                'non_wallet_amount_residual':-100000,
                'non_wallet_amount_residual_currency': -100000
            }
        ])
        self.assertRecordValues(self.partner.commercial_partner_id.wallet_ids, [
            {
                'currency_id': self.currency_usd.id,
                'amount': 200000
            }
        ])

    def test_create_non_wallet_invoice(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000
            }])
        receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(receivable_move_line, [
            {
                'wallet': False,
                'wallet_amount': 0,
                'wallet_amount_currency': 0,
                'wallet_amount_residual': 0,
                'wallet_amount_residual_currency': 0,
                'non_wallet_amount_residual': 100000,
                'non_wallet_amount_residual_currency': 100000
            }
        ])

    def test_create_wallet_invoice(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }])
        receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(receivable_move_line, [
            {
                'wallet': True,
                'wallet_amount':-100000,
                'wallet_amount_currency': -100000,
                'wallet_amount_residual': 100000,
                'wallet_amount_residual_currency': 100000,
                'non_wallet_amount_residual': 0,
                'non_wallet_amount_residual_currency': 0
            }
        ])

    def test_create_wallet_invoice_currency(self):
        invoice = self.create_invoice(
            custom_vals={
                'currency_id': self.currency_eur.id
            },
            custom_line_vals_list=[{
                'price_unit': 100,
                'wallet': True
            }])
        receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(receivable_move_line, [
            {
                'wallet': True,
                'wallet_amount': -110,
                'wallet_amount_currency': -100,
                'wallet_amount_residual': 110,
                'wallet_amount_residual_currency': 100,
                'non_wallet_amount_residual': 0,
                'non_wallet_amount_residual_currency': 0
            }
        ])

    def test_create_mix_wallet_invoice(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
            }, {
                'price_unit': 200000,
                'wallet': True
            }])
        receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(receivable_move_line, [
            {
                'wallet': True,
                'wallet_amount':-200000,
                'wallet_amount_currency': -200000.0,
                'wallet_amount_residual': 200000,
                'wallet_amount_residual_currency': 200000.0,
                'non_wallet_amount_residual': 100000,
                'non_wallet_amount_residual_currency': 100000
            }
        ])

    def test_create_mix_wallet_invoice_form(self):
        invoice = self.create_invoice(post_invoice=False)
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product
            line.price_unit = 200000
            line.account_id = self.account_income
            line.wallet = True
            line.tax_ids.clear()
        with invoice_form.invoice_line_ids.new() as line:
            line.product_id = self.product
            line.account_id = self.account_income
            line.price_unit = 100000
            line.tax_ids.clear()
        invoice_form.save()
        invoice.action_post()
        self.assertRecordValues(invoice.line_ids, [
            {
                'wallet': True,
                'wallet_amount': -200000,
                'wallet_amount_currency': -200000.0,
                'wallet_amount_residual': 200000,
                'wallet_amount_residual_currency': 200000,
                'non_wallet_amount_residual': 100000,
                'non_wallet_amount_residual_currency': 100000.0
            },
            {
                'wallet': True,
                'wallet_amount': 200000,
                'wallet_amount_currency': 200000,
                'wallet_amount_residual': 0,
                'wallet_amount_residual_currency': 0,
                'non_wallet_amount_residual': 0,
                'non_wallet_amount_residual_currency': 0
            },
            {
                'wallet': False,
                'wallet_amount': 0,
                'wallet_amount_currency': 0,
                'wallet_amount_residual': 0,
                'wallet_amount_residual_currency': 0,
                'non_wallet_amount_residual': 0,
                'non_wallet_amount_residual_currency': 0
            },
        ])

    def test_reconcile_non_wallet_invoice_with_non_wallet_payment(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 200000
            }])
        payment = self.create_payment(amount=100000, wallet=False)
        self.reconcile_payment_vs_invoice(payment, invoice)
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 100000,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 100000,
            'non_wallet_amount_residual_currency': 100000.0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_wallet_invoice_with_lesser_wallet_payment(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 200000,
                'wallet': True
            }])
        payment = self.create_payment(amount=100000, wallet=True)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'partial')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 100000,
            'wallet_amount_residual': 100000,
            'wallet_amount_residual_currency': 100000,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_wallet_invoice_with_greater_wallet_payment(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }])
        payment = self.create_payment(amount=200000, wallet=True)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual':-100000,
            'wallet_amount_residual':-100000,
            'wallet_amount_residual_currency': -100000,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 100000)

    def test_reconcile_non_wallet_invoice_with_mix_wallet_payment(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000
            }])
        payment = self.create_payment(amount=100000, wallet=True, wallet_amount=50000)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'partial')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 50000,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 50000,
            'non_wallet_amount_residual_currency': 50000
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual':-50000,
            'wallet_amount_residual':-50000,
            'wallet_amount_residual_currency': -50000,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 50000)

    def test_reconcile_wallet_invoice_with_mix_wallet_payment(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }])
        payment = self.create_payment(amount=100000, wallet=True, wallet_amount=50000)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'partial')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 50000,
            'wallet_amount_residual': 50000,
            'wallet_amount_residual_currency': 50000,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual':-50000,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual':-50000,
            'non_wallet_amount_residual_currency': -50000
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_mix_wallet_invoice_with_wallet_payment(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000
            }, {
                'price_unit': 100000,
                'wallet': True
            }])
        payment = self.create_payment(amount=150000, wallet=True)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'partial')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 100000,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 100000,
            'non_wallet_amount_residual_currency': 100000
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual':-50000,
            'wallet_amount_residual':-50000,
            'wallet_amount_residual_currency': -50000,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 50000)

    def test_reconcile_non_wallet_invoice_with_wallet_payment(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000
            }])
        payment = self.create_payment(amount=100000, wallet=True)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'not_paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 100000,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 100000,
            'non_wallet_amount_residual_currency': 100000
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual':-100000,
            'wallet_amount_residual':-100000,
            'wallet_amount_residual_currency': -100000,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 100000)

    def test_reconcile_wallet_invoice_with_non_wallet_payment(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }])
        payment = self.create_payment(amount=100000, wallet=False)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'not_paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 100000,
            'wallet_amount_residual': 100000,
            'wallet_amount_residual_currency': 100000,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual':-100000,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual':-100000,
            'non_wallet_amount_residual_currency': -100000
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_1(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }, {
                'price_unit': 100000,
            }])
        payment = self.create_payment(amount=160000, wallet=True, wallet_amount=70000)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'partial')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 40000,
            'wallet_amount_residual': 30000,
            'wallet_amount_residual_currency': 30000,
            'non_wallet_amount_residual': 10000,
            'non_wallet_amount_residual_currency': 10000
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_2(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }, {
                'price_unit': 100000,
            }])
        payment = self.create_payment(amount=160000, wallet=True, wallet_amount=60000)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'partial')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 40000,
            'wallet_amount_residual': 40000,
            'wallet_amount_residual_currency': 40000,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_3(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }, {
                'price_unit': 100000,
            }])
        payment = self.create_payment(amount=160000, wallet=True, wallet_amount=50000)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'partial')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 50000,
            'wallet_amount_residual': 50000,
            'wallet_amount_residual_currency': 50000,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual':-10000,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual':-10000,
            'non_wallet_amount_residual_currency': -10000
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_4(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }, {
                'price_unit': 100000,
            }])
        payment = self.create_payment(amount=200000, wallet=True, wallet_amount=100000)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_5(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }, {
                'price_unit': 100000,
            }])
        payment = self.create_payment(amount=300000, wallet=True, wallet_amount=150000)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual':-100000,
            'wallet_amount_residual':-50000,
            'wallet_amount_residual_currency': -50000,
            'non_wallet_amount_residual':-50000,
            'non_wallet_amount_residual_currency': -50000
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 50000)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_6(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }, {
                'price_unit': 100000,
            }])
        payment = self.create_payment(amount=160000, wallet=True, wallet_amount=80000)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'partial')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 40000,
            'wallet_amount_residual': 20000,
            'wallet_amount_residual_currency': 20000,
            'non_wallet_amount_residual': 20000,
            'non_wallet_amount_residual_currency': 20000
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

        payment2 = self.create_payment(amount=50000, wallet=True, wallet_amount=25000)
        self.reconcile_payment_vs_invoice(payment2, invoice)
        self.assertEqual(invoice.payment_state, 'paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment2.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual':-10000,
            'wallet_amount_residual':-5000,
            'wallet_amount_residual_currency': -5000,
            'non_wallet_amount_residual':-5000,
            'non_wallet_amount_residual_currency': -5000
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 5000)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_7(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000
            }])
        invoice2 = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }])
        invoice3 = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }, {
                'price_unit': 100000,
            }])
        payment = self.create_payment(amount=100000, wallet=False)
        payment2 = self.create_payment(amount=100000, wallet=True)
        payment3 = self.create_payment(amount=200000, wallet=True, wallet_amount=100000)
        payment_receivable_move_lines = (payment + payment2 + payment3).mapped('line_ids').filtered(
            lambda r: r.account_id.internal_type == 'receivable')
        # quick way to register payment of all invoice
        lines = payment_receivable_move_lines + (invoice + invoice2 + invoice3).line_ids.filtered(
            lambda line: line.account_id == payment_receivable_move_lines[0].account_id and not line.reconciled)
        lines.reconcile()
        self.assertEqual(invoice.payment_state, 'paid')
        self.assertEqual(invoice2.payment_state, 'paid')
        self.assertEqual(invoice3.payment_state, 'paid')
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_8(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000
            }])
        invoice2 = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }])
        invoice3 = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }, {
                'price_unit': 100000,
            }])
        payment = self.create_payment(amount=80000, wallet=False)
        payment2 = self.create_payment(amount=100000, wallet=True)
        payment3 = self.create_payment(amount=220000, wallet=True, wallet_amount=100000)
        payment_receivable_move_lines = (payment + payment2 + payment3).line_ids.filtered(
            lambda r: r.account_id.internal_type == 'receivable')

        # quick way to register payment of all invoice
        lines = payment_receivable_move_lines + (invoice + invoice2 + invoice3).line_ids.filtered(
            lambda line: line.account_id == payment_receivable_move_lines[0].account_id and not line.reconciled)
        lines.reconcile()

        self.assertEqual(invoice.payment_state, 'paid')
        self.assertEqual(invoice2.payment_state, 'paid')
        self.assertEqual(invoice3.payment_state, 'paid')
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_currency_1(self):
        invoice = self.create_invoice(
            custom_vals={
                'currency_id': self.currency_eur.id
            },
            custom_line_vals_list=[{
                'price_unit': 100,
                'wallet': True
            }, {
                'price_unit': 100,
            }])
        payment = self.create_payment(amount=160, wallet=True, wallet_amount=70, currency_id=self.currency_eur.id)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'partial')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 44,
            'wallet_amount_residual': 33,
            'wallet_amount_residual_currency': 30,
            'non_wallet_amount_residual': 11,
            'non_wallet_amount_residual_currency': 10
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 0)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_currency_2(self):
        invoice = self.create_invoice(
            custom_vals={
                'currency_id': self.currency_eur.id
            },
            custom_line_vals_list=[{
                'price_unit': 100,
                'wallet': True
            }, {
                'price_unit': 100,
            }])
        payment = self.create_payment(amount=250, wallet=True, wallet_amount=125)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': -30,
            'wallet_amount_residual': -15,
            'wallet_amount_residual_currency': -15,
            'non_wallet_amount_residual': -15,
            'non_wallet_amount_residual_currency': -15
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 15)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_currency_3(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 55,
                'wallet': True
            }, {
                'price_unit': 55,
            }])
        payment = self.create_payment(amount=120, wallet=True, wallet_amount=70, currency_id=self.currency_eur.id)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': -22,
            'wallet_amount_residual': -22,
            'wallet_amount_residual_currency': -20,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 20)

    def test_reconcile_mix_wallet_invoice_with_mix_wallet_payment_currency_4(self):
        invoice = self.create_invoice(
            custom_vals={
                'currency_id': self.currency_eur.id
            },
            custom_line_vals_list=[{
                'price_unit': 100,
                'wallet': True
            }, {
                'price_unit': 100,
            }])
        payment = self.create_payment(amount=6000000, wallet=True, wallet_amount=3000000, currency_id=self.currency_vnd.id)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': -44,
            'wallet_amount_residual': -22,
            'wallet_amount_residual_currency': -500000,
            'non_wallet_amount_residual': -22,
            'non_wallet_amount_residual_currency': -500000
        }])
        self.assertEqual(self.partner.commercial_partner_id.wallet_ids.amount, 500000)

    def test_full_reconcile(self):
        invoice = self.create_invoice(
            custom_line_vals_list=[{
                'price_unit': 100000,
                'wallet': True
            }])
        payment = self.create_payment(amount=100000, wallet=True)
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertTrue(invoice_receivable_move_line.full_reconcile_id)
        self.assertTrue(payment_receivable_move_line.full_reconcile_id)
        self.assertEqual(invoice_receivable_move_line.full_reconcile_id, payment_receivable_move_line.full_reconcile_id)

    def test_full_reconcile_exchange_rate(self):
        invoice = self.create_invoice(
            custom_vals={
                'currency_id': self.currency_eur.id
            },
            custom_line_vals_list=[{
                'price_unit': 100,
                'wallet': True
            }])
        payment = self.create_payment(amount=100, wallet=True, currency_id=self.currency_eur.id,
                                      date=datetime.date(self.current_year + 1, 2, 1))
        self.reconcile_payment_vs_invoice(payment, invoice)
        self.assertEqual(invoice.payment_state, 'paid')
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        payment_receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(payment_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])
        self.assertTrue(invoice_receivable_move_line.full_reconcile_id)
        self.assertTrue(payment_receivable_move_line.full_reconcile_id)
        self.assertEqual(invoice_receivable_move_line.full_reconcile_id, payment_receivable_move_line.full_reconcile_id)
        exchange_line = invoice_receivable_move_line.full_reconcile_id.reconciled_line_ids.filtered(
            lambda r: r.journal_id == r.company_id.currency_exchange_journal_id)
        self.assertRecordValues(exchange_line, [{
            'debit': 10,
            'credit': 0
        }])

    def test_mix_wallet_invoice_not_full_reconcile(self):
        invoice = self.create_invoice(custom_line_vals_list=[{
            'price_unit': 100000,
            'wallet': True
        }, {
            'price_unit': 200000,
            'wallet': False
        }])
        payment = self.create_payment(amount=300000, wallet=True)
        self.reconcile_payment_vs_invoice(payment, invoice)
        # we expect no full reconcile here
        self.assertTrue(all(not line.full_reconcile_id for line in payment.line_ids))

        invoice2 = self.create_invoice(custom_line_vals_list=[{
            'price_unit': 200000,
            'wallet': True
        }])
        (invoice2.line_ids + payment.line_ids).filtered(lambda l: l.account_id.internal_type == 'receivable').reconcile()
        # we expect the invoice2 is paid but still no full reconcile here
        self.assertTrue(invoice2.payment_state == 'paid')
        self.assertTrue(all(not line.full_reconcile_id for line in payment.line_ids))

        payment2 = self.create_payment(amount=200000, wallet=False)
        self.reconcile_payment_vs_invoice(payment2, invoice)

        receivable_lines = ((payment + payment2).line_ids + (invoice + invoice2).line_ids)\
            .filtered(lambda l: l.account_id.internal_type == 'receivable')
        # we expect the invoice is paid and there is a single full reconcile here
        self.assertTrue(invoice.payment_state == 'paid')
        self.assertTrue(all(line.full_reconcile_id for line in receivable_lines))
        self.assertTrue(len(receivable_lines.mapped('full_reconcile_id')) == 1)

    def test_reconcile_invoice_with_multiple_payments(self):
        payment1 = self.create_payment(amount=1956014, wallet=True)
        payment1_receivable_move_lines = payment1.line_ids.filtered(lambda line: line.account_id.internal_type == 'receivable')
        payment2 = self.create_payment(amount=1999000, wallet=True)
        payment2_receivable_move_lines = payment2.line_ids.filtered(lambda line: line.account_id.internal_type == 'receivable')
        invoice = self.create_invoice(custom_line_vals_list=[{
            'price_unit': 1999000,
            'wallet': True
        }])
        invoice_payable_lines = invoice.line_ids.filtered(lambda line: line.account_id.internal_type == 'receivable')
        (invoice_payable_lines + payment1_receivable_move_lines + payment2_receivable_move_lines).reconcile()
        self.assertRecordValues(invoice, [{'payment_state': 'paid'}])
        self.assertRecordValues(payment1_receivable_move_lines, [{'wallet_amount_residual': 0}])
        self.assertRecordValues(payment1_receivable_move_lines.matched_debit_ids, [{'amount': 1956014}])
        self.assertRecordValues(payment2_receivable_move_lines, [{'wallet_amount_residual':-1956014}])
        self.assertRecordValues(payment2_receivable_move_lines.matched_debit_ids, [{'amount': 42986}])

    def test_reconcile_multiple_invoices_with_multiple_payments(self):
        payment1 = self.create_payment(amount=1000000, wallet=True)
        payment1_receivable_move_lines = payment1.line_ids.filtered(lambda line: line.account_id.internal_type == 'receivable')
        invoice1 = self.create_invoice(custom_line_vals_list=[{
            'price_unit': 100000,
            'wallet': True
        }])
        invoice1_payable_lines = invoice1.line_ids.filtered(lambda line: line.account_id.internal_type == 'receivable')
        (invoice1_payable_lines + payment1_receivable_move_lines).reconcile()
        self.assertRecordValues(invoice1, [{'payment_state': 'paid'}])

        payment2 = self.create_payment(amount=2000000, wallet=True)
        payment2_receivable_move_lines = payment2.line_ids.filtered(lambda line: line.account_id.internal_type == 'receivable')
        invoice2 = self.create_invoice(custom_line_vals_list=[{
            'price_unit': 1999000,
            'wallet': True
        }])
        invoice2_payable_lines = invoice2.line_ids.filtered(lambda line: line.account_id.internal_type == 'receivable')
        (invoice2_payable_lines + payment1_receivable_move_lines + payment2_receivable_move_lines).reconcile()
        self.assertRecordValues(invoice2, [{'payment_state': 'paid'}])
        self.assertRecordValues(payment1_receivable_move_lines, [{'wallet_amount_residual': 0}])
        self.assertRecordValues(payment1_receivable_move_lines.matched_debit_ids, [{'amount': 100000}, {'amount': 900000}])
        self.assertRecordValues(payment2_receivable_move_lines, [{'wallet_amount_residual':-901000}])
        self.assertRecordValues(payment2_receivable_move_lines.matched_debit_ids, [{'amount': 1099000}])

    def _create_manual_journal_entry(self, amount, wallet_total):
        entry = self.env['account.move'].create({
            'wallet_total': wallet_total,
            'line_ids': [
                (0, 0, {
                    'account_id': self.account_112.id,
                    'partner_id': self.partner.id,
                    'debit': amount,
                    'credit': 0.0
                }),
                (0, 0, {
                    'account_id': self.account_131.id,
                    'partner_id': self.partner.id,
                    'debit': 0.0,
                    'credit': amount
                })
            ]
        })
        entry._post()
        return entry

    def test_deposit_zero_wallet_amount_from_manual_journal_entry(self):
        entry = self._create_manual_journal_entry(1000000, 0)
        self.assertRecordValues(entry.line_ids, [{
            'account_id': self.account_112.id,
            'partner_id': self.partner.id,
            'debit': 1000000,
            'credit': 0,
            'wallet': False,
            'wallet_amount': 0,
            'wallet_amount_currency': 0
        }, {
            'account_id': self.account_131.id,
            'partner_id': self.partner.id,
            'debit': 0,
            'credit': 1000000,
            'wallet': False,
            'wallet_amount': 0,
            'wallet_amount_currency': 0
        }])
        self.assertEqual(len(self.partner.commercial_partner_id.wallet_ids), 0)

    def test_deposit_non_zero_wallet_amount_from_manual_journal_entry(self):
        entry = self._create_manual_journal_entry(1000000, 600000)
        self.assertRecordValues(entry.line_ids, [{
            'account_id': self.account_112.id,
            'partner_id': self.partner.id,
            'debit': 1000000,
            'credit': 0,
            'wallet': False,
            'wallet_amount': 0,
            'wallet_amount_currency': 0
        }, {
            'account_id': self.account_131.id,
            'partner_id': self.partner.id,
            'debit': 0,
            'credit': 1000000,
            'wallet': True,
            'wallet_amount': 600000,
            'wallet_amount_currency': 600000
        }])
        self.assertRecordValues(self.partner.commercial_partner_id.wallet_ids, [{'amount': 600000}])

    def test_withdraw_wallet(self):
        self.create_payment(amount=100000, wallet=True, wallet_amount=100000)
        self.create_payment(amount=10000, wallet=True, wallet_amount=10000, payment_type='outbound')
        self.assertRecordValues(self.partner.commercial_partner_id.wallet_ids, [{'amount': 90000}])
        # test in case that withdrawing money much more than money in wallet
        self.assertRaises(ValidationError, self.create_payment, amount=100000, payment_type='outbound', wallet=True, wallet_amount=100000)
        # test in case not exist wallet to withdraw
        self.assertRaises(ValidationError, self.create_payment, amount=100000, payment_type='outbound', wallet=True, wallet_amount=100000, currency_id=self.currency_usd.id)

    def test_compute_wallet_amount_1(self):
        payment = self.create_payment()
        self.assertEqual(payment.wallet_amount, 0)

    def test_compute_wallet_amount_2(self):
        payment = self.create_payment(wallet=True)
        self.assertEqual(payment.wallet_amount, 0)

    def test_compute_wallet_amount_3(self):
        invoice = self.create_invoice(custom_vals={
            'currency_id': self.currency_vnd.id,
        }, custom_line_vals_list=[
            {
                'wallet': True,
                'price_unit': 25000
            }, {
                'wallet': False,
                'price_unit': 100000
            }
        ])
        payment_register = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({'amount': 27000})
        payment = payment_register._create_payments()
        self.assertEqual(payment.wallet_amount, 25000)

    def test_register_payment_full_reconcile(self):
        invoice = self.create_invoice(custom_vals={
        }, custom_line_vals_list=[
            {
                'wallet': True,
                'price_unit': 25000
            }, {
                'wallet': False,
                'price_unit': 100000
            }
        ])
        payments = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({})._create_payments()
        self.assertRecordValues(payments, [{
            'amount': 125000,
            'wallet': True,
            'wallet_amount': 25000
        }])
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])

    def test_register_payment_partial_reconcile(self):
        invoice = self.create_invoice(custom_vals={
        }, custom_line_vals_list=[
            {
                'wallet': True,
                'price_unit': 25000
            }, {
                'wallet': False,
                'price_unit': 100000
            }
        ])
        payments = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({
            'amount': 65000,
            'wallet': True,
            'wallet_amount': 15000
        })._create_payments()
        self.assertRecordValues(payments, [{
            'amount': 65000,
            'wallet': True,
            'wallet_amount': 15000
        }])
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 60000,
            'wallet_amount_residual': 10000,
            'wallet_amount_residual_currency': 10000,
            'non_wallet_amount_residual': 50000,
            'non_wallet_amount_residual_currency': 50000
        }])

    def test_register_payment_currency(self):
        invoice = self.create_invoice(custom_vals={
        }, custom_line_vals_list=[
            {
                'wallet': True,
                'price_unit': 121000
            }, {
                'wallet': False,
                'price_unit': 110000
            }
        ])
        payments = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({
            'currency_id': self.currency_eur.id,
        })._create_payments()
        self.assertRecordValues(payments, [{
            'amount': 210000,
            'wallet': True,
            'wallet_amount': 110000,
            'currency_id': self.currency_eur.id,
        }])
        invoice_receivable_move_line = invoice.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(invoice_receivable_move_line, [{
            'amount_residual': 0,
            'wallet_amount_residual': 0,
            'wallet_amount_residual_currency': 0,
            'non_wallet_amount_residual': 0,
            'non_wallet_amount_residual_currency': 0
        }])

    def test_register_payment_from_batch(self):
        invoice1 = self.create_invoice(custom_vals={
        }, custom_line_vals_list=[
            {
                'wallet': True,
                'price_unit': 25000
            }, {
                'wallet': False,
                'price_unit': 100000
            }
        ])
        invoice_2 = self.create_invoice(custom_vals={
        }, custom_line_vals_list=[
            {
                'wallet': True,
                'price_unit': 25000
            }, {
                'wallet': False,
                'price_unit': 100000
            }
        ])
        payments = self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=(invoice1 + invoice_2).ids
        ).create({})._create_payments()
        self.assertRecordValues(payments, [{
            'amount': 125000,
            'wallet': True,
            'wallet_amount': 25000
        }, {
            'amount': 125000,
            'wallet': True,
            'wallet_amount': 25000
        }])

    def test_multi_invoice_multi_payment_complex(self):
        self.cr.execute("UPDATE res_company SET currency_id = %s WHERE id = %s", [self.currency_vnd.id, self.env.company.id])
        self.env['res.currency.rate'].search([]).unlink()
        currency_rate_vals = [
            {
                'name': '2022-01-01',
                'rate': 1,
                'currency_id': self.currency_vnd.id
            },
            {
                'name': '2022-01-01',
                'inverse_rate': 22530,
                'currency_id': self.currency_usd.id
            },
            {
                'name': '2022-01-15',
                'inverse_rate': 23450,
                'currency_id': self.currency_usd.id
            },
            {
                'name': '2022-01-30',
                'inverse_rate': 23970,
                'currency_id': self.currency_usd.id
            },
            {
                'name': '2022-02-10',
                'inverse_rate': 22150,
                'currency_id': self.currency_usd.id
            },
            {
                'name': '2022-02-20',
                'inverse_rate': 24230,
                'currency_id': self.currency_usd.id
            },
            {
                'name': '2022-02-22',
                'inverse_rate': 23130,
                'currency_id': self.currency_usd.id
            },
            {
                'name': '2022-03-10',
                'inverse_rate': 24560,
                'currency_id': self.currency_usd.id
            },
            {
                'name': '2022-03-15',
                'inverse_rate': 24270,
                'currency_id': self.currency_usd.id
            },
            {
                'name': '2022-03-20',
                'inverse_rate': 24670,
                'currency_id': self.currency_usd.id
            },
        ]
        self.env['res.currency.rate'].create(currency_rate_vals)
        invoice1 = self.create_invoice(
            custom_vals={
                'currency_id': self.currency_usd.id,
                'date': '2022-01-01'
            },
            custom_line_vals_list=[{
                'price_unit': 69,
                'wallet': True
            }]
        )
        invoice2 = self.create_invoice(
            custom_vals={
                'currency_id': self.currency_usd.id,
                'date': '2022-01-30'
            },
            custom_line_vals_list=[{
                'price_unit': 69,
                'wallet': True
            }]
        )
        invoice3 = self.create_invoice(
            custom_vals={
                'currency_id': self.currency_usd.id,
                'date': '2022-03-10'
            },
            custom_line_vals_list=[{
                'price_unit': 69,
                'wallet': True
            }]
        )
        payment1 = self.create_payment(amount=75, wallet=True, wallet_amount=65, date='2022-01-15')
        payment2 = self.create_payment(amount=70, wallet=True, wallet_amount=70, date='2022-02-10')
        payment3 = self.create_payment(amount=50, wallet=True, wallet_amount=31.5, date='2022-02-20')
        payment4 = self.create_payment(amount=27, wallet=True, wallet_amount=27, date='2022-02-28')
        payment5 = self.create_payment(amount=33.5, wallet=True, wallet_amount=33.5, date='2022-03-20')

        (invoice1.line_ids | payment1.line_ids).filtered(lambda l: l.account_id.internal_type == 'receivable').reconcile()
        self.assertNotEqual(invoice1.payment_state, 'paid')
        (invoice1.line_ids | payment2.line_ids).filtered(lambda l: l.account_id.internal_type == 'receivable').reconcile()
        self.assertEqual(invoice1.payment_state, 'paid')
        (invoice2.line_ids | payment2.line_ids).filtered(lambda l: l.account_id.internal_type == 'receivable').reconcile()
        self.assertNotEqual(invoice2.payment_state, 'paid')
        (invoice2.line_ids | payment3.line_ids).filtered(lambda l: l.account_id.internal_type == 'receivable').reconcile()
        self.assertEqual(invoice2.payment_state, 'paid')
        (invoice3.line_ids | payment3.line_ids).filtered(lambda l: l.account_id.internal_type == 'receivable').reconcile()
        self.assertNotEqual(invoice3.payment_state, 'paid')
        (invoice3.line_ids | payment4.line_ids).filtered(lambda l: l.account_id.internal_type == 'receivable').reconcile()
        self.assertNotEqual(invoice3.payment_state, 'paid')
        (invoice3.line_ids | payment5.line_ids).filtered(lambda l: l.account_id.internal_type == 'receivable').reconcile()
        self.assertEqual(invoice3.payment_state, 'paid')

    def test_adjust_wallet_amount_onpayment_before_confirm(self):
        vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': self.partner.id,
            'payment_method_id': self.account_payment_method_manual_in.id,
            'journal_id': self.bank_journal_usd.id,
            'date': datetime.date(self.current_year - 1, 1, 1),
            'wallet': True,
            'amount': 150000,
            'wallet_amount': 100000,
        }
        payment = self.env['account.payment'].create(vals)
        payment_form = Form(payment)
        payment_form.wallet_amount = 50000
        payment_form.save()
        payment.action_post()
        receivable_move_line = payment.line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable')
        self.assertRecordValues(receivable_move_line, [{
            'wallet_amount': 50000,
            'wallet_amount_residual': -50000,
            'non_wallet_amount_residual': -100000,
        }])

    def test_edit_payment_01(self):
        partner_demo = self.env.ref('base.partner_demo')
        self.assertFalse(partner_demo.wallet_ids)

        payment1 = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': partner_demo.id,
            'amount': 500
        })
        self.assertFalse(partner_demo.wallet_ids)
        payment1.wallet = True
        self.assertRecordValues(partner_demo.wallet_ids, [{'amount': 0}])

        payment1.action_post()
        self.assertEqual(partner_demo.wallet_ids[0].amount, 500)

    def test_edit_payment_02(self):
        partner_demo = self.env.ref('base.partner_demo')
        payment = self.env['account.payment'].create({
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id': partner_demo.id,
            'amount': 500,
            'wallet': True,
            'currency_id': self.env.company.currency_id.id
        })
        self.assertRecordValues(payment.line_ids, [
            {
                'wallet': True,
                'wallet_amount': 500,
                'wallet_id': partner_demo.wallet_ids.id,
                'wallet_amount_currency': 500
            },
            {
                'wallet': True,
                'wallet_amount': 500,
                'wallet_id': partner_demo.wallet_ids.id,
                'wallet_amount_currency': 500
            }
        ])

        payment.wallet = False
        self.assertRecordValues(payment.line_ids, [
            {
                'wallet': False,
                'wallet_amount': False,
                'wallet_id': False,
                'wallet_amount_currency': False
            },
            {
                'wallet': False,
                'wallet_amount': False,
                'wallet_id': False,
                'wallet_amount_currency': False
            }
        ])
