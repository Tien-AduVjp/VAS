from odoo import models, fields, api

class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Vehicle Trip', domain="[('vehicle_id', '=', vehicle_id)]")

    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        if self.vehicle_id != self.trip_id.vehicle_id:
            self.trip_id = False
