from odoo import fields, models

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    warning_volume = fields.Float(string='Warning Volume', help='The total volume can be safely loaded onto the vehicle.', default=0.0)
    max_volume = fields.Float(string='Max. Volume', help='The maximum volume can be loaded onto the vehicle, but not recommended.', default=0.0)
    warning_weight = fields.Float(string='Warning Weight Load', help='The total weight can be safely loaded onto the vehicle.', default=0.0)
    max_weight = fields.Float(string='Max. Weight Load', help='The maximum weight can be loaded onto the vehicle, but not recommended.', default=0.0)
