from odoo.tests.common import tagged
from odoo.exceptions import AccessError
from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):

    def test_biling_user_access_right(self):
        """ Test access right: group `account.group_account_invoice`, model: `fleet.vehicle.revenue`
        """
        self.user_demo.groups_id = [(6, 0, [self.env.ref('account.group_account_invoice').id])]
        self.create_fleet_vehicle_revenue_from_invoice_line(self.invoice1.invoice_line_ids[0], self.vehicle1)
        vehicle_revenue1 = self.invoice1.fleet_vehicle_revenue_ids

        with self.assertRaises(AccessError):
            vehicle_revenue1.with_user(self.user_demo).read(['id'])
        with self.assertRaises(AccessError):
            vehicle_revenue1.with_user(self.user_demo).amount = 100
        with self.assertRaises(AccessError):
            vehicle_revenue1.with_user(self.user_demo).unlink()

        vehicle_revenue2 = self.env['fleet.vehicle.revenue'].with_user(self.user_demo).create({
            'vehicle_id': self.vehicle1.id
        })
        vehicle_revenue2.with_user(self.user_demo).read(['id'])
        vehicle_revenue2.with_user(self.user_demo).amount = 100
        vehicle_revenue2.with_user(self.user_demo).unlink()

    def test_account_user_access_right(self):
        """ Test access right: group `account.group_account_user`, model: `fleet.vehicle.revenue`
        """
        self.user_demo.groups_id = [(6, 0, [self.env.ref('account.group_account_user').id])]
        self.create_fleet_vehicle_revenue_from_invoice_line(self.invoice1.invoice_line_ids[0], self.vehicle1)
        vehicle_revenue1 = self.invoice1.fleet_vehicle_revenue_ids

        vehicle_revenue1.with_user(self.user_demo).read(['id'])
        vehicle_revenue1.with_user(self.user_demo).amount = 100
        vehicle_revenue1.with_user(self.user_demo).unlink()
