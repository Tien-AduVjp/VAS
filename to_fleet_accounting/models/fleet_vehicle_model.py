from odoo import models, fields, api


class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'

    def write(self, vals):
        res = super(FleetVehicleModel, self).write(vals)
        if 'name' in vals:
            vehicles = self.env['fleet.vehicle'].search([('model_id', 'in', self.ids)])
            vehicles._synch_analytic_account_name()
        return res
