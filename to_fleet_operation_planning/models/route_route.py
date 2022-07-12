from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RouteRoute(models.Model):
    _inherit = 'route.route'

    trip_ids = fields.One2many('fleet.vehicle.trip', 'route_id', string='Trips', readonly=True)
    trips_count = fields.Integer(string='Trips Count', compute='_count_trips')

    @api.depends('trip_ids')
    def _count_trips(self):
        trips = self.env['fleet.vehicle.trip'].read_group([('route_id', 'in', self.ids)], ['route_id'], ['route_id'])
        mapped_data = dict([(trip['route_id'][0], trip['route_id_count']) for trip in trips])
        for r in self:
            r.trips_count = mapped_data.get(r.id, 0)

    @api.depends('waypoint_ids', 'waypoint_ids.stop_duration')
    def _compute_est_trip_time(self):
        super(RouteRoute, self)._compute_est_trip_time()
        for r in self:
            r.est_trip_time += sum(r.waypoint_ids.mapped('stop_duration'))

    def action_cancel(self):
        if not self.env.user.has_group('fleet.fleet_group_manager'):
            if any(r.trips_count > 0 for r in self):
                raise UserError(_('Only Fleet Managers can cancel routes those are have existing trips linked!'))

        super(RouteRoute, self).action_cancel()

    @api.model
    def get_waypoint(self, sequence):
        """
        The the waypoint of in the input sequence. The starting waypoint has index 0
        """
        try:
            waypoint = self.waypoint_ids[sequence]
        except IndexError:
            waypoint = False

        return waypoint

    @api.model
    def _prepare_trip_waypoints_data(self, trip_id):
        trip_waypoint_ids = []
        sequence = 10
        for waypoint in self.waypoint_ids:
            waypoint_data = waypoint._parepare_trip_waypoint_data(trip_id)
            waypoint_data['sequence'] = sequence
            trip_waypoint_ids.append((0, 0, waypoint_data))
            sequence += 1
        return trip_waypoint_ids

