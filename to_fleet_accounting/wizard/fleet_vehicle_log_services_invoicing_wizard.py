from odoo import models, api

class FleetVehicleLogServicesInvoicingWizard(models.TransientModel):
    _name = 'fleet.vehicle.log.services.invoicing.wizard'
    _description = 'Fleet Vehicle Log Services Invoicing Wizard'
    _inherit = 'abstract.fleet.vehicle.log.services.invoicing.wizard'


    def create_invoices(self):
        active_ids = self._context.get('active_ids', [])
        fleet_vehicle_log_services_ids = self.env['fleet.vehicle.log.services'].browse(active_ids)

        return self.create_invoice_from_services(fleet_vehicle_log_services_ids)


