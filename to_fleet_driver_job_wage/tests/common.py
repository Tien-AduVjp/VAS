from odoo.tests.common import SavepointCase


class FleetDriverJobWageCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(FleetDriverJobWageCommon, cls).setUpClass()
        cls.user = cls.env.ref('base.user_demo')
        cls.partner = cls.user.partner_id
        cls.user.employee_id.address_home_id = cls.partner
        cls.route_1 = cls.env['route.route'].create({
            'name': 'route_test_to_fleet_driver_job_wage',
            'waypoint_ids': [(0, 0, {'address_id': cls.partner.id}),
                             (0, 0, {'address_id': cls.env.ref('base.res_partner_2').id})]
        })
        cls.route_2 = cls.env['route.route'].create({
            'name': 'route_test_to_fleet_driver_job_wage',
            'waypoint_ids': [(0, 0, {'address_id': cls.env.ref('base.res_partner_3').id}),
                             (0, 0, {'address_id': cls.env.ref('base.res_partner_4').id})]
        })
        cls.fl_job_wage_di_1 = cls.env['fleet.job.wage.definition'].create({
            'route_id': cls.route_1.id,
            'vehicle_id': cls.env.ref('fleet.vehicle_1').id,
            'consumption': 15,
            'allowance': 100000,
            'fleet_service_type_id': cls.env.ref('fleet.type_service_service_1').id,
        })
        cls.trip_1 = cls.env['fleet.vehicle.trip'].create({
            'vehicle_id': cls.env.ref('fleet.vehicle_1').id,
            'driver_id': cls.partner.id,
            'expected_start_date': '2021-09-29 12:00:00',
            'route_id':cls.route_1.id,
            })
        # Need call onChange to auto add trip_waypoint
        cls.trip_1._onchange_route_id()

    @classmethod
    def setUP_fuel_price(cls):
        cls.fl_fuel_price_14_10 = cls.env['fleet.fuel.price'].create({
            'date': "2021-09-14",
            'price_per_liter': 14000,
        })
        cls.fl_fuel_price_15_10 = cls.env['fleet.fuel.price'].create({
            'date': "2021-09-15",
            'price_per_liter': 15000,
        })

    @classmethod
    def setUP_multiple_trip(cls):
        cls.fl_job_wage_di_2 = cls.env['fleet.job.wage.definition'].create({
            'route_id': cls.route_2.id,
            'vehicle_id': cls.env.ref('fleet.vehicle_2').id,
            'consumption': 20,
            'allowance': 200000,
            'fleet_service_type_id': cls.env.ref('fleet.type_service_service_2').id,
        })
        cls.trip_2 = cls.env['fleet.vehicle.trip'].create({
            'vehicle_id': cls.env.ref('fleet.vehicle_2').id,
            'driver_id': cls.partner.id,
            'expected_start_date': '2021-09-14 12:00:00',
            'route_id':cls.route_2.id,
            })
        cls.trip_another_month = cls.env['fleet.vehicle.trip'].create({
            'vehicle_id': cls.env.ref('fleet.vehicle_1').id,
            'driver_id': cls.partner.id,
            'expected_start_date': '2021-10-14 12:00:00',
            'route_id':cls.route_1.id,
            })
        cls.trip_not_done = cls.env['fleet.vehicle.trip'].create({
            'vehicle_id': cls.env.ref('fleet.vehicle_1').id,
            'driver_id': cls.partner.id,
            'expected_start_date': '2021-10-14 12:00:00',
            'route_id':cls.route_1.id,
            })
        cls.trip_another_partner = cls.env['fleet.vehicle.trip'].create({
            'vehicle_id': cls.env.ref('fleet.vehicle_1').id,
            'driver_id': cls.env.ref('base.res_partner_2').id,
            'expected_start_date': '2021-09-15 12:00:00',
            'route_id':cls.route_1.id,
            })
        # Need call onChange to auto add trip_waypoint
        cls.trip_2._onchange_route_id()
        cls.trip_another_month._onchange_route_id()
        cls.trip_another_partner._onchange_route_id()
        cls.trip_not_done._onchange_route_id()
