from datetime import date
from odoo.tests.common import tagged, Form
from odoo.exceptions import ValidationError
from .common import Common


@tagged('-at_install', 'post_install')
class TestEmployeeAdvanceForm(Common):

    def test_01_validate_amount_total(self):
        """
        The total advance amount is the same as the total advance detail lines
        """
        employee_advance_form = Form(self.env['employee.advance'])
        with employee_advance_form.lines.new() as line:
            line.name = 'Advance Line 1'
            line.amount = 100
        with employee_advance_form.lines.new() as line:
            line.name = 'Advance Line 2'
            line.amount = 200
        self.assertEqual(employee_advance_form.amount, 300)

    def test_11_check_employee(self):
        """
        Without a private address, it is impossible to create advance payments for employees
        """
        with self.assertRaises(ValidationError):
            employee_advance_form = Form(self.env['employee.advance'])
            employee_advance_form.employee_id = self.employee_advance_employee

    def test_21_validate_reconcile_batches(self):
        # When creating a reconcile batches, don't show employees.
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_manager_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        employee_advance.action_confirm()
        employee_advance.action_approve()

        emd_reconcile_batch_1 = Form(self.env['employee.advance.reconcile.batch'])
        emd_reconcile_batch_1.date = date(2021, 7, 10)
        emd_reconcile_batch_1.journal_id = self.advance_journal
        self.assertFalse(emd_reconcile_batch_1.employee_domain_ids)

        # When creating a reconcile batches, show employees.
        employee_advance_payment = self.env['employee.advance.payment'].create({
            'emp_advance_id': employee_advance.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 300,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment.action_pay()

        emd_reconcile_batch_2 = Form(self.env['employee.advance.reconcile.batch'])
        emd_reconcile_batch_2.date = date(2021, 7, 10)
        emd_reconcile_batch_2.journal_id = self.advance_journal
        self.assertIn(self.employee_advance_manager_employee.id, emd_reconcile_batch_2.employee_domain_ids._get_ids())

        # Change the batch reconciliation creation date to be smaller than the advance date, don't show employees.
        emd_reconcile_batch_2.date = date(2021, 7, 1)
        self.assertFalse(emd_reconcile_batch_2.employee_domain_ids)

        # Change the batch reconciliation creation date to be larger than the advance date, show employees.
        emd_reconcile_batch_2.date = date(2021, 10, 30)
        self.assertIn(self.employee_advance_manager_employee.id, emd_reconcile_batch_2.employee_domain_ids._get_ids())
