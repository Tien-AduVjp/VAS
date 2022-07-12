from datetime import date, datetime
from odoo.tests.common import tagged
from odoo.exceptions import ValidationError, UserError
from .common import Common


@tagged('-at_install', 'post_install')
class TestEmployeeAdvance(Common):

    def setUp(self):
        super(TestEmployeeAdvance, self).setUp()
        self.employee_advance_approver_employee.write({
            'address_home_id': self.employee_advance_approver_partner.id
        })
        self.employee_advance_employee.write({
            'address_home_id': self.employee_advance_partner.id
        })

    def test_01_check_account_journal(self):
        """
        Automatically create employee advance journal
        """
        self.assertEqual(len(self.advance_journal), 1, "Employee advance journal doesn't exist")
        self.assertEqual(self.advance_journal.type, 'general', "Employee advance journal isn't of general type")

    def test_11_check_amount_total(self):
        """
        Creating an advance with a total sum of 0 was unsuccessful.
        """
        with self.assertRaises(ValidationError):
            employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
                'employee_id': self.employee_advance_manager_employee.id,
            })
            employee_advance.amount

    def test_12_check_amount_total(self):
        """
        Creating an advance with a total sum of 0 was unsuccessful.
        """
        with self.assertRaises(ValidationError):
            employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
                'employee_id': self.employee_advance_manager_employee.id,
                'lines': [(0, 0, {
                    'name': 'Advance Line 1',
                    'amount': 0
                    })]
            })
            employee_advance.amount

    def test_31_pay_employee_advance(self):
        # Generate journal entries after approval
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

        # Generate journal entries after pay
        employee_advance_payment = self.env['employee.advance.payment'].create({
            'emp_advance_id': employee_advance.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 300,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment.action_pay()
        self._check_account_move_line(employee_advance.payment_ids.move_id.line_ids,
                                      self.account_receivable.code, 300,
                                      self.cash_journal.payment_credit_account_id.code, 300)

    def test_41_validate_employee_advance_reconcile(self):
        account_date = datetime(2021, 7, 10, 12, 0)
        with self.patch_datetime_now(account_date), self.patch_date_today(account_date), self.patch_date_context_today(account_date):
            # After approval, double-check the employee advance reconciliation lines
            employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
                'employee_id': self.employee_advance_manager_employee.id,
                'date': account_date.date(),
                'journal_id': self.advance_journal.id,
                'lines': [(0, 0, {
                    'name': 'Advance Line 1',
                    'amount': 100
                })]
            })
            employee_advance.action_confirm()
            employee_advance.action_approve()

            employee_advance_reconcile = self.env['employee.advance.reconcile'].with_context(tracking_disable=True).create({
                'employee_id': self.employee_advance_manager_employee.id,
                'date': account_date.date(),
                'journal_id': self.advance_journal.id,
            })
            self.assertFalse(employee_advance_reconcile.line_db_ids)
            self.assertFalse(employee_advance_reconcile.line_cr_ids)
            self.assertEqual(employee_advance_reconcile.balance, 0)

            # After pay, double-check the employee advance reconciliation lines
            employee_advance_payment = self.env['employee.advance.payment'].create({
                'emp_advance_id': employee_advance.id,
                'journal_id': self.cash_journal.id,
                'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
                'amount': 100,
                'payment_date': account_date.date(),
            })
            employee_advance_payment.action_pay()

            employee_advance_reconcile.action_compute_data_line()
            self.assertEqual(employee_advance_reconcile.line_db_ids[:1].amount, 100)
            self.assertEqual(employee_advance_reconcile.balance, 100)

            # After altering the reconciliation date, double-check the employee advance reconciliation lines
            employee_advance_reconcile.date = date(2021, 1, 7)
            self.assertFalse(employee_advance_reconcile.line_db_ids)
            self.assertFalse(employee_advance_reconcile.line_cr_ids)
            self.assertEqual(employee_advance_reconcile.balance, 0)

            # Check the employee advance reconciliation lines when the expense entry entry is less than the advance
            account_move_1 = self.env['account.move'].create({
                'date': account_date.date(),
                'journal_id': self.misc_journal.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.account_expenses.id,
                        'debit': 50,
                        'credit': 0,
                    }),
                    (0, 0, {
                        'account_id': self.account_receivable.id,
                        'debit': 0,
                        'credit': 50,
                        'partner_id': self.employee_advance_manager_partner.id
                    })
                ]
            })
            account_move_1.action_post()
            employee_advance_reconcile.date = account_date.date()
            self.assertEqual(employee_advance_reconcile.line_db_ids[:1].amount, 100)
            self.assertEqual(employee_advance_reconcile.line_cr_ids[:1].amount, 50)
            self.assertEqual(employee_advance_reconcile.balance, 50)

            # Check the employee advance reconciliation lines when recording expenses in advance
            account_move_2 = self.env['account.move'].create({
                'date': account_date.date(),
                'journal_id': self.misc_journal.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.account_expenses.id,
                        'debit': 50,
                        'credit': 0,
                    }),
                    (0, 0, {
                        'account_id': self.account_receivable.id,
                        'debit': 0,
                        'credit': 50,
                        'partner_id': self.employee_advance_manager_partner.id
                    })
                ]
            })
            account_move_2.action_post()
            employee_advance_reconcile.action_compute_data_line()
            self.assertEqual(employee_advance_reconcile.line_db_ids[:1].amount, 100)
            self.assertEqual(employee_advance_reconcile.line_cr_ids[0].amount, 50)
            self.assertEqual(employee_advance_reconcile.line_cr_ids[1].amount, 50)
            self.assertEqual(employee_advance_reconcile.balance, 0)

            # Check the employee advance reconciliation lines when recording the advance large expense entry
            account_move_3 = self.env['account.move'].create({
                'date': account_date.date(),
                'journal_id': self.misc_journal.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.account_expenses.id,
                        'debit': 50,
                        'credit': 0,
                    }),
                    (0, 0, {
                        'account_id': self.account_receivable.id,
                        'debit': 0,
                        'credit': 50,
                        'partner_id': self.employee_advance_manager_partner.id
                    })
                ]
            })
            account_move_3.action_post()
            employee_advance_reconcile.action_compute_data_line()
            self.assertEqual(employee_advance_reconcile.line_db_ids[:1].amount, 100)
            self.assertEqual(employee_advance_reconcile.line_cr_ids[0].amount, 50)
            self.assertEqual(employee_advance_reconcile.line_cr_ids[1].amount, 50)
            self.assertEqual(employee_advance_reconcile.line_cr_ids[2].amount, 50)
            self.assertEqual(employee_advance_reconcile.balance, 50)

            employee_advance_reconcile.action_confirm()
            advance_payment_register_1 = self.env['employee.advance.payment'].create({
                'employee_advance_reconcile_id': employee_advance_reconcile.id,
                'amount': 30
            })
            advance_payment_register_1.action_pay()
            self.assertEqual(employee_advance_reconcile.state, 'confirm')

            advance_payment_register_2 = self.env['employee.advance.payment'].create({
                'employee_advance_reconcile_id': employee_advance_reconcile.id,
                'amount': 20
            })
            advance_payment_register_2.action_pay()
            self.assertEqual(employee_advance_reconcile.state, 'done')

    def test_51_check_payment(self):
        """
        Make a payment to acknowledge an overabundance of funds
        """
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 200
            })]
        })
        employee_advance.action_confirm()
        employee_advance.action_approve()
        employee_advance_payment = self.env['employee.advance.payment'].create({
            'emp_advance_id': employee_advance.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 200,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment.action_pay()
        account_date = datetime(2021, 7, 10, 12, 0)
        with self.patch_datetime_now(account_date), self.patch_date_today(account_date), self.patch_date_context_today(account_date):
            account_move = self.env['account.move'].create({
                'date': account_date.date(),
                'journal_id': self.misc_journal.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.account_expenses.id,
                        'debit': 50,
                        'credit': 0,
                    }),
                    (0, 0, {
                        'account_id': self.account_receivable.id,
                        'debit': 0,
                        'credit': 50,
                        'partner_id': self.employee_advance_partner.id
                    })
                ]
            })
            account_move.action_post()
        employee_advance_reconcile = self.env['employee.advance.reconcile'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
        })
        employee_advance_reconcile.action_confirm()
        employee_advance_payment = self.env['employee.advance.payment'].create({
            'employee_advance_reconcile_id': employee_advance_reconcile.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 150,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment.action_pay()
        self.assertEqual(employee_advance_reconcile.payment_ids[:1].amount, 150)
        self.assertEqual(employee_advance_reconcile.balance, 0)

    def test_52_check_payment(self):
        """
        Make a payment that acknowledges a lack of foresight.
        """
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 200
            })]
        })
        employee_advance.action_confirm()
        employee_advance.action_approve()
        employee_advance_payment = self.env['employee.advance.payment'].create({
            'emp_advance_id': employee_advance.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 200,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment.action_pay()
        account_date = datetime(2021, 7, 10, 12, 0)
        with self.patch_datetime_now(account_date), self.patch_date_today(account_date), self.patch_date_context_today(account_date):
            account_move = self.env['account.move'].create({
                'date': account_date.date(),
                'journal_id': self.misc_journal.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.account_expenses.id,
                        'debit': 250,
                        'credit': 0,
                    }),
                    (0, 0, {
                        'account_id': self.account_receivable.id,
                        'debit': 0,
                        'credit': 250,
                        'partner_id': self.employee_advance_partner.id
                    })
                ]
            })
            account_move.action_post()
        employee_advance_reconcile = self.env['employee.advance.reconcile'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
        })
        employee_advance_reconcile.action_confirm()
        employee_advance_payment = self.env['employee.advance.payment'].create({
            'employee_advance_reconcile_id': employee_advance_reconcile.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 50,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment.action_pay()
        with self.assertRaises(ValidationError):
            account_move.button_draft()
        self.assertEqual(employee_advance_reconcile.payment_ids[:1].amount, 50)
        self.assertEqual(employee_advance_reconcile.balance, 0)

    def test_53_check_payment(self):
        """
        Make a payment that acknowledges a lack of foresight.
        """
        account_date = datetime(2021, 7, 10, 12, 0)
        with self.patch_datetime_now(account_date), self.patch_date_today(account_date), self.patch_date_context_today(account_date):
            self.account_receivable_origin = self.accounts.filtered(lambda a: a.code == '121000')
            account_move = self.env['account.move'].create({
                'date': account_date.date(),
                'journal_id': self.advance_journal.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.account_receivable.id,
                        'debit': 0,
                        'credit': 100,
                        'partner_id': self.employee_advance_partner.id,
                    }),
                    (0, 0, {
                        'account_id': self.account_receivable_origin.id,
                        'debit': 100,
                        'credit': 0,
                        'partner_id': self.employee_advance_partner.id,
                    })
                ]
            })
            account_move.action_post()

            employee_advance_reconcile = self.env['employee.advance.reconcile'].with_context(tracking_disable=True).create({
                'employee_id': self.employee_advance_employee.id,
                'date': date(2021, 7, 10),
                'journal_id': self.advance_journal.id,
            })
            self.assertEqual(employee_advance_reconcile.line_cr_ids[0].amount, 100)

            with self.assertRaises(UserError):
                employee_advance_reconcile.action_confirm()

    def test_61_validate_reconcile_batches(self):
        """
        Create batch reconciliation
        """
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        employee_advance.action_confirm()
        employee_advance.action_approve()
        employee_advance_payment = self.env['employee.advance.payment'].create({
            'emp_advance_id': employee_advance.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 300,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment.action_pay()
        emd_reconcile_batch = self.env['employee.advance.reconcile.batch'].create({
            'employee_ids': [(6, 0, self.employee_advance_employee.ids)],
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
        })
        emd_reconcile_batch.action_create()
        employee_advance_reconcile = self.env['employee.advance.reconcile'].search([('employee_id', '=', self.employee_advance_employee.id)], limit=1)
        self.assertEqual(len(employee_advance_reconcile), 1)
        self.assertEqual(employee_advance_reconcile.state, 'draft')

    def test_62_validate_reconcile_batches(self):
        """
        Batch reconciliation for multiple employees
        """
        employee_advance_1 = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 100
            })]
        })
        employee_advance_1.action_confirm()
        employee_advance_1.action_approve()

        employee_advance_2 = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_approver_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 200
            })]
        })
        employee_advance_2.action_confirm()
        employee_advance_2.action_approve()

        employee_advance_payment_1 = self.env['employee.advance.payment'].create({
            'emp_advance_id': employee_advance_1.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 100,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment_1.action_pay()
        employee_advance_payment_2 = self.env['employee.advance.payment'].create({
            'emp_advance_id': employee_advance_2.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 200,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment_2.action_pay()

        emd_reconcile_batch = self.env['employee.advance.reconcile.batch'].create({
            'employee_ids': [(6, 0, [self.employee_advance_employee.id, self.employee_advance_approver_employee.id])],
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
        })
        emd_reconcile_batch.action_create()
        employee_advance_reconcile_1 = self.env['employee.advance.reconcile'].search([('employee_id', '=', self.employee_advance_employee.id)], limit=1)
        employee_advance_reconcile_2 = self.env['employee.advance.reconcile'].search([('employee_id', '=', self.employee_advance_approver_employee.id)], limit=1)
        self.assertEqual(len(employee_advance_reconcile_1), 1)
        self.assertEqual(employee_advance_reconcile_1.state, 'draft')
        self.assertEqual(len(employee_advance_reconcile_2), 1)
        self.assertEqual(employee_advance_reconcile_2.state, 'draft')

    def test_71_check_double_validation(self):
        self.env.company.amount_double_validation = 100

        # Does not have the right to approve advances for non-subordinate employees
        employee_advance_1 = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 150
            })]
        })
        employee_advance_1.with_user(self.employee_advance_approver_user).action_confirm()
        with self.assertRaises(UserError):
            employee_advance_1.with_user(self.employee_advance_approver_user).action_approve()

        self.employee_advance_employee.write({
            'parent_id': self.employee_advance_approver_employee.id
        })

        # No need to appraise employee advances twice for lower-level employees when the approver is a person with management rights
        employee_advance_2 = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 150
            })]
        })
        employee_advance_2.action_confirm()
        employee_advance_2.action_approve()
        self.assertEqual(employee_advance_2.state, 'validate')

        # No need to appraise employee advance twice for junior employees with the advance amount smaller than the minimum value to be appraised.
        employee_advance_3 = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 50
            })]
        })
        employee_advance_3.with_user(self.employee_advance_approver_user).action_confirm()
        employee_advance_3.with_user(self.employee_advance_approver_user).action_approve()
        self.assertEqual(employee_advance_3.state, 'validate')

        # Appraisal of 2 successful employee advances for junior employees
        employee_advance_4 = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 150
            })]
        })
        employee_advance_4.with_user(self.employee_advance_approver_user).action_confirm()
        employee_advance_4.with_user(self.employee_advance_approver_user).action_approve()
        self.assertEqual(employee_advance_4.state, 'validate1')

    def test_71_unlink_employee_advance(self):
        """
        Delete employee advance in draft status
        """
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 150
            })]
        })
        employee_advance.unlink()

    def test_72_unlink_employee_advance(self):
        """
        Unable to delete advance in status other than draft
        """
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 150
            })]
        })
        employee_advance.action_confirm()
        with self.assertRaises(UserError):
            employee_advance.unlink()
        employee_advance.action_approve()
        with self.assertRaises(UserError):
            employee_advance.unlink()

    def test_81_check_infor_in_employee_advance(self):
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        self.assertFalse(employee_advance.job_id)
        self.assertFalse(employee_advance.department_id)

        department = self.env['hr.department'].create({
            'name': 'Sale',
        })
        job = self.env['hr.job'].create({
            'name': 'Sale',
            'department_id': department.id,
            'no_of_recruitment': 5,
        })
        self.employee_advance_employee.write({
            'department_id': department.id,
            'job_id': job.id,
        })
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 300
            })]
        })
        self.assertEqual(employee_advance.job_id, self.employee_advance_employee.job_id)
        self.assertEqual(employee_advance.department_id, self.employee_advance_employee.department_id)

        self.assertEqual(employee_advance.currency_id, self.employee_advance_employee.company_id.currency_id)

    def test_91_check_has_outstanding_payment_and_payment_state(self):
        """
        Check compute_has_outstanding_payment, payment_state in employee_advance model
        """
        employee_advance = self.env['employee.advance'].with_context(tracking_disable=True).create({
            'employee_id': self.employee_advance_employee.id,
            'date': date(2021, 7, 10),
            'journal_id': self.advance_journal.id,
            'lines': [(0, 0, {
                'name': 'Advance Line 1',
                'amount': 150
            })]
        })
        self.assertFalse(employee_advance.has_outstanding_payment)
        self.assertEqual(employee_advance.payment_state, 'not_paid')

        employee_advance.action_confirm()
        employee_advance.action_approve()
        employee_advance_payment = self.env['employee.advance.payment'].create({
            'emp_advance_id': employee_advance.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 100,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment.action_pay()
        self.assertFalse(employee_advance.has_outstanding_payment)
        self.assertEqual(employee_advance.payment_state, 'partial')

        employee_advance_payment_1 = self.env['employee.advance.payment'].create({
            'emp_advance_id': employee_advance.id,
            'journal_id': self.cash_journal.id,
            'payment_method_id': self.cash_journal.outbound_payment_method_ids[0].id,
            'amount': 50,
            'payment_date': date(2021, 7, 10),
        })
        employee_advance_payment_1.action_pay()
        self.assertFalse(employee_advance.has_outstanding_payment)
        self.assertEqual(employee_advance.payment_state, 'paid')

        employee_advance.action_refuse()
        self.assertTrue(employee_advance.has_outstanding_payment)
        self.assertEqual(employee_advance.payment_state, 'not_paid')

        account_payments = self.env['account.payment'].search([
            ('employee_advance_id', '=', employee_advance.id),
            ('journal_id', '=', self.cash_journal.id),
            ('employee_id', '=', employee_advance.employee_id.id)
        ])
        account_payments.action_post()
        self.assertFalse(employee_advance.has_outstanding_payment)
        self.assertEqual(employee_advance.payment_state, 'not_paid')

        employee_advance.action_confirm()
        employee_advance.action_approve()
        self.assertFalse(employee_advance.has_outstanding_payment)
        self.assertEqual(employee_advance.payment_state, 'paid')

    def test_92_check_has_outstanding_payment(self):
        """
        Check compute_has_outstanding_payment in employee_advance_reconcile model
        """
