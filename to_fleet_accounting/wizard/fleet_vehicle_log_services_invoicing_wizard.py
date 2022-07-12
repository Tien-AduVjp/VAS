from odoo import models, api

class FleetVehicleLogServicesInvoicingWizard(models.TransientModel):
    _name = 'fleet.vehicle.log.services.invoicing.wizard'
    _description = 'Fleet Vehicle Log Services Invoicing Wizard'
    _inherit = 'abstract.fleet.vehicle.cost.invoicing.wizard'


    def create_invoices(self):
        fleet_vehicle_cost_ids = self.env['fleet.vehicle.cost']

        active_ids = self._context.get('active_ids', [])
        fleet_vehicle_log_services_ids = self.env['fleet.vehicle.log.services'].browse(active_ids)
        if fleet_vehicle_log_services_ids:

            parent_cost_ids = fleet_vehicle_log_services_ids.mapped('cost_id')
            fleet_vehicle_cost_ids |= parent_cost_ids

            child_cost_ids = parent_cost_ids.mapped('cost_ids')
            if child_cost_ids:
                fleet_vehicle_cost_ids |= child_cost_ids

        return self.create_invoice_from_costs(fleet_vehicle_cost_ids)


