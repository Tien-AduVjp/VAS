from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    class_id = fields.Many2one('vehicle.class', string='Vehicle Class', index=True)
    type_id = fields.Many2one(related='class_id.type_id', store=True, index=True, readonly=True)
    type = fields.Selection(related='class_id.type', store=True, index=True, readonly=True,
                            help="The type of the vehicle which is related to the vehicle class's Vehicle Type.")

    year_made = fields.Integer(string='Year Made', help="The year in which the vehicle was made.")
    engine_sn = fields.Char(string='Engine Serial Number', size=20, help="Engine serial number of the vehicle.")
    self_weight = fields.Float(string='Self-Weight', help="The self weight of the vehicle in kilograms.")
    trailer_inner_height = fields.Float(string='Trailer Inner Height',
                                        help="The inner height in meters of the built-in trailer. This applies vehicle in type of Truck only.")
    trailer_inner_width = fields.Float(string='Trailer Inner Width',
                                       help="The inner width in meters of the built-in trailer. This applies vehicle in type of Truck only.")
    trailer_inner_length = fields.Float(string='Trailer Inner Length',
                                        help="The inner length in meters of the built-in trailer. This applies vehicle in type of Truck only.")

    @api.constrains('seats', 'class_id')
    def _check_seats_class_id(self):
        for r in self:
            if r.seats and r.class_id:
                if r.class_id.min_seats:
                    if float_compare(r.seats, r.class_id.min_seats, precision_digits=2) == -1:
                        raise ValidationError(_("The number of seats of the vehicle must be equal to or greater than the type's min. seats which is %s.\n"
                                                "You may need to change the Vehicle Class to meet the requirement.")
                                              % r.class_id.min_seats)
                if r.class_id.max_seats:
                    if float_compare(r.seats, r.class_id.max_seats, precision_digits=2) == 1:
                        raise ValidationError(_("The number of seats of the vehicle must be equal to or less than the type's max. seats which is %s.\n"
                                                "You may need to change the Vehicle Class to meet the requirement.")
                                              % r.class_id.max_seats)

    @api.constrains('self_weight', 'class_id')
    def _check_self_weight_class_id(self):
        for r in self:
            if r.self_weight and r.class_id:
                if r.class_id.min_weight:
                    if float_compare(r.self_weight, r.class_id.min_weight, precision_digits=2) == -1:
                        raise ValidationError(_("The Weight of the vehicle must be equal to or greater than the type's min. weight which is %s.\n"
                                                "You may need to change the Vehicle Class to meet the requirement.")
                                              % r.class_id.min_weight)
                if r.class_id.max_weight:
                    if float_compare(r.self_weight, r.class_id.max_weight, precision_digits=2) == 1:
                        raise ValidationError(_("The Weight of the vehicle must be equal to or less than the type's max. weight which is %s.\n"
                                                "You may need to change the Vehicle Class to meet the requirement.")
                                              % r.class_id.max_weight)

    @api.constrains('year_made')
    def _check_year_made(self):
        this_year = fields.Datetime.now().year
        for r in self.filtered(lambda r: r.year_made):
            if r.year_made < 1900 or r.year_made > this_year:
                raise ValidationError(_("Year made must be between 1900 and %s") % str(this_year))

    @api.constrains('self_weight')
    def _check_self_weight(self):
        for r in self:
            if float_compare(r.self_weight, 0.0, precision_digits=2) == -1:
                raise ValidationError(_("The Self Weight must not be a negative value"))

    @api.constrains('trailer_inner_height')
    def _check_trailer_inner_height(self):
        for r in self:
            if float_compare(r.trailer_inner_height, 0.0, precision_digits=2) == -1:
                raise ValidationError(_("The Trailer Inner Height must not be a negative value"))

    @api.constrains('trailer_inner_width')
    def _check_trailer_inner_width(self):
        for r in self:
            if float_compare(r.trailer_inner_width, 0.0, precision_digits=2) == -1:
                raise ValidationError(_("The Trailer Inner Width must not be a negative value"))

    @api.constrains('trailer_inner_length')
    def _check_trailer_inner_length(self):
        for r in self:
            if float_compare(r.trailer_inner_length, 0.0, precision_digits=2) == -1:
                raise ValidationError(_("The Trailer Inner Length must not be a negative value"))
