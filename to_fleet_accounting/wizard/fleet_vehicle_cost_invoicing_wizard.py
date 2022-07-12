from odoo import models, api

class FleetVehicleCostInvoicingWizard(models.TransientModel):
    _name = 'fleet.vehicle.cost.invoicing.wizard'
    _inherit = 'abstract.fleet.vehicle.cost.invoicing.wizard'
    _description = 'Fleet Vehicle Cost Invoicing Wizard'

    def create_invoices(self):
        active_ids = self._context.get('active_ids', [])
        fleet_vehicle_cost_ids = self.env['fleet.vehicle.cost'].browse(active_ids)
        return self.create_invoice_from_costs(fleet_vehicle_cost_ids)


