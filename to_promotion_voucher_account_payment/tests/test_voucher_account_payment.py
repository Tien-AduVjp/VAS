from psycopg2 import IntegrityError

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import Form
from odoo.tools.misc import mute_logger

from odoo.addons.to_promotion_voucher.tests.test_voucher_issue_order import TestVoucherIssueOrder


@tagged('post_install', '-at_install')
class TestVoucherAccountPayment(TestVoucherIssueOrder):

    def setUp(self):
        super(TestVoucherAccountPayment, self).setUp()
        self.AccountJournal = self.env['account.journal'].with_context(tracking_disable=True)
        self.AccountPayment = self.env['account.payment'].with_context(tracking_disable=True)
        self.AccountMove = self.env['account.move'].with_context(tracking_disable=True)
        partner = self.env.ref('base.partner_admin')
        self.voucher_journal = self.AccountJournal.search([
             ('name', '=', 'Promotion Voucher'),
             ('company_id', '=', self.env.company.id),
             ('code', '=', 'PVJ'),
             ('voucher_payment', '=', True)], limit=1)
        if not self.voucher_journal:
            self.voucher_journal = self.AccountJournal.create({
                        'name': 'Promotion Voucher',
                        'type': 'cash',
                        'code': 'PVJ',
                        'company_id': self.env.company.id,
                        'show_on_dashboard': True,
                        'voucher_payment': True
                    })
        self.issue_voucher_payment = self.issue_order.copy()
        self.issue_voucher_payment.action_issue()
        self.voucher_promotion = self.Voucher.search([('issue_order_id', '=', self.issue_voucher_payment.id)], limit=1)
        self.voucher_promotion.write({'value': 100000 , 'state': 'activated'})
        
        self.account_payment_form = Form(self.AccountPayment)
        self.account_payment_form.payment_type = 'inbound'
        self.account_payment_form.partner_type = 'customer'
        self.account_payment_form.partner_id = partner
        self.account_payment_form.journal_id = self.voucher_journal
        self.account_payment_form.voucher_code = self.voucher_promotion.serial
        self.account_payment = self.account_payment_form.save()
        
        self.product_a = self.env['product.product'].create({
            'name': 'product_a',
            'type': 'product',
            'uom_id': self.env.ref('uom.product_uom_unit').id,
            'lst_price': 100000.0,
        })
        self.invoice_line_vals = {
            'name': self.product_a.name,
            'product_id': self.product_a.id,
            'quantity': 1.0,
            'discount': 0.0,
            'price_unit': 100000.0,
        }
        self.invoice_form = Form(self.env['account.move'].with_context(default_type='out_invoice'))
        self.invoice_form.partner_id = partner
        self.invoice = self.invoice_form.save()
        
    def test_01_onchange_on_payment_with_voucher(self):
        self.account_payment_form.voucher_code = self.voucher_promotion.serial
        self.assertEqual(self.account_payment_form.voucher_id.id, self.voucher_promotion.id)
        self.assertEqual(self.account_payment_form.amount, self.voucher_promotion.value - self.voucher_promotion.used_amount)

    def test_02_onchange_on_payment_with_voucher(self):
        # Onchange voucher code of voucher does not exist
        with self.assertRaises(ValidationError):
            self.account_payment_form.voucher_code = 'demo123'

    def test_03_onchange_on_payment_with_voucher(self):
        # Onchange voucher code of voucher in status new
        with self.assertRaises(ValidationError):
            self.voucher_promotion.write({'state': 'new'})
            self.account_payment_form.voucher_code = self.voucher_promotion.serial

    def test_04_onchange_on_payment_with_voucher(self):
        # Onchange voucher code of voucher in status expired
        with self.assertRaises(ValidationError):
            self.voucher_promotion.write({'state': 'expired'})
            self.account_payment_form.voucher_code = self.voucher_promotion.serial

    def test_05_onchange_on_payment_with_voucher(self):
        # Onchange voucher code of voucher in status used : Used Amount = Voucher Value
        with self.assertRaises(ValidationError):
            self.voucher_promotion.write({'state': 'used', 'used_amount': 100000})
            self.account_payment_form.voucher_code = self.voucher_promotion.serial

    def test_06_onchange_on_payment_with_voucher(self):
        # Onchange voucher code of voucher in status used : Used Amount < Voucher Value
        self.voucher_promotion.write({'state': 'used', 'used_amount': 0})
        self.account_payment_form.voucher_code = self.voucher_promotion.serial
        self.assertEqual(self.account_payment_form.voucher_id.id, self.voucher_promotion.id)
        self.assertEqual(self.account_payment_form.amount, self.voucher_promotion.value - self.voucher_promotion.used_amount)
        
    def test_07_onchange_on_payment_with_voucher(self):
        # Onchange voucher code of voucher in status used , type voucher is payable once
        self.voucher_promotion.write({'state': 'used'})
        self.voucher_promotion.voucher_type_id.write({'payable_once': True})
        with self.assertRaises(ValidationError):
            self.account_payment_form.voucher_code = self.voucher_promotion.serial

    def test_01_constrains_prepayment_with_voucher(self):
        # Test constrains payment: Voucher in status activated
        self.assertEqual(self.account_payment.voucher_id.id, self.voucher_promotion.id)
        self.assertEqual(self.account_payment.amount, self.voucher_promotion.value)

    def test_02_constrains_prepayment_with_voucher(self):
        # Test constrains payment: Voucher not in status activated
        with self.assertRaises(ValidationError):
            self.account_payment.write({'voucher_id': {'state': 'new'}})
    
    def test_03_constrains_prepayment_with_voucher(self):
        # Test constrains payment: Voucher in status activated, amount payment > value voucher
        with self.assertRaises(ValidationError):
            self.account_payment.write({'amount': 200000})

    def test_01_check_confirm_prepayment_with_voucher(self):
        # Voucher in activated status
        # Confirm payment not in status draft
        with self.assertRaises(UserError):
            self.account_payment.write({'state': 'sent'})
            self.account_payment.post()

    def test_02_check_confirm_prepayment_with_voucher(self):
        # Voucher in activated status
        # Confirm payment, payment type not is inbound
        with self.assertRaises(UserError):
            self.account_payment.write({'payment_type': 'outbound'})
            self.account_payment.post()

    def test_03_check_confirm_prepayment_with_voucher(self):
        # Confirm payment, partner type not customer
        with self.assertRaises(UserError):
            self.account_payment.write({'partner_type': 'supplier'})
            self.account_payment.post()

    def test_04_check_confirm_prepayment_with_voucher(self):
        # Voucher in activated status
        # Confirmation of a successful payment utilizing the entire voucher value
        self.account_payment.post()
        self.assertEqual(self.account_payment.state, 'posted')
        self.assertEqual(self.account_payment.voucher_id.used_amount, self.account_payment.voucher_id.value)
        self.assertEqual(self.account_payment.amount, self.account_payment.voucher_id.value)
        self.assertEqual(self.account_payment.voucher_id.state, 'used')
        self.assertTrue(self.account_payment.move_line_ids)
    
    def test_05_check_confirm_prepayment_with_voucher(self):
        # Voucher in activated status# Voucher in activated status
        # Payment confirmation with a portion of the voucher value
        self.account_payment.write({'amount': 50000})
        self.account_payment.post()
        self.assertEqual(self.account_payment.state, 'posted')
        self.assertNotEqual(self.account_payment.voucher_id.used_amount, self.account_payment.voucher_id.value)
        self.assertEqual(self.account_payment.voucher_id.used_amount, self.account_payment.voucher_id.value - self.account_payment.amount)
        self.assertEqual(self.account_payment.voucher_id.state, 'used')
        self.assertTrue(self.account_payment.move_line_ids)
        
        # Confirm payment of the voucher's remaining balance.
        account_payment_copy = self.account_payment.copy()
        account_payment_copy.post()
        account_payment_copy.flush()

    @mute_logger('odoo.sql_db')
    def test_06_check_confirm_prepayment_with_voucher(self):
        # Voucher in used status
        # Payment confirmation for an amount greater than the voucher remaining balance
        self.account_payment.write({'amount': 50000})
        self.account_payment.post()
        with self.assertRaises(IntegrityError):
            account_payment_copy = self.account_payment.copy()
            account_payment_copy.write({'amount': 60000})
            account_payment_copy.post()
            account_payment_copy.flush()
    
    def test_01_check_payment_invoice_with_voucher(self):
        # Using a vouchder, pay bills that haven't been opened yet.
        self.assertEqual(self.invoice.state, 'draft')
        with self.assertRaises(ValidationError):
            self.invoice.write({'invoice_line_ids': [(0, 0 , self.invoice_line_vals)]})
            self.account_payment.write({'invoice_ids': [(6, 0, self.invoice.ids)]})
            self.account_payment.post()
    
    def test_02_check_payment_invoice_with_voucher(self):
        # Pay bills using a voucher in an open state
        self.invoice.write({'invoice_line_ids': [(0, 0 , self.invoice_line_vals)]})
        self.invoice.action_post()
        self.assertEqual(self.invoice.state, 'posted')
        self.account_payment.write({'invoice_ids': [(6, 0, self.invoice.ids)]})
        self.account_payment.post()
        self.assertEqual(self.invoice.amount_residual, self.invoice.amount_total - self.account_payment.amount)
