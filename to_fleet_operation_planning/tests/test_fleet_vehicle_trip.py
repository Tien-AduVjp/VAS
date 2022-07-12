from datetime import datetime, timedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import tagged, Form

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestFleetVehicleTrip(TestCommon):
    
    def test_compute_employee(self):
        self.assertEqual(self.employee1, self.trip.employee_id)
        
    def test_onchange_route(self):
        self.route.action_confirm()
        route_address = self.route.waypoint_ids.mapped('address_id')
        trip_form = Form(self.trip)
        trip_form.route_id = self.route
        # Test with route section available, Est. Duration of trip get the value of Est. Duration of route section
        self.assertEqual(trip_form._values['est_trip_time'], self.route_section.est_trip_time)
        # Test compute expected_end_date
        expected_end_date = datetime.strptime(trip_form._values['expected_start_date'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=trip_form._values['est_trip_time'])
        self.assertEqual(trip_form._values['expected_end_date'], expected_end_date)
        # Test auto fill waypoint, section, est_distance
        self.assertEqual(trip_form._values['est_distance'], self.route_section.distance)
        
        trip_waypoint_forms = []
        for waypoint in trip_form.trip_waypoint_ids._records:
            trip_waypoint_forms.append(waypoint['address_id'])
        self.assertEqual(trip_waypoint_forms, route_address.ids)
        
        trip_section_form = []
        for section in trip_form.trip_section_ids._records:
            trip_section_form.append(section['address_from_id'])
            trip_section_form.append(section['address_to_id'])
        self.assertEqual(trip_section_form, route_address.ids)
        
        trip_form.save()
        self.assertEqual(self.trip.est_trip_time, self.route_section.est_trip_time)
        self.assertEqual(self.trip.est_distance, self.route_section.distance)
        self.assertEqual(self.trip.trip_waypoint_ids.mapped('address_id'), route_address)
        
        trip_section = []
        for section in self.trip.trip_section_ids:
            trip_section.append(section['address_from_id'].id)
            trip_section.append(section['address_to_id'].id)
        self.assertEqual(trip_section, route_address.ids)
        
    def test_create_trip_with_more_than_2_waypoint(self):
        route_form = Form(self.route)
        with route_form.waypoint_ids.new() as waypoint_form:
            waypoint_form.address_id = self.partner_3
        route_form.save()
        self.route.action_confirm()
        
        new_trip_form = Form(self.env['fleet.vehicle.trip'])
        new_trip_form.vehicle_id = self.vehicle2
        new_trip_form.driver_id = self.driver2
        new_trip_form.expected_start_date = '2020-01-01 09:00:00'
        new_trip_form.route_id = self.route
        # Edit the trip_waypoint_ids, add stop_duration
        with new_trip_form.trip_waypoint_ids.edit(index=1) as trip_waypoint:
            trip_waypoint.stop_duration = 1.5
        with new_trip_form.trip_waypoint_ids.edit(index=2) as trip_waypoint:
            trip_waypoint.stop_duration = 2.0
        # Test when create trip with 3 waypoint, 2 trip section auto fill
        self.assertEqual(len(new_trip_form.trip_waypoint_ids._records) - 1, len(new_trip_form.trip_section_ids._records))
        # Test compute est_distance, est_trip_time, expected_end_date
        total_stop_duration = sum(line['stop_duration'] for line in new_trip_form.trip_waypoint_ids._records)
        est_distance = sum(line['distance'] for line in new_trip_form.trip_section_ids._records)
        est_trip_time = total_stop_duration + sum(line['est_trip_time'] for line in new_trip_form.trip_section_ids._records)
        
        self.assertEqual(new_trip_form.est_distance, est_distance)
        self.assertEqual(new_trip_form.est_trip_time, est_trip_time)
        
        expected_end_date = datetime.strptime(new_trip_form._values['expected_start_date'], '%Y-%m-%d %H:%M:%S') + timedelta(hours=new_trip_form._values['est_trip_time'])
        self.assertEqual(new_trip_form.expected_end_date, expected_end_date)
        
        new_trip = new_trip_form.save()
        new_trip.action_confirm()
        # start new trip
        trip_wizard_start = self._trip_wizard_start(new_trip)
        trip_wizard_start.action_start()
        # end new trip
        trip_wizard_end = self._trip_wizard_end(new_trip)
        trip_wizard_end.action_done()
        # test cpmpute actual distance
        self.assertEqual(new_trip.actual_distance, trip_wizard_end.odometer - trip_wizard_start.odometer)
        # test compute end date
        self.assertEqual(new_trip.operation_end, trip_wizard_end.operation_end)
        self.assertEqual(new_trip.end_date, trip_wizard_end.operation_end)
        # test compute fuel_consumption
        self.assertEqual(new_trip.fuel_consumption, trip_wizard_end.fuel_consumption)
        self.assertEqual(new_trip.average_fuel_consumption_per_hundred, new_trip.fuel_consumption * 100 / new_trip.actual_distance)
        # test compute distance_deviation
        self.assertEqual(new_trip.distance_deviation, new_trip.actual_distance - new_trip.est_distance)
        # test compute operation_duration
        self.assertEqual(new_trip.operation_duration, (new_trip.operation_end - new_trip.operation_start).total_seconds() / 3600)
        # test compute time deviation
        self.assertEqual(new_trip.time_deviation, new_trip.operation_duration - new_trip.est_trip_time)
    
    def test_onchange_vehicle(self):
        # Test auto fill driver
        trip_form = Form(self.trip)
        trip_form.vehicle_id = self.vehicle2
        self.assertEqual(trip_form.driver_id, self.vehicle2.driver_id)
        trip_form.save()
        self.assertEqual(self.trip.driver_id, self.vehicle2.driver_id)
        
    def test_unlink(self):
        # Test unlink when trip state is not draft
        with self.assertRaises(UserError):
            self._prepare_trip_confirm(self.trip)
            self.trip.unlink()
        # Test unlink when trip state is draft
        raised = False
        try:
            self.trip.state = 'draft'
            self.trip.unlink()
        except:
            raised = True
        self.assertFalse(raised)
        
    def test_action_confirm(self):
        # Test contrains when confirm trip have not Waypoints
        with self.assertRaises(ValidationError):
            self.trip.action_confirm()
        # Test when confirm trip have Waypoints
        self._prepare_trip_confirm(self.trip)
        self.assertEqual(self.trip.state, 'confirmed')
        # Test check operation overlap when confim trip
        new_trip = self.env['fleet.vehicle.trip'].create({
            'vehicle_id': self.vehicle1.id,
            'driver_id': self.driver1.id,
            'expected_start_date': '2020-01-01 13:00:00'
            })
        with self.assertRaises(UserError):
            self._prepare_trip_confirm(new_trip)

    def test_trip_with_cost(self):
        cost_val = {
            'vehicle_id': self.vehicle1.id,
            'trip_id': self.trip.id,
            'amount': 1000
        }
        self.env['fleet.vehicle.cost'].create(cost_val)
        self.assertEqual(self.trip.fleet_vehicle_costs_count, 1)
        self.assertEqual(self.trip.fleet_vehicle_cost_ids.amount, 1000)
