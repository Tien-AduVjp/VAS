from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestHrContractActions(TransactionCase):

    def setUp(self):
        super(TestHrContractActions, self).setUp()
        self.hr_contract_test = self.env['hr.contract'].with_context(tracking_disable=True).create({
            'name': 'test',
            'state': 'draft',
            'wage': 1
        })

    def test_01_action_start_contract(self):
        self.hr_contract_test.action_start_contract()
        self.assertEqual(self.hr_contract_test.state, 'open', "to_hr_contract_actions: error action_start_contract")
        with self.assertRaises(UserError):
            self.hr_contract_test.action_start_contract()

    def test_02_action_to_renew(self):
        with self.assertRaises(UserError):
            self.hr_contract_test.action_to_renew()

        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.action_to_renew()
        self.assertEqual(self.hr_contract_test.kanban_state, 'blocked', "to_hr_contract_actions: error blocked")

    def test_03_set_as_close(self):
        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.set_as_close()
        self.assertEqual(self.hr_contract_test.state, 'close', "to_hr_contract_actions: error set_as_close")

    def test_04_action_renew(self):
        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.set_as_close()
        self.hr_contract_test.action_renew()
        self.assertEqual(self.hr_contract_test.state, 'open', "to_hr_contract_actions: error action_renew")

    def test_05_action_cancel(self):
        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.action_cancel()
        self.assertEqual(self.hr_contract_test.state, 'cancel', "to_hr_contract_actions: error action_cancel")

    def test_06_action_set_to_draft(self):
        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.action_cancel()
        self.hr_contract_test.action_set_to_draft()
        self.assertEqual(self.hr_contract_test.state, 'draft', "to_hr_contract_actions: error action_set_to_draft")
