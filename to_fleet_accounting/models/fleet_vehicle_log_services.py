from odoo import models, fields, api


class FleetVehicleLogServices(models.Model):
    _name = 'fleet.vehicle.log.services'
    _inherit = ['fleet.vehicle.log.services', 'abstract.fleet.vehicle.log', 'mail.thread']

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
                if log.cost_id.cost_ids:
                    log.cost_id.cost_ids.write({
                        'vendor_id': log.vendor_id.id
                        })
        return
