from odoo.tests.common import tagged
from odoo.exceptions import UserError
from .common import Common


class TestFleetVehicleRevenue(Common):
    
    def test_01_set_odometer(self):
        with self.assertRaises(UserError):
            self.fleet_vehicle_revenue_1.odometer = 0
        
    def test_02_set_odometer(self):
        self.assertFalse(self.fleet_vehicle_revenue_1.odometer_id)
        self.fleet_vehicle_revenue_1.odometer = 1
        self.assertTrue(self.fleet_vehicle_revenue_1.odometer_id)
