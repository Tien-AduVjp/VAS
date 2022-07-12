from odoo import models


class FleetVehicleModelBrand(models.Model):
    _inherit = 'fleet.vehicle.model.brand'

    def write(self, vals):
        res = super(FleetVehicleModelBrand, self).write(vals)
        if 'name' in vals:
            vehicles = self.env['fleet.vehicle'].search([('model_id.brand_id', 'in', self.ids)])
            vehicles._synch_analytic_account_name()
        return res
