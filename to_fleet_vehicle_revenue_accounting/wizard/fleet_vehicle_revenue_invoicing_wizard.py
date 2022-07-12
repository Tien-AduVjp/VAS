from odoo import models


class FleetVehicleRevenueInvoicingWizard(models.TransientModel):
    _name = 'fleet.vehicle.revenue.invoicing.wizard'
    _inherit = 'abstract.fleet.vehicle.revenue.invoicing.wizard'
    _description = 'Fleet Vehicle Revenue Invoicing Wizard'

    def create_invoices(self):
        active_ids = self._context.get('active_ids', [])
        fleet_vehicle_revenue_ids = self.env['fleet.vehicle.revenue'].browse(active_ids)
        return self.create_invoice_from_revenues(fleet_vehicle_revenue_ids)
