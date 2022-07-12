from psycopg2 import IntegrityError
from odoo.tools import mute_logger
from odoo.tests.common import tagged
from .common import FleetDriverJobWageCommon


@tagged('post_install', '-at_install')
class TestFleetFuelPrice(FleetDriverJobWageCommon):

    def test_1_validate_fleet_fuel_price(self):
        """ test case 1
            Create fuel price on 16 Sep, then we can't create fuel price again on 16 Sep"""
        self.env['fleet.fuel.price'].create({
            'date': "2021-9-16",
            'price_per_liter': 16000,
        })
        with mute_logger('odoo.sql_db'):
            with self.assertRaises(IntegrityError):
                self.env['fleet.fuel.price'].create({
                    'date': "2021-9-16",
                    'price_per_liter': 25000,
                })

    def test_2_compute_fuel_price(self):
        """ Test case 2"""
        self.trip_1.action_confirm()
        self.assertEqual(self.trip_1.fuel_price_id.price_per_liter, 0, "to_fleet_driver_job_wage: error compute fuel price")

        self.setUP_fuel_price()

        self.trip_1.write({'expected_start_date':'2021-09-13 12:00:00'})
        self.trip_1.flush()
        self.assertEqual(self.trip_1.fuel_price_id.price_per_liter, 0, "to_fleet_driver_job_wage: error compute fuel price")

        self.trip_1.write({'expected_start_date':'2021-09-14 12:00:00'})
        self.trip_1.flush()
        self.assertEqual(self.trip_1.fuel_price_id.price_per_liter, 14000, "to_fleet_driver_job_wage: error compute fuel price")

        self.trip_1.write({'expected_start_date':'2021-09-30 12:00:00'})
        self.trip_1.flush()
        self.assertEqual(self.trip_1.fuel_price_id.price_per_liter, 15000, "to_fleet_driver_job_wage: error compute fuel price")
