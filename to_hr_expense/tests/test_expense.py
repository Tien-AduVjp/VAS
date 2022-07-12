from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form

from .common import Common


class TestExpense(Common):

    def test_form_require_vendor_field(self):
        hr_expense = Form(self.env['hr.expense'])
        hr_expense.payment_mode = 'own_account'
        hr_expense.to_invoice = True

        self.assertTrue(hr_expense._get_modifier('vendor_id', 'required'))

    def test_type_journal_post_expense_sheet(self):
        exp_sheet_post = self.post_hr_expense_sheet(self.expense_sheet)
        self.assertEqual(exp_sheet_post.account_move_id.type, 'in_invoice')

    def test_partner_id_on_payment_paid_employee(self):
        exp_sheet_payment = self.register_payment_hr_expense_sheet_employee_paid(self.expense_sheet)
        self.assertEqual(exp_sheet_payment.partner_id, self.partner)

    def test_cancel_unlink_expense_sheet_paid(self):
        exp_sheet_payment = self.register_payment_hr_expense_sheet_employee_paid(self.expense_sheet)
        self.assertRaises(UserError, self.expense_sheet.unlink)

        # Cancel payment
        exp_sheet_payment.action_draft()
        exp_sheet_payment.cancel()

        # Cancel entry journal items
        journal_bill = self.expense_sheet.account_move_id
        journal_bill.button_draft()
        journal_bill.button_cancel()

        # Click cancel button will open refusing wizard
        wz_reason_cancel = self.expense_sheet.action_cancel()
        self.assertEqual(wz_reason_cancel.get('type'), 'ir.actions.act_window')

        # Test can't unlink expense sheet when it's state is cancel
        self.cancel_hr_expense_sheet_posted(self.expense_sheet)
        self.assertRaises(UserError, self.expense_sheet.unlink)

    def test_expense_sheet_linking_payment(self):
        exp_sheet_payment = self.register_payment_hr_expense_sheet_employee_paid(self.expense_sheet)
        self.assertEqual(self.expense_sheet.payment_ids, exp_sheet_payment)
        self.assertEqual(self.expense_sheet.payments_count, len(self.expense_sheet.payment_ids))

    def test_condition_submit_expense_sheet_paid_employee_to_manager1(self):
        # All expense line per expense sheet must be same to_invoice value
        self.expense_sheet.expense_line_ids[-1:].to_invoice = False
        self.assertRaises(ValidationError, self.expense_sheet.action_submit_sheet)

        self.expense_sheet.expense_line_ids[-1:].to_invoice = True
        self.expense_sheet.action_submit_sheet()

    def test_condition_submit_expense_sheet_paid_employee_to_manager2(self):
        # All expense line per expense sheet must be same vendor
        self.expense_sheet.expense_line_ids[-1:].vendor_id = self.env.ref('base.res_partner_2')
        self.assertRaises(ValidationError, self.expense_sheet.action_submit_sheet)

        self.expense_sheet.expense_line_ids[-1:].vendor_id = self.partner
        self.expense_sheet.action_submit_sheet()

    def test_aggregate_payment_expense_sheet_paid_company(self):
        # Generate only one payment feature
        self.expense_sheet.expense_line_ids.payment_mode = 'company_account'
        self.expense_sheet.aggregate_payments = True

        exp_sheet = self.post_hr_expense_sheet(self.expense_sheet)
        journal_items = exp_sheet.account_move_id.line_ids

        journal_bank_account = journal_items.filtered(lambda r: r.credit)

        self.assertEqual(len(journal_bank_account), 1)
        self.assertEqual(journal_bank_account.credit, sum(self.expense_sheet.expense_line_ids.mapped('total_amount')))

    def test_expense_with_tax(self):
        tax_purchase = self.env['account.tax'].search([], limit=1)
        self.expense_sheet.expense_line_ids.tax_ids = [tax_purchase.id]
        self.post_hr_expense_sheet(self.expense_sheet)

        self.assertIn(tax_purchase, self.expense_sheet.account_move_id.invoice_line_ids.tax_ids)
