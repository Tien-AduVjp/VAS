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
        self.assertEquals(self.hr_contract_test.state, 'open')
        with self.assertRaises(UserError):
            self.hr_contract_test.action_start_contract()

    def test_02_action_to_renew(self):
        with self.assertRaises(UserError):
            self.hr_contract_test.action_to_renew()

        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.action_to_renew()
        self.assertEquals(self.hr_contract_test.kanban_state, 'blocked')

    def test_03_set_as_close(self):
        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.set_as_close()
        self.assertEquals(self.hr_contract_test.state, 'close')

    def test_04_action_renew(self):
        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.set_as_close()
        self.hr_contract_test.action_renew()
        self.assertEquals(self.hr_contract_test.state, 'open')

    def test_05_action_cancel(self):
        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.action_cancel()
        self.assertEquals(self.hr_contract_test.state, 'cancel')

    def test_06_action_set_to_draft(self):
        self.hr_contract_test.action_start_contract()
        self.hr_contract_test.action_cancel()
        self.hr_contract_test.action_set_to_draft()
        self.assertEquals(self.hr_contract_test.state, 'draft')
