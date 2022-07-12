from odoo.exceptions import UserError
from odoo.tests.common import tagged
from .common import FleetAccountingFleetOperationCommon


@tagged('post_install', '-at_install')
class TestFletAccountMoveLine(FleetAccountingFleetOperationCommon):
    def test_05_trip_invoicing_cost_wizard(self):
        self.vehicle_service_uninvoice.write({
            'trip_id': self.trip.id,
        })
        trip_invoicing_cost_wizard = self.env['trip.invoicing.cost.wizard'].with_context(
            active_ids=[self.trip.id]).create({})
        trip_invoicing_cost_wizard.create_invoices()
        self.assertTrue(self.vehicle_service_uninvoice.invoice_line_id,
                        "to_fleet_accounting_fleet_operation: Error invoicing_cost_wizard, lost invoice_line_id")
        self.assertEqual(self.trip.vendor_invoices_count, 2,
                         "to_fleet_accounting_fleet_operation: Error vendor_invoices_count")

    def test_07_create_invoice_for_cost_of_another_trip(self):
        trip_invoicing_cost_wizard = self.env['trip.invoicing.cost.wizard'].with_context(
            active_ids=[self.trip.id]).create({})
        trip_invoicing_cost_wizard.vehicle_service_ids += self.vehicle_service_uninvoice
        with self.assertRaises(UserError):
            trip_invoicing_cost_wizard.create_invoices()
