from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class FleetVehicleCost(models.Model):
    _inherit = 'fleet.vehicle.cost'

    trip_section_id = fields.Many2one('fleet.vehicle.trip.section', string='Trip Section',
                                      help="The section of the trip's route for which the cost has been raised")
    route_section_id = fields.Many2one('route.section', related='trip_section_id.route_section_id', store=True, index=True, readonly=True)
    trip_waypoint_id = fields.Many2one('fleet.vehicle.trip.waypoint', string='Trip Waypoint',
                                       help="The waypoint of the trip's route for where the cost has been raised")
    address_id = fields.Many2one('res.partner', string='Address/Location', related='trip_waypoint_id.address_id', store=True, index=True, readonly=True)

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', compute='_compute_trip', inverse='_set_trip', store=True, index=True,
                              help="The trip on which the cost concerns. This field is automatically computed"
                              " base on the Trip Section and the Trip Waypoint")

    route_id = fields.Many2one('route.route', string="Route", related='trip_id.route_id', store=True, index=True, readonly=True,
                               help="The route on which the cost concerns which is computed based on the route of the corresponding trip")


    @api.constrains('trip_section_id', 'trip_waypoint_id')
    def _check_constrains_trip_section_id_trip_waypoint_id(self):
        for r in self:
            if r.trip_section_id and r.trip_waypoint_id:
                raise ValidationError(_("You may register a cost for either a Trip Section or a Trip Waypoint. Not for both!"))

    @api.constrains('trip_id', 'trip_section_id', 'trip_waypoint_id')
    def _check_constrains_trip_id(self):
        for r in self.filtered(lambda r: r.trip_id):
            if r.trip_section_id:
                if r.trip_section_id.trip_id.id != r.trip_id.id:
                    raise ValidationError(_("There is discrepancy between the selected trip and the trip section!"
                                            " The trip section %s belong to the trip %s")
                                          % (r.trip_section_id.display_name, r.trip_section_id.trip_id.name))
            if r.trip_waypoint_id:
                if r.trip_waypoint_id.trip_id.id != r.trip_id.id:
                    raise ValidationError(_("There is discrepancy between the selected trip and the trip waypoint!"
                                            " The trip waypoint %s belong to the trip %s")
                                          % (r.trip_waypoint_id.display_name, r.trip_waypoint_id.trip_id.name))

    @api.depends('trip_section_id', 'trip_waypoint_id')
    def _compute_trip(self):
        for r in self:
            if r.trip_section_id:
                r.trip_id = r.trip_section_id.trip_id
            elif r.trip_waypoint_id:
                r.trip_id = r.trip_waypoint_id.trip_id
            else:
                r.trip_id = False

    def _set_trip(self):
        pass

    @api.onchange('trip_id')
    def _onchange_trip_id(self):
        res = {}
        if self.trip_id:
            res['domain'] = {
                'trip_section_id': [('id', 'in', self.trip_id.trip_section_ids.ids)],
                'trip_waypoint_id': [('id', 'in', self.trip_id.trip_waypoint_ids.ids)]
                }
        return res


