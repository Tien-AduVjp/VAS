from odoo import fields, models

class RouteWaypoint(models.Model):
    _name = 'route.waypoint'
    _description = 'Route Waypoint'
    _order = 'route_id, sequence, id'
    _rec_name = 'address_id'

    route_id = fields.Many2one('route.route', string="Route", required=True, ondelete='cascade', index=True, copy=False)
    sequence = fields.Integer(string="Sequence", help="Gives the sequence order when displaying a list of waypoints.", default=10, required=True)
    address_id = fields.Many2one('res.partner', string="Waypoint", required=True)

    street = fields.Char(string='Street', related='address_id.street', readonly=True)
    street2 = fields.Char(string='Street 2', related='address_id.street2', readonly=True)
    city = fields.Char(string='City', related='address_id.city', readonly=True)
    state_id = fields.Many2one('res.country.state', string="State", related='address_id.state_id', readonly=True)
    country_id = fields.Many2one('res.country', string="Country", related='address_id.country_id', readonly=True)
    waypoint_area_id = fields.Many2one('route.waypoint.area', related='address_id.waypoint_area_id', readonly=True,
                                       string='Waypoint Area',
                                       help='This field is to group waypoints into an area')
