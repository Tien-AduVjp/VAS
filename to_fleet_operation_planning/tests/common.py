from datetime import date
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase, Form


class TestCommon(TransactionCase):

    def setUp(self):
        super(TestCommon, self).setUp()

        Partner = self.env['res.partner']
        self.fleet_manager = new_test_user(self.env, "fleet manager", groups="fleet.fleet_group_manager,base.group_partner_manager")
        self.base_user = new_test_user(self.env, "base user", groups="base.group_user")
        self.partner_1 = Partner.create({
            'name': 'Partner 1',
            'is_company': True,
            'street': '1888 Arbor Way',
            'city': 'Turlock',
            'state_id': self.env.ref('base.state_us_5').id,
            'country_id': self.env.ref('base.us').id,
            'email': 'partner1@example.viindoo.com'
            })
        self.partner_2 = Partner.create({
            'name': 'Partner 2',
            'is_company': True,
            'street': '88 Santa Barbara Rd',
            'city': 'Pleasant Hill',
            'state_id': self.env.ref('base.state_us_5').id,
            'country_id': self.env.ref('base.us').id,
            'email': 'partner2@example.viindoo.com'
            })
        self.partner_3 = Partner.create({
            'name': 'Partner 3',
            'is_company': True,
            'street': '55 Santa Barbara Rd',
            'city': 'Pleasant Hill',
            'state_id': self.env.ref('base.state_us_5').id,
            'country_id': self.env.ref('base.us').id,
            'email': 'partner3@example.viindoo.com'
            })
        self.driver1 = Partner.create({
            'name': 'Driver 1',
            'is_driver': True,
            'street': '55 Santa Barbara Rd',
            'city': 'Pleasant Hill',
            'state_id': self.env.ref('base.state_us_5').id,
            'country_id': self.env.ref('base.us').id,
            'email': 'driver1@example.viindoo.com',
            })
        self.driver1_license = self.env['fleet.driver.license'].create({
            'legal_number': 'B2-123456789',
            'driver_id': self.driver1.id,
            'issued_date': date(2019, 12, 30),
            })
        self.driver1_license.action_confirm()
        self.driver2 = Partner.create({
            'name': 'Driver 2',
            'is_driver': True,
            'street': '44 Santa Barbara Rd',
            'city': 'Pleasant Hill',
            'state_id': self.env.ref('base.state_us_5').id,
            'country_id': self.env.ref('base.us').id,
            'email': 'driver2@example.viindoo.com'
            })
        self.vehicle1 = self.env['fleet.vehicle'].create({
            'license_plate': '1-BMW-999',
            'vin_sn': 99999,
            'model_id': self.env.ref('fleet.model_serie1').id,
            'driver_id': self.driver1.id,
            'odometer': 9876.00
            })
        self.vehicle2 = self.env['fleet.vehicle'].create({
            'license_plate': '2-BMW-888',
            'vin_sn': 88888,
            'model_id': self.env.ref('fleet.model_serie1').id,
            'driver_id': self.driver2.id,
            'odometer': 4560.00
            })
        self.employee1 = self.env['hr.employee'].create({
            'name': 'Employee 1',
            'address_home_id': self.driver1.id
            })
        self.route_section = self.env['route.section'].create({
            'address_from_id': self.partner_1.id,
            'address_to_id': self.partner_2.id,
            'distance': 600.0,
            'ave_speed': 100.0
            })
        self.route_section2 = self.env['route.section'].create({
            'address_from_id': self.partner_2.id,
            'address_to_id': self.partner_3.id,
            'distance': 300.0,
            'ave_speed': 100.0
            })

        route_form = Form(self.env['route.route'])
        route_form.name = 'Test Route'
        with route_form.waypoint_ids.new() as waypoint_form:
            waypoint_form.address_id = self.partner_1
        with route_form.waypoint_ids.new() as waypoint_form:
            waypoint_form.address_id = self.partner_2
        self.route = route_form.save()

        self.trip = self.env['fleet.vehicle.trip'].create({
            'vehicle_id': self.vehicle1.id,
            'driver_id': self.driver1.id,
            'expected_start_date': '2020-01-01 12:00:00'
            })
        self.service_type_1 = self.env['fleet.service.type'].create({
            'name': 'Service Type 1',
            'category': 'service'
        })

    def _prepare_trip_confirm(self, trip):
        self.route.action_confirm()
        trip_form = Form(trip)
        trip_form.route_id = self.route
        trip_form.save()
        trip.action_confirm()

    def _trip_wizard_start(self, trip):
        return self.env['vehicle.trip.start.wizard'].create({
            'trip_id': trip.id,
            'operation_start': '2020-01-01 09:00:00',
            'vehicle_id': self.vehicle2.id,
            'odometer': 800.0,
            'driver_id': self.driver2.id,
            'assistant_ids': [(6, 0, self.driver1.ids)]
            })

    def _trip_wizard_end(self, trip):
        return self.env['vehicle.trip.end.wizard'].create({
            'trip_id': trip.id,
            'operation_end': '2020-01-01 23:00:00',
            'odometer': 1500.0,
            'fuel_consumption': 100.0,
            })
