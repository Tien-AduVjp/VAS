from odoo.tests.common import tagged, Form, SavepointCase
from odoo.exceptions import ValidationError


@tagged('-at_install', 'post_install')
class TestExpenseEmployeeAdvance(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestExpenseEmployeeAdvance, cls).setUpClass()
        cls.journals = cls.env['account.journal'].search([('company_id', '=', cls.env.company.id)])
        cls.emd_journal = cls.journals.filtered(lambda j: j.is_advance_journal and j.code == 'EAJ')[:1]
        cls.account_receivable = cls.env['account.account'].search([('company_id', '=', cls.env.company.id)], limit=1)
        cls.emd_journal.write({
            'default_debit_account_id': cls.account_receivable.id,
            'default_credit_account_id': cls.account_receivable.id,
        })
        cls.partner = cls.env.ref('base.res_partner_1')
        cls.employee = cls.env.ref('hr.employee_al')
        cls.expense_sheet = cls.env.ref('hr_expense.office_furniture_sheet')
        cls.expense_sheet.approve_expense_sheets()
        cls.expense_sheet.action_sheet_move_create()
    
    def test_01_validate_register_payment_form(self):
        """
        Change journal in form expense sheet register payment, check value of employee
        """
        cash_journal = self.journals.filtered(lambda j: j.type == 'cash' and not j.is_advance_journal)[:1]
        expense_register_payment_form = Form(self.env['hr.expense.sheet.register.payment.wizard'].with_context(active_model='hr.expense.sheet'))
        expense_register_payment_form.expense_sheet_id = self.expense_sheet
        expense_register_payment_form.journal_id = self.emd_journal
        self.assertEqual(expense_register_payment_form.employee_id, self.employee)

        expense_register_payment_form.journal_id = cash_journal
        self.assertFalse(expense_register_payment_form.employee_id)

    def test_11_validate_payment(self):
        """
        Pay the expenditure then check the employee in the payment
        """
        expense_register_payment = self.env['hr.expense.sheet.register.payment.wizard'].with_context(active_model='hr.expense.sheet').create({
            'expense_sheet_id': self.expense_sheet.id,
            'journal_id': self.emd_journal.id,
            'partner_id': self.partner.id,
            'payment_method_id': self.emd_journal.outbound_payment_method_ids[:1].id,
            'amount': self.expense_sheet.total_amount,
            'employee_id': self.employee.id,
            'partner_bank_account_id': self.expense_sheet.employee_id.sudo().bank_account_id.id,
            'company_id': self.env.company.id,
        })
        expense_register_payment.with_context(active_ids=[self.expense_sheet.id]).expense_post_payment()
        account_payment = self.env['account.payment'].search([('expense_sheet_id', '=', self.expense_sheet.id), ('journal_id', '=', self.emd_journal.id)], limit=1)
        self.assertEqual(account_payment.employee_id, self.employee)

    def test_12_validate_payment(self):
        """
        Unable to pay expenses when employees do not have a private address
        """
        expense_register_payment = self.env['hr.expense.sheet.register.payment.wizard'].with_context(active_model='hr.expense.sheet').create({
            'expense_sheet_id': self.expense_sheet.id,
            'journal_id': self.emd_journal.id,
            'partner_id': self.partner.id,
            'payment_method_id': self.emd_journal.outbound_payment_method_ids[:1].id,
            'amount': self.expense_sheet.total_amount,
            'employee_id': self.employee.id,
            'partner_bank_account_id': self.expense_sheet.employee_id.sudo().bank_account_id.id,
        })
        self.employee.write({'address_home_id': False})
        with self.assertRaises(ValidationError):
            expense_register_payment.with_context(active_ids=[self.expense_sheet.id]).expense_post_payment()
