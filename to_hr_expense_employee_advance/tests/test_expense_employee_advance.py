from odoo.tests.common import tagged
from odoo.exceptions import ValidationError, UserError
from odoo.tests import Form
from odoo.addons.to_hr_expense.tests.common import Common


@tagged('-at_install', 'post_install')
class TestExpenseEmployeeAdvance(Common):

    @classmethod
    def setUpClass(cls):
        super(TestExpenseEmployeeAdvance, cls).setUpClass()
        cls.emd_journal = cls.env['account.journal'].search([
            ('company_id', '=', cls.env.company.id),
            ('is_advance_journal', '=', True),
            ('code', '=', 'EAJ')], limit=1)
        cls.account_receivable = cls.env['account.account'].search([
            ('company_id', '=', cls.env.company.id),
            ('internal_type', '=', 'receivable'),
            ('deprecated', '=', False)], limit=1)
        cls.employee = cls.env.ref('hr.employee_al')
        cls.employee.write({'property_advance_account_id': cls.account_receivable.id})
        cls.expense_sheet = cls.env.ref('hr_expense.office_furniture_sheet')

    def test_11_validate_payment(self):
        """
        Check advance account
        """
        self.expense_sheet.action_submit_sheet()
        self.expense_sheet.approve_expense_sheets()
        self.expense_sheet.action_sheet_move_create()
        context = {
            'active_model': 'account.move',
            'active_ids': self.expense_sheet.move_ids.ids,
        }
        advance_payment_register = self.env['account.advance.payment.register'].with_context(context).create({
            'employee_id': self.expense_sheet.employee_id.id,
            'expense_sheet_id': self.expense_sheet.id,
        })
        advance_payment_register.action_create_advance_journal_entries()
        accounts = self.expense_sheet.move_ids.line_ids.account_id
        self.assertTrue(self.account_receivable in accounts)
        self.assertEqual(self.expense_sheet.state, 'done')
        self.assertEqual(self.expense_sheet.payment_state, 'paid')

    def test_12_validate_payment(self):
        """
        Unable to pay expenses when employees do not have a private address
        """
        self.employee.write({'address_home_id': False})
        with self.assertRaises(UserError):
            posted_expense_sheet = self.post_hr_expense_sheet(self.expense_sheet)
            action_data = posted_expense_sheet.action_register_payment()
            context = action_data['context']
            context.update({
                'active_model': 'account.move',
                'expense_ids': posted_expense_sheet.ids,
                'active_ids': posted_expense_sheet.move_ids.ids,
            })
            wizard =  Form(self.env['account.payment.register'].with_context(context)).save()
            wizard.journal_id = self.emd_journal
            wizard._create_payments()

    def test_13_validate_payment(self):
        """
        Pay expense sheet many times with advance payment in many times
        Expense sheet: 363.49
        Register Advance Payment 1: 300
        Register Advance Payment 2: 63.49
        """
        self.expense_sheet.action_submit_sheet()
        self.expense_sheet.approve_expense_sheets()
        self.expense_sheet.action_sheet_move_create()
        context = {
            'active_model': 'account.move',
            'active_ids': self.expense_sheet.move_ids.ids,
        }
        advance_payment_register = self.env['account.advance.payment.register'].with_context(context).create({
            'employee_id': self.expense_sheet.employee_id.id,
            'expense_sheet_id': self.expense_sheet.id,
            'amount': 300
        })
        advance_payment_register.action_create_advance_journal_entries()
        self.assertEqual(self.expense_sheet.state, 'post')
        self.assertEqual(self.expense_sheet.payment_state, 'partial')

        advance_payment_register_1 = self.env['account.advance.payment.register'].with_context(context).create({
            'employee_id': self.expense_sheet.employee_id.id,
            'expense_sheet_id': self.expense_sheet.id,
            'amount': 63.49
        })
        advance_payment_register_1.action_create_advance_journal_entries()
        self.assertEqual(self.expense_sheet.state, 'done')
        self.assertEqual(self.expense_sheet.payment_state, 'paid')

    def test_14_validate_payment_mix_cash_and_advance(self):
        """
        Case mix payment type: direct by cash and advance
        """
        self.expense_sheet.action_submit_sheet()
        self.expense_sheet.approve_expense_sheets()
        self.expense_sheet.action_sheet_move_create()
        wizard_payment_advance = self.expense_sheet.action_register_advance_payment()
        advance_payment_register = self.env['account.advance.payment.register'].with_context(wizard_payment_advance['context']).create({
            'amount': 150
        })
        advance_payment_register.action_create_advance_journal_entries()
        accounts = self.expense_sheet.move_ids.line_ids.account_id
        self.assertTrue(self.account_receivable in accounts)
        self.assertNotEqual(self.expense_sheet.state, 'done')
        self.assertNotEqual(self.expense_sheet.payment_state, 'paid')

        wizard_payment_direct = self.expense_sheet.action_register_payment()
        direct_register_payment = self.env['account.payment.register'].with_context(wizard_payment_direct['context']).create({})
        direct_register_payment.action_create_payments()
        self.assertEqual(self.expense_sheet.state, 'done')
        self.assertEqual(self.expense_sheet.payment_state, 'paid')
