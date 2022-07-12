from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestSaleOrderFollowersAccess(TestCommon):

    def setUp(self):
        super(TestSaleOrderFollowersAccess, self).setUp()

    def test_sales_access_right(self):
        # Test access right in user1 (group: "User: Own Documents Only")

        # test access right in sale.order
        with self.assertRaises(AccessError):
            self.sale_order1.with_user(self.user1).read(['name'])
        with self.assertRaises(AccessError):
            self.sale_order1.with_user(self.user1).name = 'test'
        with self.assertRaises(AccessError):
            self.sale_order1.with_user(self.user1).unlink()
        with self.assertRaises(AccessError):
            self.sale_order1.with_user(self.user1).message_post(body='Test 123', email_from='test@abc.xyz')

        # test access right in sale.order.line
        with self.assertRaises(AccessError):
            self.sale_order_line1.with_user(self.user1).read(['id'])
        with self.assertRaises(AccessError):
            self.sale_order_line1.with_user(self.user1).name = 'test'
        with self.assertRaises(AccessError):
            self.sale_order_line1.with_user(self.user1).unlink()

        # User admin add follower user1 to sale_order1
        self.sale_order1.message_subscribe(self.user1.partner_id.ids)

        # user1 has read permission and message_post after being added follower
        self.sale_order1.with_user(self.user1).read(['id'])
        self.sale_order_line1.with_user(self.user1).read(['id'])
        self.sale_order1.with_user(self.user1).message_post(body='2222', email_from='test@abc.xyz')

        with self.assertRaises(AccessError):
            self.sale_order1.with_user(self.user1).name = 'test'
        with self.assertRaises(AccessError):
            self.sale_order1.with_user(self.user1).unlink()
