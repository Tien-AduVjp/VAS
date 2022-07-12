from odoo import fields, models, api
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    ready_for_fleet_picking = fields.Boolean(string='Ready for Fleet Picking', default=False,
                                             help='Check this field to indicate that this picking is ready for your fleet to pick')

    total_weight = fields.Float(string="Total Weight (kg)", compute='_compute_total',
                                help='Total Weight of the available products (which are ready to transfer), not of the whole products in the stock picking')
    total_volume = fields.Float(string="Total Volume (m3)", compute='_compute_total',
                                help='Total Volume of the available products (which are ready to transfer), not of the whole products in the stock picking')
    total_stowage_volume = fields.Float(string="Total Stowage Volume (m3)", compute='_compute_total',
                                help='Total Stowage Volume of the available products (which are ready to transfer), not of the whole products in the stock picking')
    trip_waypoint_id = fields.Many2one('fleet.vehicle.trip.waypoint', string='Delivering Trip Waypoint', index=True, help="The trip waypoint"
                                       " at which this stock transfer is delivered", readonly=True)
    pick_trip_waypoint_id = fields.Many2one('fleet.vehicle.trip.waypoint', string='Picking Trip Waypoint', index=True, help="The trip waypoint"
                                       " at which this stock transfer is picked")
    trip_id = fields.Many2one('fleet.vehicle.trip', string='Vehicle Trip', index=True)

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', related='trip_id.vehicle_id', readonly=True,
                                 help='The vehicle that carried this transfer')
    driver_id = fields.Many2one('res.partner', related='trip_id.driver_id', readonly=True,
                                help='The driver who carried out this transfer')
    
    fleet_picking_address_id = fields.Many2one('res.partner', string='Fleet Picking Address', compute='_compute_picking_delivery_addresses',
                                                store=True, index=True,
                                                help='Technical field to provide picking address for the fleet')

    fleet_delivery_address_id = fields.Many2one('res.partner', string='Fleet Delivery Address', compute='_compute_picking_delivery_addresses',
                                                store=True, index=True,
                                                help='Technical field to provide delivery address for the fleet')

    @api.depends(
        'move_line_ids',
        'move_line_ids.product_id',
        'move_line_ids.product_qty',
        'move_line_ids.qty_done',
        'move_lines',
        'move_lines.product_id',
        'move_lines.product_qty',
        'move_lines.product_uom_qty',
        'move_lines.quantity_done'
    )
    def _compute_total(self):
        prec = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        for r in self:
            total_weight = total_volume = total_stowage_volume = 0.0
            if r.state in ('partially_available', 'assigned', 'done'):  # calculate base on pack operation lines

                # check if we should use qty_done or product_qty (qty to do)
                use_qty_done = False
                if any(float_compare(line.qty_done, 0.0, precision_digits=prec) == 1 for line in r.move_line_ids):
                    use_qty_done = True

                # iterate pack operation lines for totals
                for line in r.move_line_ids:
                    # convert to quantity in default UoM
                    pack_uom = line.product_uom_id
                    default_uom = line.product_id.uom_id
                    qty = line.qty_done if use_qty_done else line.product_qty
                    qty = pack_uom._compute_quantity(qty, default_uom)

                    total_weight += line.product_id.weight * qty
                    total_volume += line.product_id.volume * qty
                    total_stowage_volume += line.product_id.stowage_volume * qty

            else:  # calculate base on move lines

                # iterate move lines for totals
                for line in r.move_lines:
                    # convert to quantity in default UoM
                    move_line_uom = line.product_uom
                    default_uom = line.product_id.uom_id
                    qty = move_line_uom._compute_quantity(line.product_uom_qty, default_uom)

                    total_weight += line.product_id.weight * qty
                    total_volume += line.product_id.volume * qty
                    total_stowage_volume += line.product_id.stowage_volume * qty

            r.total_weight = total_weight
            r.total_volume = total_volume
            r.total_stowage_volume = total_stowage_volume

    @api.depends('picking_type_id', 'picking_type_id.code', 'picking_type_id.warehouse_id', 'picking_type_id.warehouse_id.partner_id', 'partner_id')
    def _compute_picking_delivery_addresses(self):
        for r in self:
            fleet_picking_address_id = fleet_delivery_address_id = False
            if r.picking_type_id.code == 'incoming':
                fleet_picking_address_id = r.partner_id
                fleet_delivery_address_id = r.picking_type_id.warehouse_id.partner_id
            if r.picking_type_id.code == 'outgoing':
                fleet_picking_address_id = r.picking_type_id.warehouse_id.partner_id
                fleet_delivery_address_id = r.partner_id
            if r.picking_type_id.code == 'internal':
                fleet_picking_address_id = r.location_id.warehouse_id.partner_id
                fleet_delivery_address_id = r.location_dest_id.warehouse_id.partner_id
            r.fleet_picking_address_id = fleet_picking_address_id
            r.fleet_delivery_address_id = fleet_delivery_address_id

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if vals.get('trip_id', False):
            res.move_lines._update_vehicle_id(vals['trip_id'])
            res.trip_id._set_picking_ids()
        return res

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if vals.get('trip_id', False):
            self.mapped('move_lines')._update_vehicle_id(vals['trip_id'])
            self.mapped('trip_id')._set_picking_ids()
        return res
