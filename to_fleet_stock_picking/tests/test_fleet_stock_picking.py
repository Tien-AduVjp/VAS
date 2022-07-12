from odoo.tests.common import tagged
from odoo.exceptions import UserError, ValidationError
from .common import TestCommon


@tagged('post_install', '-at_install')
class TestFleetStockPicking(TestCommon):

    def test_stock_picking_compute_total(self):
        qty = self.stock_move.product_uom._compute_quantity(self.stock_move.product_uom_qty, self.stock_move.product_uom)
        total_weight_stock_move = self.stock_move.product_id.weight * qty
        # Test compute total weight, total volume, total stowage volume in picking
        self.assertEqual(self.picking.total_weight, total_weight_stock_move)
        self.assertEqual(self.picking.total_volume, self.stock_move.product_id.volume * qty)
        self.assertEqual(self.picking.total_stowage_volume, self.stock_move.product_id.stowage_volume * qty)

    def test_compute_picking_delivery_addresses(self):
        # with picking type code as outgoing
        self.assertEqual(self.picking.fleet_picking_address_id, self.picking.picking_type_id.warehouse_id.partner_id)
        self.assertEqual(self.picking.fleet_delivery_address_id, self.picking.partner_id)

    def test_set_picking_ids(self):
        self.picking.write({'trip_id': self.trip.id})
        # Test select picking, auto fill trip waypoints
        address_ids = self.picking.fleet_delivery_address_id | self.picking.fleet_picking_address_id
        self.assertEqual(self.trip.trip_waypoint_ids.mapped('address_id'), address_ids)

    def test_check_max_capacity(self):
        self.stock_move.write({'product_uom_qty': 1000})
        with self.assertRaises(UserError):
            self.picking.write({'trip_id': self.trip.id})\
            # Force recompute
            self.picking.flush()

    def test_compute_total_load(self):
        self.picking._compute_total()
        self.picking.write({'trip_id': self.trip.id})

        self.assertEqual(self.trip.total_weight, sum(self.trip.trip_waypoint_ids.mapped('total_weight')))
        self.assertEqual(self.trip.total_stowage_volume, sum(self.trip.trip_waypoint_ids.mapped('total_stowage_volume')))
