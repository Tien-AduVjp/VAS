from odoo import models, fields


class VehicleClass(models.Model):
    _name = 'vehicle.class'
    _description = 'Vehicle Class'

    name = fields.Char(translate=True, string='Name', required=True)
    type_id = fields.Many2one('vehicle.type', string='Vehicle Type', required=True, ondelete='restrict')
    type = fields.Selection(related='type_id.type', store=True)

    min_weight = fields.Float(string='Min. Weight', help="Minimum Weight in kilograms for vehicles in this vehicle class")
    max_weight = fields.Float(string='Max. Weight', help="Maximum Weight in kilograms for vehicles in this vehicle class")
    min_seats = fields.Integer(string='Min. Seats', help="Minimum Seats for vehicles in this vehicle class")
    max_seats = fields.Integer(string='Max. Seats', help="Maximum Seats for vehicles in this vehicle class")

    description = fields.Text(string='Description', translate=True)

    _sql_constraints = [
        ('check_min_weight',
         'CHECK(min_weight >= 0.0)',
         "The Min. Weight must be greater than or equal to zero!"),

        ('check_max_weight',
         'CHECK(max_weight >= 0.0)',
         "The max. Weight must be greater than or equal to zero!"),

        ('check_min_seats',
         'CHECK(min_seats >= 0.0)',
         "The Min. Seats must be greater than or equal to zero!"),

        ('check_max_seats',
         'CHECK(max_seats >= 0.0)',
         "The Max. Seats must be greater than or equal to zero!"),

        ('check_weights',
         'CHECK(max_weight >= min_weight)',
         "The Min. Weight must be less than or equal to the Max. Weight!"),

        ('check_seats',
         'CHECK(max_seats >= min_seats)',
         "The Min. Seats must be less than or equal to the Max. Weight!"),
    ]
