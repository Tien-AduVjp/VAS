from datetime import date

from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestBalanceCarryForward(Common):

    def test_01_balance_carry_forward_fiscalyear_last_month(self):
        self.env.company.fiscalyear_last_month = '12'
        rule_profit_lost = self.env['balance.carry.forward.rule'].create({
            'name': '911->4212',
            'source_account_ids': [(6, 0, [self.account_911.id])],
            'dest_account_id': self.account_4212.id,
            'profit_loss': True,
        })
        cfw = self.env['balance.carry.forward'].create({
            'date': date(2021, 8, 27),
            'journal_id': self.journal_bcf.id,
        })
        self.assertNotIn(rule_profit_lost, cfw.forward_rule_ids)
        cfw.date = date(2021, 12 , 27)
        self.assertIn(rule_profit_lost, cfw.forward_rule_ids)

    def test_02_balance_carry_forward_flow(self):
        cfw = self.env['balance.carry.forward'].create({
            'date': date(2021, 8, 19),
            'journal_id': self.journal_bcf.id,
        })
        # Until 19-8-2021, no journal item for source accounts have been created, so cannot confirm this cfw
        with self.assertRaises(UserError):
            cfw.action_confirm()
        cfw.date = date(2021, 8, 23)
        # Cannot post item which is in draft state
        with self.assertRaises(UserError):
            cfw.action_post()
        cfw.action_confirm()
        # cannot delete item which is in confirmed state
        with self.assertRaises(UserError):
            cfw.unlink()
        cfw.action_post()
        # cannot delete item which is in posted state
        with self.assertRaises(UserError):
            cfw.unlink()
        cfw.action_cancel()
        # Cannot confirm item which is in canceled state
        with self.assertRaises(UserError):
            cfw.action_confirm()
        # cannot delete item which is in canceled state
        with self.assertRaises(UserError):
            cfw.unlink()

    def test_03_balance_carry_forward_rule_line(self):
        """
        Input:
        - Journal Items: - 20-8-2021: N131 1000.0/ C5111 1000.0
                      - 23-9-2021: N521 300.0/ C131 300.0
        - rule_511_to_911: sequence 5
        - rule_521_to_5111: sequence 10
        Output:
        - Order of balance carry forwards: rule_511_to_911 -> rule_521_to_5111
        """
        # At 19-8-2021 balance: No balance
        cfw = self.env['balance.carry.forward'].create({
            'date': date(2021, 8, 19),
            'journal_id': self.journal_bcf.id,
            'forward_rule_ids': [(6, 0, [self.rule_511_to_911.id, self.rule_521_to_5111.id])]
        })
        self.assertRecordValues(cfw.forward_rule_line_ids, [
            {'source_account_id': self.account_5111.id, 'balance': 0.0, 'dest_account_id': self.account_911.id},
            {'source_account_id': self.account_5112.id, 'balance': 0.0, 'dest_account_id': self.account_911.id},
            {'source_account_id': self.account_521.id, 'balance': 0.0, 'dest_account_id': self.account_5111.id},
        ])
        # At 20-8-2021 balance: 5111 -1000.0, 521 no balance
        cfw.write({
            'date': date(2021, 8, 20),
            'forward_rule_ids': [(6, 0, [self.rule_511_to_911.id, self.rule_521_to_5111.id])]
        })
        self.assertRecordValues(cfw.forward_rule_line_ids, [
            {'source_account_id': self.account_5111.id, 'balance':-1000.0, 'dest_account_id': self.account_911.id},
            {'source_account_id': self.account_5112.id, 'balance': 0.0, 'dest_account_id': self.account_911.id},
            {'source_account_id': self.account_521.id, 'balance': 0.0, 'dest_account_id': self.account_5111.id},
        ])
        # At 23-8-2023 balance: 5111 -1000, 521 300
        cfw.write({
            'date': date(2021, 8, 23),
            'forward_rule_ids': [(6, 0, [self.rule_511_to_911.id, self.rule_521_to_5111.id])]
        })
        self.assertRecordValues(cfw.forward_rule_line_ids, [
            {'source_account_id': self.account_5111.id, 'balance':-1000.0, 'dest_account_id': self.account_911.id},
            {'source_account_id': self.account_5112.id, 'balance': 0.0, 'dest_account_id': self.account_911.id},
            {'source_account_id': self.account_521.id, 'balance': 300, 'dest_account_id': self.account_5111.id},
        ])
        # Generate Journal items after confirm
        cfw.action_confirm()
        self.assertRecordValues(cfw.aml_ids, [
            {'account_id': self.account_5111.id, 'debit': 1000.0, 'credit': 0.0},
            {'account_id': self.account_911.id, 'debit': 0.0, 'credit': 1000.0},
            {'account_id': self.account_5111.id, 'debit': 300.0, 'credit': 0.0},
            {'account_id': self.account_521.id, 'debit': 0.0, 'credit': 300.0},
        ])
        for move in cfw.account_move_ids:
            self.assertEqual(move.state, 'draft')
        cfw.action_post()
        for move in cfw.account_move_ids:
            self.assertEqual(move.state, 'posted')
        # Remove Journal items after cancel
        cfw.action_cancel()
        self.assertFalse(cfw.account_move_ids)
        self.assertFalse(cfw.aml_ids)

    def test_04_balance_carry_forward_succeeding_rule(self):
        """
        Input:
        - Journal Items: - 20-8-2021: N131 1000.0/ C5111 1000.0
                      - 23-9-2021: N521 300.0/ C131 300.0
        - rule_511_to_911: sequence 5
        - rule_521_to_5111: sequence 10
        - Change succeeding rule of rule_521_to_5111 to rule_511_to_911
        Output:
        - Order of balance carry forwards: rule_521_to_5111 -> rule_511_to_911
        """
        self.rule_521_to_5111.succeeding_rule_id = self.rule_511_to_911
        cfw = self.env['balance.carry.forward'].create({
            'date': date(2021, 8, 25),
            'journal_id': self.journal_bcf.id,
            'forward_rule_ids': [(6, 0, [self.rule_521_to_5111.id, self.rule_511_to_911.id])]
        })
        self.assertRecordValues(cfw.forward_rule_line_ids, [
            {'source_account_id': self.account_521.id, 'balance': 300.0, 'dest_account_id': self.account_5111.id},
            {'source_account_id': self.account_5111.id, 'balance':-1000.0, 'dest_account_id': self.account_911.id},
            {'source_account_id': self.account_5112.id, 'balance': 0.0, 'dest_account_id': self.account_911.id},
        ])
        cfw.action_confirm()
        self.assertRecordValues(cfw.aml_ids, [
            {'account_id': self.account_5111.id, 'debit': 300.0, 'credit': 0.0},
            {'account_id': self.account_521.id, 'debit': 0.0, 'credit': 300.0},
            {'account_id': self.account_5111.id, 'debit': 700.0, 'credit': 0.0},
            {'account_id': self.account_911.id, 'debit': 0.0, 'credit': 700.0},
        ])

