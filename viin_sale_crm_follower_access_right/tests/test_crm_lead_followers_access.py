from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestCrmLeadFollowersAccess(TestCommon):

    def setUp(self):
        super(TestCrmLeadFollowersAccess, self).setUp()

    def test_crm_lead_follower_access_right(self):
        with self.assertRaises(AccessError):
            self.crm_lead1.with_user(self.user1).read(['name'])
        with self.assertRaises(AccessError):
            self.crm_lead1.with_user(self.user1).name = 'test'
        with self.assertRaises(AccessError):
            self.crm_lead1.with_user(self.user1).unlink()
        with self.assertRaises(AccessError):
            self.crm_lead1.with_user(self.user1).message_post(body='Test 123', email_from='test@abc.xyz')

        self.crm_lead1.sudo().message_subscribe(self.user1.partner_id.ids)

        self.crm_lead1.with_user(self.user1).read(['name'])
        self.crm_lead1.with_user(self.user1).message_post(body='2222', email_from='test@abc.xyz')

        with self.assertRaises(AccessError):
            self.crm_lead1.with_user(self.user1).name = 'test'
        with self.assertRaises(AccessError):
            self.crm_lead1.with_user(self.user1).unlink()
