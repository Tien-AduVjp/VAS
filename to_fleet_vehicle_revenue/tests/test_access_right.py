from odoo.tests.common import tagged
from odoo.exceptions import AccessError
from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):
    
    def test_01_access_right_fleet_vehicle_revenue(self):
        # test access right model fleet.vehicle.revenue, group fleet_vehicle_revenue_group_read
        self.fleet_vehicle_revenue_1.with_user(self.user_demo).read()
        with self.assertRaises(AccessError):
            self.env['fleet.vehicle.revenue'].with_user(self.user_demo).create({
                'vehicle_id': self.env.ref('fleet.vehicle_1').id
            })
        with self.assertRaises(AccessError):
            self.fleet_vehicle_revenue_1.with_user(self.user_demo).amount = 20
        with self.assertRaises(AccessError):
            self.fleet_vehicle_revenue_1.with_user(self.user_demo).unlink()

    def test_02_access_right_fleet_vehicle_revenue(self):
        # test access right model fleet.vehicle.revenue, group fleet.fleet_group_manager
        self.fleet_vehicle_revenue_1.with_user(self.user_admin).read()
        self.env['fleet.vehicle.revenue'].with_user(self.user_admin).create({
            'vehicle_id': self.env.ref('fleet.vehicle_1').id
        })
        self.fleet_vehicle_revenue_1.with_user(self.user_admin).amount = 20
        self.fleet_vehicle_revenue_1.with_user(self.user_admin).unlink()
