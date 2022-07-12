from odoo.tests import tagged
from odoo.exceptions import AccessError

from odoo.addons.account.tests.account_test_no_chart import TestAccountNoChartCommon


@tagged('post_install', '-at_install')
class TestAccountingEntryReportFlag(TestAccountNoChartCommon):

    @classmethod
    def setUpClass(cls):
        super(TestAccountingEntryReportFlag, cls).setUpClass()
        cls.setUpUsers()
        cls.setUpAdditionalAccounts()
        cls.setUpAccountJournal()
        group_accounting_report_flag_manager_id = cls.env.ref('to_accounting_entry_report_flag.group_accounting_report_flag_manager').id
        group_account_invoice_id = cls.env.ref('account.group_account_invoice').id

        cls.user_manager.write({
            'groups_id': [(6, 0, [group_account_invoice_id, group_accounting_report_flag_manager_id])],
        })
        cls.user_employee.write({
            'groups_id': [(6, 0, [group_account_invoice_id])],
        })
        cls.acount_move = cls.env['account.move'].create({
            'user_id': cls.user_manager.id,
            'legal_report_off': False,
            'journal_id': cls.journal_sale.id,
            'company_id': cls.env.company.id,
            'line_ids': [
                (0, 0, {
                    'account_id': cls.account_expense.id,
                    'partner_id': cls.partner_customer_usd.id,
                    'debit': 1000000,
                    'credit': 0.0
                }),
                (0, 0, {
                    'account_id': cls.account_revenue.id,
                    'partner_id': cls.partner_customer_usd.id,
                    'debit': 0.0,
                    'credit': 1000000
                })
            ]
        })

    def test_00_group_accounting_report_flag_manager(self):
        # Only user have group_accounting_report_flag_manager can change legal_report_off
        self.acount_move.with_user(self.user_manager).write({
            'legal_report_off': True,
        })
        self.acount_move.line_ids[0].with_user(self.user_manager).write({
            'legal_report_off': True,
        })
        self.assertRaises(AccessError,
                          self.acount_move.with_user(self.user_employee).write, {
                              'legal_report_off': True,
                          })
        self.assertRaises(AccessError,
                          self.acount_move.line_ids[0].with_user(self.user_employee).write, {
                              'legal_report_off': True,
                          })

    def test_01_action_flag_report_off_account_move(self):
        self.acount_move.action_flag_report_off()
        self.assertEqual(self.acount_move.legal_report_off, True,
                         "to_accounting_entry_report_flag: account_move action_flag_report_off not worked")

    def test_02_action_flag_report_on_account_move(self):
        self.acount_move.action_flag_report_on()
        self.assertEqual(self.acount_move.legal_report_off, False,
                         "to_accounting_entry_report_flag: account_move action_flag_report_on not worked")

    def test_03_action_flag_report_off_account_move_line(self):
        self.acount_move.line_ids[0].action_flag_report_off()
        self.assertEqual(self.acount_move.line_ids[0].legal_report_off, True,
                         "to_accounting_entry_report_flag: account_move action_flag_report_off not worked")

    def test_04_action_flag_report_on_account_move_line(self):
        self.acount_move.line_ids[0].action_flag_report_on()
        self.assertEqual(self.acount_move.line_ids[0].legal_report_off, False,
                         "to_accounting_entry_report_flag: account_move action_flag_report_on not worked")

    def test_05_copy_account_move(self):
        self.acount_move.with_user(self.user_employee).copy()
