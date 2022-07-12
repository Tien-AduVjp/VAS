from odoo.tests import tagged, Form
from odoo.exceptions import ValidationError, UserError

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestRoutes(TestCommon):

    def test_route_compute_with_waypoints_01(self):
        """ Test compute departure, destination, route section lines with input:
            - Create a new route with 3 waypoints HN->HP->QN
            - No section line exists
        """
        self.assertRecordValues(self.route, [{
            'departure_id': self.address_hn.id,
            'destination_id': self.address_qn.id
        }])
        self.assertRecordValues(self.route.route_section_line_ids, [{
            'address_from_id': self.address_hn.id,
            'address_to_id': self.address_hp.id,
            'distance': 0,
            'ave_speed': 0,
            'est_trip_time': 0
        }, {
            'address_from_id': self.address_hp.id,
            'address_to_id': self.address_qn.id,
            'distance': 0,
            'ave_speed': 0,
            'est_trip_time': 0
        }])

    def test_route_compute_with_waypoints_02(self):
        """ Test compute total_distance, average_speed, est_trip_time, route section lines with input:
            - Create a new route with 3 waypoints HN->HP->QN
            - Already exists route section that matches your waypoint
        """
        self.route.unlink()
        existing_route_section = self.env['route.section'].search(
            ['|', '&', ('address_from_id', '=', self.address_hn.id), ('address_to_id', '=', self.address_hp.id),
             '&', ('address_from_id', '=', self.address_hp.id), ('address_to_id', '=', self.address_qn.id)])
        self.assertEqual(len(existing_route_section), 2)

        existing_route_section[0].write({
            'distance': 100,
            'ave_speed': 40
        })
        existing_route_section[1].write({
            'distance': 90,
            'ave_speed': 30
        })
        form = Form(self.env['route.route'])
        form.name = 'Form Test'
        with form.waypoint_ids.new() as line:
            line.address_id = self.address_hn
        with form.waypoint_ids.new() as line:
            line.address_id = self.address_hp
        with form.waypoint_ids.new() as line:
            line.address_id = self.address_qn
        route = form.save()
        # Expected values
        self.assertRecordValues(route, [{
            'total_distance': 190,
            'average_speed': 190/(100/40 + 90/30),
            'est_trip_time': 100/40 + 90/30
        }])
        self.assertRecordValues(route.route_section_line_ids, [{
            'address_from_id': self.address_hn.id,
            'address_to_id': self.address_hp.id,
            'distance': 100,
            'ave_speed': 40,
            'est_trip_time': 100/40
        }, {
            'address_from_id': self.address_hp.id,
            'address_to_id': self.address_qn.id,
            'distance': 90,
            'ave_speed': 30,
            'est_trip_time': 90/30
        }])

    def test_compute_departure_dest_when_changing_sequence(self):
        route_form = Form(self.route)
        self.assertEqual(route_form.departure_id, self.address_hn)
        self.assertEqual(route_form.destination_id, self.address_qn)
        with route_form.waypoint_ids.edit(0) as line:
            line.sequence = 100
        route = route_form.save()
        self.assertRecordValues(route, [{
            'departure_id': self.address_hp.id,
            'destination_id': self.address_hn.id
        }])

    def test_route_direction(self):
        """ Test route same waypoints adjacent to each other. Ex: B->B->...
            Expected result: raise
        """
        with self.assertRaises(ValidationError):
            self.env['route.route'].create({
                'name': 'Route test',
                'waypoint_ids': [(0, 0, {
                    'address_id': self.address_hn.id
                }), (0, 0, {
                    'address_id': self.address_hn.id
                })]
            })

    def test_negative_values_route_section(self):
        route_section = self.env['route.section'].search([('address_from_id', '=', self.address_hn.id)], limit=1)
        with self.assertRaises(UserError):
            route_section.distance = -1
        with self.assertRaises(UserError):
            route_section.ave_speed = -40

    def test_km_2_miles(self):
        form = Form(self.env['route.section'])
        form.distance = 50
        self.assertEqual(form.distance_in_miles, self.env['to.base'].km2mile(50))

    def test_waypoint_area_restricted_none(self):
        self.address_hn.waypoint_area_id = self.waypoint_area.id
        self.address_qn.waypoint_area_id = self.waypoint_area.id

    def test_waypoint_area_restricted_by_state(self):
        self.waypoint_area.restricted_by = 'state'
        self.assertNotEqual(self.address_hn.state_id, self.address_qn.state_id)
        with self.assertRaises(UserError):
            self.address_hn.waypoint_area_id = self.waypoint_area.id
            self.address_qn.waypoint_area_id = self.waypoint_area.id

    def test_waypoint_area_restricted_by_country(self):
        self.waypoint_area.restricted_by = 'state'
        self.address_hn.country_id = self.env.ref('base.be').id
        self.assertNotEqual(self.address_hn.country_id, self.address_qn.country_id)
        with self.assertRaises(UserError):
            self.address_hn.waypoint_area_id = self.waypoint_area.id
            self.address_qn.waypoint_area_id = self.waypoint_area.id
