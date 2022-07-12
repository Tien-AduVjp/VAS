from odoo.tests.common import tagged
from .common import FleetAccountingFleetOperationCommon


@tagged('post_install', '-at_install')
class TestFlettVehicleTrip(FleetAccountingFleetOperationCommon):
    def test_01_compute_costs_invoiced(self):
        """ If all vehicle cost of trip have invoice, trip will be marked Costs Invoiced
            If anyone vehicle cost of trip haven't invoice, trip will be marked Costs Uninvoiced"""
        self.assertTrue(self.trip.costs_invoiced,
                        "to_fleet_accounting_fleet_operation: Error compute_costs_invoiced")
        self.vehicle_cost_uninvoice.write({
            'trip_id': self.trip.id,
        })
        self.assertFalse(self.trip.costs_invoiced,
                         "to_fleet_accounting_fleet_operation: Error compute_costs_invoiced")

    def test_02_compute_vendor_invoices_count(self):
        self.assertEqual(self.trip.vendor_invoices_count, 1,
                         "to_fleet_accounting_fleet_operation: Error compute_vendor_invoices_count")
        self.vehicle_cost_uninvoice.write({
            'trip_id': self.trip.id,
        })
        self.assertEqual(self.trip.vendor_invoices_count, 1,
                         "to_fleet_accounting_fleet_operation: Error compute_vendor_invoices_count")
