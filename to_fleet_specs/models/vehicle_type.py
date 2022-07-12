from odoo import models, fields


class VehicleType(models.Model):
    _name = 'vehicle.type'
    _description = 'Vehicle Type'

    name = fields.Char(translate=True, string='Title', required=True)
    type = fields.Selection([
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('bus', 'Bus')], string='Type', default='car', required=True,
        help="The technical type of the vehicle")
