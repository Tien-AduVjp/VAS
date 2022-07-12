from odoo.exceptions import UserError, ValidationError, AccessDenied
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
        self.assertEqual(exp_sheet_post.move_ids[0].move_type, 'in_invoice')

    def test_cancel_unlink_expense_sheet_paid(self):
        exp_sheet_payment = self.register_payment_hr_expense_sheet_employee_paid(self.expense_sheet)
        self.assertRaises(UserError, self.expense_sheet.unlink)

        # Cancel payment
        exp_sheet_payment.action_draft()
        exp_sheet_payment.action_cancel()

        # Cancel entry journal items
        journal_bill = self.expense_sheet.move_ids
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

    def test_expense_with_tax(self):
        tax_purchase = self.env['account.tax'].search([], limit=1)
        self.expense_sheet.expense_line_ids.tax_ids = [tax_purchase.id]
        self.post_hr_expense_sheet(self.expense_sheet)

        self.assertIn(tax_purchase, self.expense_sheet.move_ids.invoice_line_ids.tax_ids)

    # TODO: remove in 15.0 because it added from 15.0
    def test_expense_sheet_payment_state(self):
        ''' Test expense sheet payment states when partially paid, in payment and paid. '''
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': 'Expense for John Smith',
            'employee_id': self.expense_employee.id,
            'accounting_date': '2021-01-01',
            'expense_line_ids': [(0, 0, {
                'name': 'Car Travel Expenses',
                'employee_id': self.expense_employee.id,
                'product_id': self.product_a.id,
                'unit_amount': 350.00,
            })]
        })

        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_sheet_move_create()

        payment = self.get_payment(expense_sheet, 100.0)
        liquidity_lines1 = payment._seek_for_lines()[0]

        self.assertEqual(expense_sheet.payment_state, 'partial', 'payment_state should be partial')

        payment = self.get_payment(expense_sheet, 250.0)
        liquidity_lines2 = payment._seek_for_lines()[0]

        in_payment_state = expense_sheet.move_ids._get_invoice_in_payment_state()
        self.assertEqual(expense_sheet.payment_state, in_payment_state, 'payment_state should be ' + in_payment_state)

        statement = self.env['account.bank.statement'].create({
            'name': 'test_statement',
            'journal_id': self.default_journal_bank.id,
            'line_ids': [
                (0, 0, {
                    'payment_ref': 'pay_ref',
                    'amount': -350.0,
                    'partner_id': self.expense_employee.address_home_id.id,
                }),
            ],
        })
        statement.button_post()
        statement.line_ids.reconcile([{'id': liquidity_lines1.id}, {'id': liquidity_lines2.id}])

        self.assertEqual(expense_sheet.payment_state, 'paid', 'payment_state should be paid')

    def test_expense_sheet_invoice_emp_pay(self):
        lamp_bill_expense = self.env.ref('hr_expense.lamp_bill_expense')
        partner_2 = self.env.ref('base.res_partner_2')
        lamp_bill_expense.vendor_id = partner_2
        expense_sheet = self.post_hr_expense_sheet(self.expense_sheet)
        account_1 = expense_sheet.expense_line_ids.filtered(lambda e: e.vendor_id.id == self.partner.id).product_id.product_tmpl_id._get_product_accounts()['expense']
        account_2 = expense_sheet.expense_line_ids.filtered(lambda e: e.vendor_id.id == partner_2.id).product_id.product_tmpl_id._get_product_accounts()['expense']
        partner_1_invoice = expense_sheet.move_ids.filtered(lambda m:m.move_type == 'in_invoice' and m.partner_id.id == self.partner.id)
        partner_2_invoice = expense_sheet.move_ids.filtered(lambda m:m.move_type == 'in_invoice' and m.partner_id.id == partner_2.id)
        self._check_account_move_line(
            partner_1_invoice.line_ids,
            account_1.code,
            self.partner,
            334.5,
            self.partner.property_account_payable_id.code,
            self.partner,
            334.5
        )
        self._check_account_move_line(
            partner_2_invoice.line_ids,
            account_2.code,
            partner_2,
            28.99,
            partner_2.property_account_payable_id.code,
            partner_2,
            28.99
        )

        invoices = expense_sheet.move_ids.filtered(lambda m:m.move_type == 'entry')
        self._check_account_move_line(
            invoices[1].line_ids,
            self.partner.property_account_payable_id.code,
            self.partner,
            334.5,
            expense_sheet.employee_id.address_home_id.property_account_payable_id.code,
            expense_sheet.employee_id.address_home_id,
            334.5
        )
        self._check_account_move_line(
            invoices[0].line_ids,
            partner_2.property_account_payable_id.code,
            partner_2,
            28.99,
            expense_sheet.employee_id.address_home_id.property_account_payable_id.code,
            expense_sheet.employee_id.address_home_id,
            28.99
        )

        action_data = expense_sheet.action_register_payment()
        context = action_data['context']
        context.update({
            'active_model': 'account.move',
            'expense_ids': expense_sheet.ids,
            'active_ids': expense_sheet.move_ids.ids,
        })
        wizard =  Form(self.env['account.payment.register'].with_context(context)).save()
        account_payments = wizard._create_payments()

        self.assertEqual(account_payments.partner_id, expense_sheet.employee_id.address_home_id.commercial_partner_id)

    def test_expense_sheet_no_invoice_emp_pay(self):
        lamp_bill_expense = self.env.ref('hr_expense.lamp_bill_expense')
        partner_2 = self.env.ref('base.res_partner_2')
        lamp_bill_expense.write({
            'vendor_id' : partner_2,
            'to_invoice': False
        })
        with self.assertRaises(ValidationError):
            self.post_hr_expense_sheet(self.expense_sheet)
        self.expense_sheet.expense_line_ids.write({
            'to_invoice': False,
        })
        expense_sheet = self.post_hr_expense_sheet(self.expense_sheet)
        account_1 = expense_sheet.expense_line_ids.product_id.product_tmpl_id._get_product_accounts()['expense']

        self._check_account_move_line(
            expense_sheet.move_ids[0].line_ids,
            account_1.code,
            expense_sheet.employee_id.address_home_id.commercial_partner_id,
            363.49,
            expense_sheet.employee_id.address_home_id.property_account_payable_id.code,
            expense_sheet.employee_id.address_home_id.commercial_partner_id,
            363.49
        )

        invoices = expense_sheet.move_ids.filtered_domain([('move_type', '=', 'in_invoice')])
        for invoice in invoices:
            self.assertEqual(invoice.payment_state, 'paid')

        action_data = expense_sheet.action_register_payment()
        context = action_data['context']
        context.update({
            'active_model': 'account.move',
            'expense_ids': expense_sheet.ids,
            'active_ids': expense_sheet.move_ids.ids,
        })
        wizard =  Form(self.env['account.payment.register'].with_context(context)).save()
        account_payments = wizard._create_payments()

        self.assertEqual(account_payments.partner_id, expense_sheet.employee_id.address_home_id.commercial_partner_id)

    def test_expense_sheet_invoice_company_pay(self):
        """
            Case:
                Expense 1 của NCC 1 có Bill Ref là 111
                Expense 2 cũng của NCC 1 có Bill Ref là 222
                Expense 3 của NCC 2 có Bill Ref là 333
            Expect:
                Vào sổ expense sheet thì có 3 hóa đơn: 2 cái của NCC 1 và 1 cái của NCC 2
                Khi payment thì nếu gộp thì chỉ có 2 payment cho NCC 1 và NCC2. Nếu không gộp thì có 3 payment cho 3 hóa đơn trên.
        """

        vendor1 = self.env.ref('base.res_partner_2')
        vendor2 = self.env.ref('base.res_partner_3')
        self.expense_sheet.expense_line_ids.write({
            'vendor_id': vendor1.id,
            'to_invoice': True,
            'payment_mode': 'company_account',
        })
        self.expense_sheet.expense_line_ids[0].reference = '111'
        self.expense_sheet.expense_line_ids[1].reference = '222'
        expense3 = self.env['hr.expense'].create({
            'name': 'expense3',
            'to_invoice': True,
            'vendor_id': vendor2.id,
            'payment_mode': 'company_account',
            'employee_id': self.env.ref('hr.employee_al').id,
            'product_id': self.env.ref('product.product_delivery_02').id,
            'unit_amount': '99.5',
            'quantity': 1,
            'reference': '222',
            'sheet_id': self.expense_sheet.id
        })
        expense_sheet = self.post_hr_expense_sheet(self.expense_sheet)

        self.assertEqual(len(expense_sheet.move_ids), 3)
        self.assertEqual(expense_sheet.move_ids.journal_id, expense_sheet.vendor_bill_journal_id)
        journal_item_expense1 = expense_sheet.move_ids.line_ids.filtered(lambda line: line.expense_id == self.env.ref('hr_expense.lamp_bill_expense'))
        account_expense = expense_sheet.expense_line_ids.filtered(lambda e: e.vendor_id == vendor1).product_id.product_tmpl_id._get_product_accounts()['expense']

        self._check_account_move_line(
            journal_item_expense1,
            account_expense.code,
            vendor1,
            28.99,
            vendor1.property_account_payable_id.code,
            vendor1,
            28.99
        )

        journal_item_expense2 = expense_sheet.move_ids.line_ids.filtered(lambda line: line.expense_id == self.env.ref('hr_expense.chair_bill_expense'))
        self._check_account_move_line(
            journal_item_expense2,
            account_expense.code,
            vendor1,
            334.5,
            vendor1.property_account_payable_id.code,
            vendor1,
            334.5
        )

        journal_item_expense3 = expense_sheet.move_ids.line_ids.filtered(lambda line: line.expense_id == expense3)
        self._check_account_move_line(
            journal_item_expense3,
            account_expense.code,
            vendor2,
            99.5,
            vendor2.property_account_payable_id.code,
            vendor2,
            99.5
        )

        action_data = expense_sheet.action_register_payment()
        context = action_data['context']

        # Case don't group payment
        with self.assertRaises(AccessDenied), self.env.cr.savepoint():
            context.update({
                'active_model': 'account.move',
                'expense_ids': expense_sheet.ids,
                'active_ids': expense_sheet.move_ids.ids,
                'default_group_payment': False
            })
            wizard = Form(self.env['account.payment.register'].with_context(context)).save()
            account_payments = wizard._create_payments()
            payment_vendor1 = account_payments.filtered(lambda p: p.partner_id == vendor1)
            payment_vendor2 = account_payments.filtered(lambda p: p.partner_id == vendor2)
            self.assertEqual(len(payment_vendor1), 2)
            self.assertEqual(len(payment_vendor2), 1)
            self.assertEqual(sum(payment_vendor1.mapped('amount')), 363.49)
            self.assertEqual(payment_vendor2.amount, 99.5)

            raise AccessDenied

        # Case group payment
        context.update({
            'active_model': 'account.move',
            'expense_ids': expense_sheet.ids,
            'active_ids': expense_sheet.move_ids.ids,
            'default_group_payment': True
        })
        wizard = Form(self.env['account.payment.register'].with_context(context)).save()
        account_payments = wizard._create_payments()
        payment_vendor1 = account_payments.filtered(lambda p: p.partner_id == vendor1)
        payment_vendor2 = account_payments.filtered(lambda p: p.partner_id == vendor2)
        self.assertEqual(len(payment_vendor1), 1)
        self.assertEqual(len(payment_vendor2), 1)
        self.assertEqual(payment_vendor1.amount, 363.49)
        self.assertEqual(payment_vendor2.amount, 99.5)

    def test_cancel_move_of_expense_sheet(self):
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': 'Expense for John Smith',
            'employee_id': self.expense_employee.id,
            'accounting_date': '2021-01-01',
            'expense_line_ids': [(0, 0, {
                'name': 'Car Travel Expenses',
                'employee_id': self.expense_employee.id,
                'product_id': self.product_a.id,
                'unit_amount': 350.00,
            })]
        })

        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_sheet_move_create()

        self.assertEqual(expense_sheet.amount_residual, 350.0)

        expense_sheet.move_ids.button_draft()
        expense_sheet.move_ids.button_cancel()
        self.assertEqual(expense_sheet.amount_residual, 0)

        expense_sheet.action_cancel()
        expense_sheet.reset_expense_sheets()
        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_sheet_move_create()
        self.assertEqual(expense_sheet.amount_residual, 350.0)

        self.get_payment(expense_sheet, 350.0)
        self.assertEqual(expense_sheet.amount_residual, 0)

    def test_cancel_payment_of_expense_sheet(self):
        """
        When you cancel a statement entry, the amount residual is recalculated
        """
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': 'Expense for John Smith',
            'employee_id': self.expense_employee.id,
            'accounting_date': '2021-01-01',
            'expense_line_ids': [(0, 0, {
                'name': 'Car Travel Expenses',
                'employee_id': self.expense_employee.id,
                'product_id': self.product_a.id,
                'unit_amount': 350.00,
            })]
        })

        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_sheet_move_create()

        payment = self.get_payment(expense_sheet, 100.0)

        self.assertEqual(expense_sheet.amount_residual, 250.0)

        payment.action_draft()
        payment.action_cancel()
        self.assertEqual(expense_sheet.amount_residual, 350.0)

    def test_create_invoice_follow_reference(self):
        """
        Only expenses with the same vendor and bill reference will be consolidated into a single invoice.
        """
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': 'Expense',
            'employee_id': self.expense_employee.id,
            'accounting_date': '2021-01-01',
            'expense_line_ids': [
            (0, 0, {
                'name': 'Bike Travel Expenses',
                'employee_id': self.expense_employee.id,
                'product_id': self.product_a.id,
                'vendor_id': self.partner.id,
                'unit_amount': 100.00,
                'to_invoice': True,
                'payment_mode': 'own_account',
            }),
            (0, 0, {
                'name': 'Car Travel Expenses',
                'employee_id': self.expense_employee.id,
                'product_id': self.product_a.id,
                'vendor_id': self.partner.id,
                'unit_amount': 200.00,
                'to_invoice': True,
                'payment_mode': 'own_account',
                'reference': 'Reference 1'
            }),
            (0, 0, {
                'name': 'Moto Travel Expenses',
                'employee_id': self.expense_employee.id,
                'product_id': self.product_a.id,
                'vendor_id': self.partner.id,
                'unit_amount': 300.00,
                'to_invoice': True,
                'payment_mode': 'own_account',
                'reference': 'Reference 1'
            }),
            (0, 0, {
                'name': 'Train Travel Expenses',
                'employee_id': self.expense_employee.id,
                'product_id': self.product_a.id,
                'vendor_id': self.partner.id,
                'unit_amount': 400.00,
                'to_invoice': True,
                'payment_mode': 'own_account',
                'reference': 'Reference 2'
            })]
        })
        expense_sheet.action_submit_sheet()
        expense_sheet.approve_expense_sheets()
        expense_sheet.action_sheet_move_create()

        self.assertEqual(len(expense_sheet.move_ids.filtered_domain([('move_type', '=', 'in_invoice')])), 3)
