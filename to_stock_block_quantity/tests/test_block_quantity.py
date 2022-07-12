from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.stock.tests.common import TestStockCommon


@tagged('post_install', '-at_install')
class TestBlockQuantity(TestStockCommon):

    @classmethod
    def setUpClass(cls):
        super(TestBlockQuantity, cls).setUpClass()
        cls.picking_pick, cls.picking_client = cls.create_pick_ship()

    @classmethod
    def create_pick_ship(cls):
        picking_client = cls.env['stock.picking'].with_context(tracking_disabled=True).create({
            'location_id': cls.pack_location,
            'location_dest_id': cls.customer_location,
            'picking_type_id': cls.picking_type_out,
        })

        dest = cls.MoveObj.create({
            'name': cls.productA.name,
            'product_id': cls.productA.id,
            'product_uom_qty': 10,
            'product_uom': cls.productA.uom_id.id,
            'picking_id': picking_client.id,
            'location_id': cls.pack_location,
            'location_dest_id': cls.customer_location,
            'state': 'waiting',
            'procure_method': 'make_to_order',
        })

        picking_pick = cls.env['stock.picking'].with_context(tracking_disabled=True).create({
            'location_id': cls.stock_location,
            'location_dest_id': cls.pack_location,
            'picking_type_id': cls.picking_type_out,
        })

        cls.MoveObj.create({
            'name': cls.productA.name,
            'product_id': cls.productA.id,
            'product_uom_qty': 10,
            'product_uom': cls.productA.uom_id.id,
            'picking_id': picking_pick.id,
            'location_id': cls.stock_location,
            'location_dest_id': cls.pack_location,
            'move_dest_ids': [(4, dest.id)],
            'state': 'confirmed',
        })
        return picking_pick, picking_client

    def test_not_allow_process_exceeded_demand_quantity(self):
        self.picking_pick.picking_type_id.allow_process_exceeded_demand_qty = False
        with self.assertRaises(UserError):
            self.picking_pick.action_confirm()
            self.picking_pick.action_assign()
            self.picking_pick.button_validate()

            # Record 'done' quantity
            SIT = self.env['stock.immediate.transfer']
            stock_immediate_transfer = SIT.with_context(default_show_transfers=False,
                                                        default_pick_ids=self.picking_pick.ids,
                                                        button_validate_picking_ids=self.picking_pick.ids).create({})
            stock_immediate_transfer.process()

    def test_not_allow_process_exceeded_demand_quantity_multiple_line(self):
        self.picking_pick.picking_type_id.allow_process_exceeded_demand_qty = False
        self.picking_pick.action_confirm()
        self.picking_pick.move_lines[0].quantity_done = 10
        new_move_line = self.env['stock.move.line'].create({
            'product_id': self.picking_pick.move_lines[0].product_id.id,
            'qty_done': 1,
            'product_uom_id': self.picking_pick.move_lines[0].product_uom.id,
            'location_id': self.stock_location,
            'location_dest_id': self.pack_location,
            'company_id':self.picking_pick.company_id.id,
        })
        self.picking_pick.move_line_ids += new_move_line
        with self.assertRaises(UserError):
            self.picking_pick.button_validate()

    def test_allow_process_exceeded_demand_quantity(self):
        self.picking_client.picking_type_id.allow_process_exceeded_demand_qty = True
        self.picking_client.action_confirm()
        self.picking_client.move_lines[0].quantity_done = 12

        overprocessed_wizard_dict = self.picking_client.button_validate()

        self.assertEqual(
            self.picking_client.move_lines[0].quantity_done,
            self.picking_client.move_lines[0].product_uom_qty,
            'Quanitiy_done not ok'
        )
