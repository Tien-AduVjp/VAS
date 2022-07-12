from odoo import models, api

class FleetVehicleLogFuelInvoicingWizard(models.TransientModel):
    _name = 'fleet.vehicle.log.fuel.invoicing.wizard'
    _description = 'Fleet Vehicle Log Fuel Invoicing Wizard'
    _inherit = 'abstract.fleet.vehicle.cost.invoicing.wizard'


    def create_invoices(self):
        fleet_vehicle_cost_ids = self.env['fleet.vehicle.cost']

        active_ids = self._context.get('active_ids', [])
        fleet_vehicle_log_fuel_ids = self.env['fleet.vehicle.log.fuel'].browse(active_ids)

        if fleet_vehicle_log_fuel_ids:
            fleet_vehicle_cost_ids |= fleet_vehicle_log_fuel_ids.mapped('cost_id')

        return self.create_invoice_from_costs(fleet_vehicle_cost_ids)


