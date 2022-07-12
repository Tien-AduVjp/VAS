from odoo import fields, models, api
from odoo.tools import float_compare


class FleetVehicleTripWaypoint(models.Model):
    _name = 'fleet.vehicle.trip.waypoint'
    _description = 'Trip Waypoint'
    _order = 'trip_id, sequence, id'
    _rec_name = 'address_id'

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', required=True, index=True, ondelete='cascade')
    route_id = fields.Many2one('route.route', index=True, string='Route', help="The Route to which the waypoint belongs")
    sequence = fields.Integer(string='Sequence', required=True, index=True, default=10)
    address_id = fields.Many2one('res.partner', string='Address', required=True)
    street = fields.Char(string='Street', related='address_id.street', readonly=True)
    street2 = fields.Char(string='Street 2', related='address_id.street2', readonly=True)
    city = fields.Char(string='City', related='address_id.city', readonly=True)
    state_id = fields.Many2one('res.country.state', string="State", related='address_id.state_id', readonly=True)
    country_id = fields.Many2one('res.country', string="Country", related='address_id.country_id', readonly=True)
    stop_duration = fields.Float(string='Stop Duration', required=True, default=0.0, compute='_compute_stop_duration', readonly=False, store=True,
                                 help="The duration of stop time (in hours) that the vehicle usually takes")

    log_services_ids = fields.One2many('fleet.vehicle.log.services', 'trip_waypoint_id', string='Services Logs',
                                       groups="viin_fleet.group_fleet_vehicle_log_services_read")

    _sql_constraints = [
        ('stop_duration_positive_check',
         'CHECK(stop_duration >= 0.0)',
         "The Stop Duration must not be negative!"),
    ]

    @api.depends('address_id')
    def _compute_stop_duration(self):
        for r in self:
            r.stop_duration = 0.0
            if r.address_id:
                if float_compare(r.address_id.ave_stop_duration, 0.0, precision_digits=2) == 1:
                    r.stop_duration = r.address_id.ave_stop_duration
                else:
                    r.stop_duration = r.address_id.default_stop_duration

