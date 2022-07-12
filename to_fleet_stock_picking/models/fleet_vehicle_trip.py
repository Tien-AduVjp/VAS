from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class FleetVehicleTrip(models.Model):
    _inherit = 'fleet.vehicle.trip'

    stock_picking_ids = fields.One2many('stock.picking', 'trip_id', string='Stock Pickings',
                                  readonly=False, states={'confirmed': [('readonly', True)],
                                                          'progress': [('readonly', True)],
                                                          'done': [('readonly', True)],
                                                          'cancelled': [('readonly', True)]},
                                  help='List of stock pickings associated to this trip')

    total_weight = fields.Float(string="Total Weight", compute='_compute_total_load', store=True, tracking=True,
                                help='Total Weight in Kg')
    total_stowage_volume = fields.Float(string="Total Stowage Volume", store=True, tracking=True,
                                        compute='_compute_total_load',
                                        help='Total Stowage Volume in m3')

    @api.model
    def get_most_matched_route(self, address_ids):
        """
        :param address_ids: list of ids of addresses (res.partner)
        """
        address_ids_set = set(address_ids.ids)
        matched_routes = self.env['route.route'].search([('address_ids', 'like', address_ids.ids)]).filtered(lambda r: sorted(r.address_ids.ids) == sorted(address_ids_set))
        if not matched_routes:
            matched_routes = self.env['route.route'].search([('address_ids', 'like', address_ids.ids)])
        matched_routes.read(['total_distance', 'address_ids', 'est_trip_time'])
        most_matched_route = False
        for route in matched_routes:
            if not most_matched_route:
                most_matched_route = route

            # comparing number of intersection between the last most matched route vs addresses and the current route vs addresses
            last_intersection_len = len(address_ids_set.intersection(most_matched_route.address_ids.ids))
            current_intersection_len = len(address_ids_set.intersection(route.address_ids.ids))

            # select the current route if the number of intersection is bigger than that last most matched
            if current_intersection_len > last_intersection_len:
                most_matched_route = route
            # in case they have same number of intersection, we select the one with less total distance and less
            elif current_intersection_len == last_intersection_len:
                less_distance = route.total_distance < most_matched_route.total_distance
                equal_distance = route.total_distance == most_matched_route.total_distance
                less_est_trip_time = route.est_trip_time < most_matched_route.est_trip_time
                equal_est_trip_time = route.est_trip_time == most_matched_route.est_trip_time

                if less_distance and less_est_trip_time:
                    most_matched_route = route
                elif (equal_est_trip_time and less_distance) or (equal_distance and less_est_trip_time):
                    most_matched_route = route

        return most_matched_route

    @api.onchange('stock_picking_ids')
    def _set_picking_ids(self):
        address_ids = self.stock_picking_ids.fleet_delivery_address_id | self.stock_picking_ids.fleet_picking_address_id
        address_ids = self.env['res.partner'].browse(address_ids.ids)

        route_id = False
        if address_ids:
            # only suggest the most matched route in case no route is selected priorily.
            if not self.route_id:
                most_matched_route = self.get_most_matched_route(address_ids)
                route_id = most_matched_route
        self.update({'route_id': route_id})
        self._onchange_route_id()

        # take the existing waypoints that match the address_ids
        trip_waypoint_ids = self.trip_waypoint_ids.filtered(lambda p: p.address_id.id in address_ids.ids)
        # create new waypoints of not exist than match with stock pickings
        # TODO: Improve functionality for better assigning picking and delivery orders to waypoint.
        for address_id in address_ids:
            delivery_stock_picking_ids = self.stock_picking_ids.filtered(lambda p: p.fleet_delivery_address_id.id == address_id.id)
            pick_stock_picking_ids = self.stock_picking_ids.filtered(lambda p: p.fleet_picking_address_id.id == address_id.id)
            trip_waypoints = trip_waypoint_ids.filtered(lambda wp: wp.address_id.id == address_id.id).sorted('sequence')
            if trip_waypoints:
                if len(trip_waypoints) == 1:
                    # If the address has only one waypoint, both delivery and picking order assigned to this one.
                    trip_waypoints.update({
                        'picked_stock_picking_ids': [(6, 0, pick_stock_picking_ids.ids)],
                        'stock_picking_ids': [(6, 0, delivery_stock_picking_ids.ids)],
                    })
                else:
                    # If the address has more than one waypoint:
                    # - First waypoint will be used to pick up orders
                    # - Last waypoint will be used to delivery orders
                    trip_waypoints[0].update({
                        'picked_stock_picking_ids': [(6, 0, pick_stock_picking_ids.ids)],
                    })
                    trip_waypoints[-1].update({
                        'stock_picking_ids': [(6, 0, delivery_stock_picking_ids.ids)],
                    })
            else:
                new_wp = trip_waypoint_ids.new({
                    'address_id': address_id.id,
                    'stock_picking_ids': [(6, 0, delivery_stock_picking_ids.ids)],
                    'picked_stock_picking_ids':[(6, 0, pick_stock_picking_ids.ids)],
                    })
                trip_waypoint_ids += new_wp
        self.update({
            'trip_waypoint_ids': trip_waypoint_ids,
            'route_id': route_id,
        })
        self._onchange_trip_waypoint_ids()

    @api.depends('trip_waypoint_ids', 'trip_waypoint_ids.total_weight', 'trip_waypoint_ids.total_stowage_volume')
    def _compute_total_load(self):
        for r in self:
            r.update({
                'total_weight': sum(r.trip_waypoint_ids.mapped('total_weight')),
                'total_stowage_volume': sum(r.trip_waypoint_ids.mapped('total_stowage_volume'))
                })

    @api.constrains('vehicle_id', 'total_weight', 'total_stowage_volume')
    def _check_max_capacity(self):
        for r in self.filtered(lambda r: r.vehicle_id):
            if r.total_weight > r.vehicle_id.max_weight:
                raise UserError(_("Total Weight of all the transfers must be less than the max allowed weight of the vehicle %s which is %s.")
                                % (r.vehicle_id.display_name, r.vehicle_id.max_weight))
            if r.total_stowage_volume > r.vehicle_id.max_volume:
                    raise UserError(_("Total Stowage Volume of all the transfers must be less than the max allowed Volume of the vehicle %s which is %s.")
                                    % (r.vehicle_id.display_name, r.vehicle_id.max_volume))

    @api.onchange('vehicle_id', 'total_weight', 'total_stowage_volume')
    def onchange_capacity(self):
        if self.vehicle_id:
            if self.total_weight > self.vehicle_id.warning_weight and self.total_weight < self.vehicle_id.max_weight:
                return {'warning': {
                    'title': _('Total Weight Warning!'),
                    'message': _('Total Weight is greater than %s. Are you sure to continue?') % self.vehicle_id.warning_weight
                    }}

            if self.total_stowage_volume > self.vehicle_id.warning_volume and self.total_stowage_volume < self.vehicle_id.max_volume:
                return {'warning': {
                    'title': _('Total Stowage Volume Warning!'),
                    'message': _('Total Stowage Volume is greater than %s. Are you sure to continue?') % self.vehicle_id.warning_volume
                    }}

    @api.constrains('stock_picking_ids')
    def _check_picking_waypoint(self):
        for r in self:
            for picking in r.stock_picking_ids:
                if not picking.trip_waypoint_id:
                    raise ValidationError(_('The transfer %s did not find its proper delivery waypoint from the Waypoints list of the trip.'
                                            ' Please either change the route or add a waypoint in the Waypoints tab or remove the transfer from the trip')
                                          % picking.name)

    def print_picking(self):
        pickings = self.trip_waypoint_ids.stock_picking_ids
        if not pickings:
            raise UserError(_('Nothing to print.'))
        action = self.env.ref('stock.action_report_picking').with_context(active_ids=pickings.ids, active_model='stock.picking').report_action([])
        return action
