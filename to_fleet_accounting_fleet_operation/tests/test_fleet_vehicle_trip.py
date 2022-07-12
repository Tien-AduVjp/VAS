from odoo.tests.common import tagged
from .common import FleetAccountingFleetOperationCommon


@tagged('post_install', '-at_install')
class TestFlettVehicleTrip(FleetAccountingFleetOperationCommon):
    def test_01_compute_services_invoiced(self):
        """ If all vehicle service of trip have invoice, trip will be marked Sevices Invoiced
            If anyone vehicle service of trip haven't invoice, trip will be marked Services Uninvoiced"""
        self.assertTrue(self.trip.services_invoiced,
                        "to_fleet_accounting_fleet_operation: Error compute_services_invoiced")
        self.vehicle_service_uninvoice.write({
            'trip_id': self.trip.id,
        })
        self.assertFalse(self.trip.services_invoiced,
                         "to_fleet_accounting_fleet_operation: Error compute_services_invoiced")

    def test_02_compute_vendor_invoices_count(self):
        self.assertEqual(self.trip.vendor_invoices_count, 1,
                         "to_fleet_accounting_fleet_operation: Error compute_vendor_invoices_count")
        self.vehicle_service_uninvoice.write({
            'trip_id': self.trip.id,
        })
        self.assertEqual(self.trip.vendor_invoices_count, 1,
                         "to_fleet_accounting_fleet_operation: Error compute_vendor_invoices_count")
