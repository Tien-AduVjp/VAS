from odoo import models, fields, api


class FleetVehicleLogFuel(models.Model):
    _name = 'fleet.vehicle.log.fuel'
    _inherit = ['fleet.vehicle.log.fuel', 'abstract.fleet.vehicle.log', 'mail.thread']

    cost_amount = fields.Monetary()

    @api.model
    def update_vendors(self):
        """
        This method is called once when installing this module to update vendor of the parent to the child cost
        """
        logs = self.search([])
        for log in logs:
            if log.vendor_id:
                log.cost_id.write({
                    'vendor_id': log.vendor_id.id
                    })
        return
