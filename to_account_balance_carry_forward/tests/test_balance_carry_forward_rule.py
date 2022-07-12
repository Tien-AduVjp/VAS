from odoo.tests import tagged
from odoo.exceptions import ValidationError

from .common import Common


@tagged('post_install', '-at_install')
class TestBalanceCarryForwardRule(Common):

    def test_01_balance_carry_foward_rule_account(self):
        """
        rule_511_to_911:   - source_account_ids: account_5111, account_5112
                            - dest_account_id: account_911
        account_5111, account_5112, account_911: base.main_company
        account_company2: company2

        """
        self.rule_511_to_911.source_account_type_categ_id = self.env.ref('account.data_account_type_receivable')
        self.assertEqual(self.rule_511_to_911.source_account_ids.mapped('user_type_id'), self.env.ref('account.data_account_type_receivable'))
        self.rule_511_to_911.source_account_type_categ_id = self.env.ref('account.data_account_type_revenue')
        # Can not forward the balance to the same account
        with self.assertRaises(ValidationError):
            self.rule_511_to_911.dest_account_id = self.account_5112
        # Can not forward balance for accounts in different companies
        with self.assertRaises(ValidationError):
            self.rule_511_to_911.dest_account_id = self.account_company2
        # Overlaps an exiting rule on source accounts
        with self.assertRaises(ValidationError):
            self.env['balance.carry.forward.rule'].create({
                    'name': 'New Rule',
                    'source_account_ids': [(6, 0, [self.account_5111.id])],
                    'dest_account_id': self.account_911.id,
                })

