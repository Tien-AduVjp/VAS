from odoo.tests.common import tagged
from .common import FleetDriverJobWageCommon


@tagged('post_install', '-at_install')
class TestFleetVehiceTrip(FleetDriverJobWageCommon):

    @classmethod
    def setUpClass(cls):
        super(TestFleetVehiceTrip, cls).setUpClass()
        cls.setUP_fuel_price()

    def test_31_trip_match_a_wage_definition(self):
        # Trip match fl_job_wage_di_1
        self.trip_1.action_confirm()
        self.assertEqual(self.trip_1.fuel_based_job_wage, 15 * 15000, "to_fleet_driver_job_wage: error compute fuel_based_job_wage")
        self.assertEqual(self.trip_1.job_allowance, 100000, "to_fleet_driver_job_wage: error compute fuel_based_job_wage")

    def test_32_trip_not_match_any_wage_definition(self):
        # Trip not match any wage definition
        self.trip_1.write({'route_id':self.route_2.id})
        self.trip_1.action_confirm()
        self.assertEqual(self.trip_1.fuel_based_job_wage, 0, "to_fleet_driver_job_wage: error compute fuel_based_job_wage")
        self.assertEqual(self.trip_1.job_allowance, 0, "to_fleet_driver_job_wage: error compute fuel_based_job_wage")

    def test_33_trip_match_many_wage_definition(self):
        # Trip match many wage definition
        self.fl_job_wage_di_new = self.env['fleet.job.wage.definition'].create({
            'route_id': self.route_1.id,
            'vehicle_id': self.env.ref('fleet.vehicle_1').id,
            'consumption': 20,
            'allowance': 200000,
            'fleet_service_type_id': self.env.ref('fleet.type_service_service_1').id,
        })
        self.trip_1.action_confirm()
        self.assertEqual(self.trip_1.fuel_based_job_wage, 15 * 15000, "to_fleet_driver_job_wage: error compute fuel_based_job_wage")
        self.assertEqual(self.trip_1.job_allowance, 100000, "to_fleet_driver_job_wage: error compute fuel_based_job_wage")
