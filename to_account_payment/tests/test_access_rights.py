from odoo.tests import tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestCommon):

    def test_access_payment_details(self):
        # Input: user belonging to the Billing group
        # Output: allow to "crud" account.payment.line
        user = self.env.ref('base.user_demo')
        user.groups_id = [(4, self.env.ref('account.group_account_invoice').id)]
        payment = self._create_payment('inbound').with_user(user)
        payment.read(['account_payment_line_ids'])
        payment.account_payment_line_ids[0].amount = 33
        payment.account_payment_line_ids.unlink()
