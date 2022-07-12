from psycopg2 import IntegrityError

from odoo.tests.common import tagged, Form
from odoo.tools import mute_logger
from odoo.exceptions import UserError, ValidationError

from .common import Common


@tagged('post_install', '-at_install')
class TestToFleetAccountingFleetOperationRevenue(Common):

    def test_01_record_revenue_from_vehicle_trip(self):
        # case 1:
        """ Test record revenue from vehicle trip, amount = 0 """
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.record_revenue_from_trip(self.vehicle_trip1, 0)

    def test_02_record_revenue_from_vehicle_trip(self):
        # case 2.3:
        """ Test method _onchange_revenue_subtype_id """
        wizard_form = Form(self.env['vehicle.trip.register.revenue.wizard']\
                        .with_context(active_id=self.vehicle_trip1.id))
        wizard_form.revenue_subtype_id = self.service_type1
        self.assertEqual(wizard_form.product_id, self.service_type1.product_id)

    def test_03_record_revenue_from_vehicle_trip(self):
        # case 3:
        """ Test record revenue from vehicle trip without `trip_section_id` and `trip_waypoint_id`
            (Test method `_check_contrains_trip_waypoint_id_trip_section_id`)
        """
        with self.assertRaises(UserError):
            self.record_revenue_from_trip(self.vehicle_trip1, 10, trip_section_id=False, trip_waypoint_id=False)

    def test_04_record_revenue_from_vehicle_trip(self):
        # case 4:
        """ Test record revenue from vehicle trip without `revenue_subtype_id` and `product_id`
            Expect: record revenue successfully.
        """
        self.assertFalse(self.vehicle_trip1.fleet_vehicle_revenue_ids)
        self.record_revenue_from_trip(self.vehicle_trip1, 10, revenue_subtype_id=False, product_id=False)
        self.assertTrue(self.vehicle_trip1.fleet_vehicle_revenue_ids)

        self.assertFalse(self.vehicle_trip1.fleet_vehicle_revenue_ids.revenue_subtype_id)
        self.assertFalse(self.vehicle_trip1.fleet_vehicle_revenue_ids.product_id)

    def test_05_record_revenue_from_vehicle_trip(self):
        # case 5:
        """ Test record revenue from vehicle trip with fields: `trip_section_id` and `trip_waypoint_id` have value
            Expect: record revenue successfully.
        """
        self.assertFalse(self.vehicle_trip1.fleet_vehicle_revenue_ids)
        self.record_revenue_from_trip(self.vehicle_trip1, 10,
            revenue_subtype_id=self.service_type1.id, product_id=self.env.ref('product.product_order_01').id
        )
        self.assertTrue(self.vehicle_trip1.fleet_vehicle_revenue_ids)
        vehicle_revenue = self.vehicle_trip1.fleet_vehicle_revenue_ids
        self.assertEqual(vehicle_revenue.revenue_subtype_id, self.service_type1)
        self.assertEqual(vehicle_revenue.product_id, self.service_type1.product_id)

    def test_01_create_customer_invoice(self):
        # case 6:
        """ Test create customer invoice from vehicle trip.
            Input:
                1. record revenue from vehicle trip.
                2. create customer invoice from vehicle trip.
            Expect:
                - create customer invoice successfully, invoice in draft status.
        """
        self.assertFalse(self.vehicle_trip1.customer_invoice_ids)
        self.record_revenue_from_trip(self.vehicle_trip1, 10)
        self.create_customer_invoice_from_trip(self.vehicle_trip1)

        self.assertTrue(self.vehicle_trip1.customer_invoice_ids)

    def test_02_create_customer_invoice(self):
        # case 7:
        """ Test create customer invoice from vehicle trip.
            Input:
                1. create customer invoice from vehicle trip has not yet recorded revenue.
            Expect:
                - create customer invoice failed.
        """
        self.assertFalse(self.vehicle_trip1.fleet_vehicle_revenue_ids)
        with self.assertRaises(UserError):
            self.create_customer_invoice_from_trip(self.vehicle_trip1)

    def test_compute_fleet_vehicle_revenues_count(self):
        # case 8: test compute `fleet_vehicle_revenues_count`
        self.assertEqual(self.vehicle_trip1.fleet_vehicle_revenues_count, 0)

        self.record_revenue_from_trip(self.vehicle_trip1, 10, customer_id=self.partner1.id)
        self.record_revenue_from_trip(self.vehicle_trip1, 20, customer_id=self.partner2.id)
        self.assertEqual(self.vehicle_trip1.fleet_vehicle_revenues_count, 2)

        self.vehicle_trip1.fleet_vehicle_revenue_ids[0].unlink()
        self.assertEqual(self.vehicle_trip1.fleet_vehicle_revenues_count, 1)

    def test_compute_customer_invoices_count(self):
        # case 9: test compute `fleet_vehicle_revenues_count`
        self.assertEqual(self.vehicle_trip1.customer_invoices_count, 0)

        self.record_revenue_from_trip(self.vehicle_trip1, 10, customer_id=self.partner1.id)
        self.record_revenue_from_trip(self.vehicle_trip1, 20, customer_id=self.partner2.id)
        self.record_revenue_from_trip(self.vehicle_trip1, 20, customer_id=self.partner2.id)

        self.create_customer_invoice_from_trip(self.vehicle_trip1)
        self.assertEqual(self.vehicle_trip1.customer_invoices_count, 2)

        self.vehicle_trip1.customer_invoice_ids[0].unlink()
        self.assertEqual(self.vehicle_trip1.customer_invoices_count, 1)

    def test_negative_revenue_check(self):
        # test method: _negative_revenue_check
        self.user_demo.groups_id = [(6, 0, self.env.ref('fleet.fleet_group_user').ids)]
        with self.assertRaises(UserError):
            self.record_revenue_from_trip(self.vehicle_trip1, -10, user=self.user_demo)

        self.user_demo.groups_id = [(6, 0, self.env.ref('fleet.fleet_group_manager').ids)]
        self.record_revenue_from_trip(self.vehicle_trip1, -10, user=self.user_demo)

    def test_check_constrains_revenue_subtype_id_product_id(self):
        # test method: _check_constrains_revenue_subtype_id_product_id
        with self.assertRaises(ValidationError):
            self.record_revenue_from_trip(self.vehicle_trip1, 10,
                revenue_subtype_id=self.service_type1.id,
                product_id=self.env.ref('product.expense_product').id
            )

    def test_check_contrains_trip_id_trip_waypoint_id(self):
        # test method: _check_contrains_trip_id_trip_waypoint_id
        trip1 = self.env['fleet.vehicle.trip'].create({
            'vehicle_id': self.vehicle1.id,
            'driver_id': self.partner1.id,
            'expected_start_date': '2021-01-01 20:00:00'
        })
        trip_waypoint1 = self.env['fleet.vehicle.trip.waypoint'].create({
            'trip_id': trip1.id,
            'address_id': self.partner1.id,
        })
        with self.assertRaises(UserError):
            self.record_revenue_from_trip(self.vehicle_trip1, 10, trip_waypoint_id=trip_waypoint1.id)

    def test_check_contrains_trip_id_trip_section_id(self):
        # test method: _check_contrains_trip_id_trip_section_id
        trip1 = self.env['fleet.vehicle.trip'].create({
            'vehicle_id': self.vehicle1.id,
            'driver_id': self.partner1.id,
            'expected_start_date': '2021-01-01 20:00:00'
        })
        trip_section1 = self.env['fleet.vehicle.trip.section'].create({
            'trip_id': trip1.id,
            'address_from_id': self.partner1.id,
            'address_to_id': self.partner2.id,
            'distance': 100,
            'ave_speed': 100
        })
        with self.assertRaises(UserError):
            self.record_revenue_from_trip(self.vehicle_trip1, 10, trip_section_id=trip_section1.id)

    def test_check_contrains_trip_waypoint_id_trip_section_id(self):
        # test method: _check_contrains_trip_waypoint_id_trip_section_id
        with self.assertRaises(UserError):
            self.record_revenue_from_trip(self.vehicle_trip1, 10, trip_section_id=False, trip_waypoint_id=False)
