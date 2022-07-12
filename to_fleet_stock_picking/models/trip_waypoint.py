from odoo import fields, models, api


class FleetVehicleTripWaypoint(models.Model):
    _inherit = 'fleet.vehicle.trip.waypoint'

    stock_picking_ids = fields.One2many('stock.picking', 'trip_waypoint_id', string='Delivered Pickings', compute='_compute_picking_ids', readonly=False,
                                        store=True,
                                        help="The pickings that will be delivered at this trip waypoints")
    picked_stock_picking_ids = fields.One2many('stock.picking', 'pick_trip_waypoint_id', string='Picked Pickings', compute='_get_picked_picking_ids', readonly=False,
                                        store=True,
                                        help="The pickings that will be delivered at this trip waypoints")

    total_weight = fields.Float(string="Total Weight", compute='_compute_total_load', store=True, tracking=True,
                                help='Total Weight in Kg of all the pickings that will be picked or delivered at this trip waypoint.')
    total_stowage_volume = fields.Float(string="Total Stowage Volume", store=True, tracking=True,
                                        compute='_compute_total_load',
                                        help='Total Stowage Volume in m3 of all the pickings that will be picked or delivered at this trip waypoint.')

    @api.depends('trip_id', 'trip_id.stock_picking_ids', 'stock_picking_ids.fleet_delivery_address_id', 'address_id')
    def _compute_picking_ids(self):
        for r in self:
            r.stock_picking_ids = []
            if r.trip_id:
                picking_ids = r.trip_id.stock_picking_ids.filtered(lambda picking: picking.fleet_delivery_address_id.id == r.address_id.id and not picking.trip_waypoint_id)
                if picking_ids:
                    r.stock_picking_ids = [(6, 0, picking_ids.ids)]

    @api.depends('trip_id', 'trip_id.stock_picking_ids', 'picked_stock_picking_ids.fleet_picking_address_id', 'address_id')
    def _get_picked_picking_ids(self):
        for r in self:
            r.picked_stock_picking_ids = []
            if r.trip_id:
                picking_ids = r.trip_id.stock_picking_ids.filtered(lambda picking: picking.fleet_picking_address_id.id == r.address_id.id and not picking.pick_trip_waypoint_id)
                if picking_ids:
                    r.picked_stock_picking_ids = [(6, 0, picking_ids.ids)]

    @api.depends('stock_picking_ids.total_weight', 'stock_picking_ids.total_stowage_volume')
    def _compute_total_load(self):
        for r in self:
            r.total_weight = sum(r.stock_picking_ids.mapped('total_weight'))
            r.total_stowage_volume = sum(r.stock_picking_ids.mapped('total_stowage_volume'))
