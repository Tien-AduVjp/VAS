from datetime import timedelta

from odoo.tests.common import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestVehicleTripWizard(TestCommon):

    def test_trip_start_wizard(self):
        self._prepare_trip_confirm(self.trip)
        trip_start_wizard = self._trip_wizard_start(self.trip)
        # Test compute expected end date
        expected_end_date = trip_start_wizard.operation_start + timedelta(hours=trip_start_wizard.trip_id.est_trip_time)
        self.assertEqual(trip_start_wizard.expected_end_date, expected_end_date)
        # Test when click action_start on wizard, override driver, assistants, vehicle, operation start, state on trip
        trip_start_wizard.action_start()
        self.assertEqual(self.trip.driver_id, trip_start_wizard.driver_id)
        self.assertEqual(self.trip.vehicle_id, trip_start_wizard.vehicle_id)
        self.assertEqual(self.trip.state, 'progress')
        self.assertEqual(self.trip.assistant_ids, trip_start_wizard.assistant_ids)
        self.assertEqual(self.trip.operation_start, trip_start_wizard.operation_start)
        # #Test when click action_start on wizard will  create Odometer
        odometer = self.env['fleet.vehicle.odometer'].search([('value', '=', trip_start_wizard.odometer),
                                                              ('date', '=', trip_start_wizard.operation_start),
                                                              ('vehicle_id', '=', trip_start_wizard.vehicle_id.id),
                                                              ('trip_id', '=', trip_start_wizard.trip_id.id),
                                                              ], limit=1)
        self.assertTrue(odometer)
        # Test add follower in trip when click action_start
        self.assertTrue(self.driver2 in trip_start_wizard.trip_id.message_follower_ids.mapped('partner_id'))
