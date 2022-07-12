from odoo.tests import tagged
from odoo.exceptions import AccessError

from odoo.tests.common import SingleTransactionCase


@tagged('post_install', '-at_install')
class TestAccountingEntryReportFlag(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountingEntryReportFlag, cls).setUpClass()
        cls.user_invoice = cls.env.ref('base.user_demo')
        cls.group_accounting_report_flag_manager_id = cls.env.ref('to_accounting_entry_report_flag.group_accounting_report_flag_manager').id
        # Create more account
        user_type_liquidity = cls.env.ref('account.data_account_type_liquidity')
        account_1 = cls.env['account.account'].create({
            'code': 'NC1115',
            'name': 'Liquidity Account1',
            'user_type_id': user_type_liquidity.id,
        })
        account_2 = cls.env['account.account'].create({
            'code': 'NC1116',
            'name': 'Liquidity Account2',
            'user_type_id': user_type_liquidity.id,
        })
        cls.acount_move = cls.env['account.move'].create({
            'legal_report_off': False,
            'move_type': 'entry',
            'line_ids': [
                (0, 0, {
                    'account_id': account_1.id,
                    'debit': 1000000,
                    'credit': 0.0
                }),
                (0, 0, {
                    'account_id': account_2.id,
                    'debit': 0.0,
                    'credit': 1000000
                })
            ]
        })

    def test_00_group_accounting_report_flag_manager(self):
        self.assertRaises(AccessError,
                          self.acount_move.with_user(self.user_invoice).write, {
                              'legal_report_off': True,
                          })
        self.assertRaises(AccessError,
                          self.acount_move.line_ids[0].with_user(self.user_invoice).write, {
                              'legal_report_off': True,
                          })
        # Only user have group_accounting_report_flag_manager can change legal_report_off
        self.user_invoice.write({
            'groups_id': [(4, self.group_accounting_report_flag_manager_id)],
        })

        self.acount_move.with_user(self.user_invoice).write({
            'legal_report_off': True,
        })
        self.acount_move.line_ids[0].with_user(self.user_invoice).write({
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
        try:
            self.acount_move.with_user(self.user_invoice).copy()
        except Exception:
            self.fail("Could not copy account move")
