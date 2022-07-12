from odoo import fields, models, api


class RouteWaypoint(models.Model):
    _inherit = 'route.waypoint'

    stop_duration = fields.Float(string='Stop Duration', required=True, default=0.0,
                                 related='address_id.default_stop_duration', store=True,
                                 help='The estimated duration of stop time (in hours) that the vehicle usually takes')

    _sql_constraints = [
        ('stop_duration_positive_check',
         'CHECK(stop_duration >= 0.0)',
         "The Stop Duration must not be negative!"),
    ]
    
    def _parepare_trip_waypoint_data(self, trip_id):
        self.ensure_one()
        return {
            'trip_id': trip_id.id,
            'route_id': self.route_id.id,
            'address_id': self.address_id.id,
            'stop_duration': self.stop_duration,
            'sequence': self.sequence,
            }

