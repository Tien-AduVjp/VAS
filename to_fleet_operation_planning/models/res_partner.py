from odoo import fields, models, api
from odoo.tools import float_compare, float_is_zero


class ResPartner(models.Model):
    _inherit = 'res.partner'

    driver_done_trip_ids = fields.One2many('fleet.vehicle.trip', 'driver_id', domain=[('state', '=', 'done')],
                                           string='Driver Trips',
                                           help="The Trips that have been done by this partner as the role of the driver")
    driver_done_trip_count = fields.Integer(string='Driver Trips Count', compute='_count_driver_done_trips', compute_sudo=True)

    assistant_done_trip_ids = fields.Many2many('fleet.vehicle.trip', 'assistant_trip_rel', 'assistant_id', 'trip_id',
                                               string='Assistant Trips', help='The trips on which this one take the assistant role',
                                               domain=[('state', '=', 'done')])
    assistant_done_trip_count = fields.Integer(string='Assistant Trips Count', compute='_count_assistant_done_trips', compute_sudo=True)

    trip_waypoint_ids = fields.One2many('fleet.vehicle.trip.waypoint', 'address_id', string='Trip Waypoints')
    default_stop_duration = fields.Float(string='Default Stop Duration', required=True, default=0.0,
                                         help='In vehicle trip planning, this is the duration of stop time (in hours) that the vehicle usually takes when staying at this address')
    ave_stop_duration = fields.Float(string='Average Stop Duration', compute='_compute_ave_stop_duration', store=True,
                                     help="The average duration is computed using average method from the past trips' stop time. In case no past trips, the Default Stop Duration"
                                     " will be used. In case the computed average duration is 30% less than the Default Stop Duration or 30% greater than"
                                     " the Default Stop Duration, the Default Stop Duration will be used instead of average method")

    _sql_constraints = [
        ('stop_duration_positive_check',
         'CHECK(default_stop_duration >= 0.0)',
         "The Default Stop Duration must not be negative!"),
    ]

    @api.depends('default_stop_duration', 'trip_waypoint_ids', 'trip_waypoint_ids.stop_duration')
    def _compute_ave_stop_duration(self):
        trip_waypoint_data = self.env['fleet.vehicle.trip.waypoint'].read_group([('address_id', 'in', self.ids)], fields=['address_id', 'stop_duration'], groupby=['address_id'])
        mapped_data = {item['address_id']: {'address_id_count': item['address_id_count'], 'stop_duration': item['stop_duration']} for item in trip_waypoint_data}
        for r in self:
            wp_no = mapped_data.get(r.id, {}).get('address_id_count', 0)
            if wp_no == 0:
                ave_stop_duration = r.default_stop_duration
            else:
                ave_stop_duration = mapped_data.get(r.id, {}).get('stop_duration', 0) / wp_no
                if not float_is_zero(r.default_stop_duration, precision_digits=2):
                    # if the computed stop duration is 30% less than the default stop duration
                    #    or 30% greater thatn the the default stop duration
                    #    reset ave_stop_duration to the default_stop_duration
                    if float_compare(ave_stop_duration, r.default_stop_duration * 1.3, precision_digits=1) == 1 or float_compare(ave_stop_duration, r.default_stop_duration / 1.3, precision_digits=1) == -1:
                        ave_stop_duration = r.default_stop_duration

            r.ave_stop_duration = ave_stop_duration

    @api.depends('driver_done_trip_ids')
    def _count_driver_done_trips(self):
        done_trips = self.env['fleet.vehicle.trip'].read_group([('driver_id', 'in', self.ids), ('state', '=', 'done')], ['driver_id'], ['driver_id'])
        mapped_data = dict([(trip['driver_id'][0], trip['driver_id_count']) for trip in done_trips])
        for r in self:
            r.driver_done_trip_count = mapped_data.get(r.id, 0)

    @api.depends('assistant_done_trip_ids')
    def _count_assistant_done_trips(self):
        for r in self:
            r.assistant_done_trip_count = len(r.assistant_done_trip_ids)

