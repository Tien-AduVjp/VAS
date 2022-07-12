from odoo import models, fields, api


class FleetVehicleLogContract(models.Model):
    _name = 'fleet.vehicle.log.contract'
    _inherit = ['fleet.vehicle.log.contract', 'abstract.fleet.vehicle.log']

    amount = fields.Monetary()
    cost_amount = fields.Monetary()
    cost_generated = fields.Monetary()

    @api.model
    def update_vendors(self):
        """
        This method is called once when installing this module to update vendor of the parent to the child cost
        """
        logs = self.search([])
        for log in logs:
            if log.insurer_id:
                log.cost_id.write({
                    'vendor_id': log.insurer_id.id
                    })
                if log.cost_id.cost_ids:
                    log.cost_id.cost_ids.write({
                        'vendor_id': log.insurer_id.id
                        })
        return
