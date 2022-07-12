from odoo import fields, _
from odoo.tests import Form, tagged
from odoo.tools import float_compare

from .common import TestCommon
from odoo.exceptions import ValidationError

@tagged('post_install', '-at_install')
class TestRepair(TestCommon):

    def test_onchange_lot_id_01(self):
        """
        [Form Test] - TC01

        - Case: Test change lot of repair order, which has product tracking by serial
        - Expected Result:
            + location of repair order will be updated based on location which contains lot
            + product qty of repair order will be updated to 1
        """
        with Form(self.repair1) as f:
            f.lot_id = self.lot3
            f.partner_id = self.partner
            self.assertTrue(f.location_id == self.repair_location)
            self.assertTrue(float_compare(f.product_qty, 1, precision_digits=self.precision) == 0)

    def test_onchange_lot_id_02(self):
        """
        [Form Test] - TC02

        - Case: Test change lot of repair order, which has product tracking by lot
        - Expected Result:
            + location of repair order will be updated based on location which contains lot
            + product qty of repair order will be kept
        """
        with Form(self.repair2) as f:
            f.lot_id = self.lot4
            f.partner_id = self.partner
            self.assertTrue(f.location_id == self.repair_location)
            self.assertTrue(float_compare(f.product_qty, 2, precision_digits=self.precision) == 0)

    def test_onchange_operation_type_01(self):
        """
        [Form Test] - TC03

        - Case: Test create repair lines, in which some lines has type add, some lines has type remove.
            Repair order already has location
        - Expected Result:
            + location of repair line, which type is add will be updated based on location of repair order
            + location of repair line, which type is remove will be kept
        """
        with Form(self.repair1) as f:
            with f.operations.new() as line:
                line.type = 'add'
                line.product_id = self.product_part_serial
                line.lot_id = self.lot5
                self.assertTrue(line.location_id == f.location_id)

            with f.operations.new() as line:
                line.type = 'remove'
                line.product_id = self.product_part_lot
                line.lot_id = self.lot6
                self.assertTrue(line.location_id != f.location_id)
            f.partner_id = self.partner

    def test_onchange_operation_type_02(self):
        """
        [Form Test] - TC04

        - Case: Test create repair lines, in which some lines has type add, some lines has type remove.
            Repair order disn't have location
        - Expected Result:
            + location of repair line, which type is add will not be set
            + location of repair line, which type is remove will be kept
        """
        with Form(self.repair1) as f:
            f.location_id = self.env['stock.location']
            with f.operations.new() as line:
                line.type = 'remove'
                line.product_id = self.product_part_lot
                line.lot_id = self.lot6
                self.assertTrue(line.location_id)

            with f.operations.new() as line:
                line.type = 'add'
                line.product_id = self.product_part_serial
                self.assertTrue(not line.location_id)
                line.lot_id = self.lot5
                # set location for line because it is required field
                line.location_id = self.repair_location
            f.partner_id = self.partner
            # set location for repair order because it is required field
            f.location_id = self.repair_location

    def test_line_onchange_lot_id_01(self):
        """
        [Form Test] - TC05

        - Case: Test change lot of repair line, which has product tracking by serial
        - Expected Result:
            + current location of repair order will be updated based on location which contains lot
            + product qty of repair order will be updated to 1
        """
        with Form(self.repair1) as f:
            f.partner_id = self.partner
            with f.operations.new() as line:
                line.type = 'add'
                line.product_id = self.product_part_serial
                line.product_uom_qty = 2
                line.lot_id = self.lot5
                self.assertTrue(line.src_location_id == self.warehouse_location)
                self.assertTrue(float_compare(line.product_uom_qty, 1, precision_digits=self.precision) == 0)

    def test_line_onchange_lot_id_02(self):
        """
        [Form Test] - TC06

        - Case: Test change lot of repair line, which has product tracking by lot
        - Expected Result:
            + current location of repair order will be updated based on location which contains lot
            + product qty of repair order will be kept
        """
        with Form(self.repair1) as f:
            f.partner_id = self.partner
            with f.operations.new() as line:
                line.type = 'add'
                line.product_id = self.product_part_lot
                line.product_uom_qty = 2
                line.lot_id = self.lot6
                self.assertTrue(line.src_location_id == self.warehouse_location)
                self.assertTrue(float_compare(line.product_uom_qty, 2, precision_digits=self.precision) == 0)

    def test_onchange_location_id_01(self):
        """
        [Form Test] - TC07

        - Case: Test change location of repair order
        - Expected Result:
            + repair location of repair line, which type is add will be updated based on location of repair order
            + repair location of repair line, which type is remove will be kept
        """
        with Form(self.repair1) as f:
            with f.operations.new() as line:
                line.type = 'remove'
                line.product_id = self.product_part_lot
                line.lot_id = self.lot6
                self.assertTrue(line.location_id != self.stock_location)

            with f.operations.new() as line:
                line.type = 'add'
                line.product_id = self.product_part_serial
                line.lot_id = self.lot5
                self.assertTrue(line.location_id == self.stock_location)

            # change location of repair order
            f.location_id = self.repair_location

            with f.operations.edit(0) as line:
                self.assertTrue(line.location_id != self.repair_location)

            with f.operations.edit(1) as line:
                self.assertTrue(line.location_id == self.repair_location)
            f.partner_id = self.partner

    def test_constraint_product_lot_01(self):
        """
        [Functional Test] - TC01

        - Case: Test create repair order, which has product tracking by serial but product quantity > 1
        - Expected Result:
            + ValidationError occurs
        """
        with self.assertRaises(ValidationError):
            self.env['repair.order'].create({
                'product_id': self.product_to_repair_serial.id,
                'product_qty': 2.0,
                'product_uom': self.uom_unit.id,
                'lot_id': self.lot2.id,
                'guarantee_limit': fields.Date.from_string('2022-09-12'),
                'location_id': self.stock_location.id,
            })

    def test_line_constraint_product_lot_01(self):
        """
        [Functional Test] - TC02

        - Case: Test create repair order, which has repair line contains product tracking by serial but product uom quantity > 1
        - Expected Result:
            + ValidationError occurs
        """
        with self.assertRaises(ValidationError):
            self.env['repair.order'].create({
                'product_id': self.product_to_repair_serial.id,
                'product_qty': 1.0,
                'product_uom': self.uom_unit.id,
                'lot_id': self.lot2.id,
                'guarantee_limit': fields.Date.from_string('2022-09-12'),
                'location_id': self.stock_location.id,
                'operations': [
                    (0, 0, {
                        'name': 'Product Part Serial',
                        'type': 'add',
                        'product_id': self.product_part_serial.id,
                        'lot_id': self.lot5.id,
                        'product_uom_qty': 2.0,
                        'product_uom': self.uom_unit.id,
                        'price_unit': 100,
                        'location_id': self.stock_location.id,
                        'location_dest_id': self.product_part_serial.property_stock_production.id,
                    })
                ]
            })

    def test_confirm_repair_order_01(self):
        """
        [Functional Test] - TC03

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is customer location
            + repair lines has type add
            + current location of repair lines are same
        - Expected Result:
            + repair order state changed to confirmed
            + there is 1 generated picking to transfer products from current location to customer location
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.customer_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Consumable',
                    'type': 'add',
                    'product_id': self.product_part_consu.id,
                    'product_uom_qty': 2.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 100,
                    'src_location_id': self.warehouse_location.id,
                    'location_id': self.customer_location.id,
                    'location_dest_id': self.product_part_consu.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Product',
                    'type': 'add',
                    'product_id': self.product_part_product.id,
                    'product_uom_qty': 1.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 150,
                    'src_location_id': self.warehouse_location.id,
                    'location_id': self.customer_location.id,
                    'location_dest_id': self.product_part_product.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        repair.action_validate()

        self.assertTrue(repair.state == 'confirmed')
        # check picking
        self.assertTrue(repair.picking_ids and len(repair.picking_ids) == 1)
        picking = repair.picking_ids[0]
        self.assertTrue(picking.location_id == self.warehouse_location)
        self.assertTrue(picking.location_dest_id == self.customer_location)
        picking_type = self.env.ref('to_repair_supply.picking_type_repair_supply')
        self.assertTrue(len(picking.move_lines) == 2)
        self.assertTrue(picking_type == picking.move_lines.picking_type_id)
        self.assertTrue(picking.move_lines.product_id == repair.operations.product_id)

        # check stock move of picking
        stock_move_part_consu = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_consu)[0]
        self.assertTrue(stock_move_part_consu.location_id == self.warehouse_location)
        self.assertTrue(stock_move_part_consu.location_dest_id == self.customer_location)
        self.assertTrue(float_compare(stock_move_part_consu.product_uom_qty, 2.0, precision_digits=self.precision) == 0)

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        self.assertTrue(stock_move_part_product.location_id == self.warehouse_location)
        self.assertTrue(stock_move_part_product.location_dest_id == self.customer_location)
        self.assertTrue(float_compare(stock_move_part_product.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

    def test_confirm_repair_order_02(self):
        """
        [Functional Test] - TC04

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is customer location
            + repair lines has type add
            + current location of repair lines are different (2 locations)
        - Expected Result:
            + repair order state changed to confirmed
            + there is 2 generated picking to transfer products from current location to customer location
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.customer_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Consumable',
                    'type': 'add',
                    'product_id': self.product_part_consu.id,
                    'product_uom_qty': 2.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 100,
                    'src_location_id': self.warehouse_location_shelf1.id,
                    'location_id': self.customer_location.id,
                    'location_dest_id': self.product_part_consu.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Product',
                    'type': 'add',
                    'product_id': self.product_part_product.id,
                    'product_uom_qty': 1.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 150,
                    'src_location_id': self.warehouse_location_shelf2.id,
                    'location_id': self.customer_location.id,
                    'location_dest_id': self.product_part_product.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        repair.action_validate()

        self.assertTrue(repair.state == 'confirmed')
        # check picking
        self.assertTrue(repair.picking_ids and len(repair.picking_ids) == 2)
        pickings = repair.picking_ids
        self.assertTrue(pickings.location_id == repair.operations.src_location_id)
        self.assertTrue(pickings.location_dest_id == self.customer_location)
        self.assertTrue(pickings[0].move_lines and len(pickings[0].move_lines) == 1)
        self.assertTrue(pickings[1].move_lines and len(pickings[1].move_lines) == 1)
        picking_type = self.env.ref('to_repair_supply.picking_type_repair_supply')
        self.assertTrue(picking_type == pickings.picking_type_id)
        self.assertTrue(picking_type == pickings.move_lines.picking_type_id)
        self.assertTrue(pickings.move_lines.product_id == repair.operations.product_id)

        # check stock move of picking
        stock_move_part_consu = pickings.move_lines.filtered(lambda m: m.product_id == self.product_part_consu)[0]
        self.assertTrue(stock_move_part_consu.location_id == self.warehouse_location_shelf1)
        self.assertTrue(stock_move_part_consu.location_dest_id == self.customer_location)
        self.assertTrue(float_compare(stock_move_part_consu.product_uom_qty, 2.0, precision_digits=self.precision) == 0)

        stock_move_part_product = pickings.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        self.assertTrue(stock_move_part_product.location_id == self.warehouse_location_shelf2)
        self.assertTrue(stock_move_part_product.location_dest_id == self.customer_location)
        self.assertTrue(float_compare(stock_move_part_product.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

    def test_confirm_repair_order_03(self):
        """
        [Functional Test] - TC05

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is customer location
            + repair lines has type add
            + there is 1 repair line, which has product with type is consumable and does not have current location on repair line
        - Expected Result:
            + repair order state changed to confirmed
            + there is not generated picking to transfer products from current location to customer location
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.customer_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Consumable',
                    'type': 'add',
                    'product_id': self.product_part_consu.id,
                    'product_uom_qty': 2.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 100,
                    'location_id': self.customer_location.id,
                    'location_dest_id': self.product_part_consu.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        repair.action_validate()

        self.assertTrue(repair.state == 'confirmed')
        self.assertTrue(not repair.picking_ids)

    def test_confirm_repair_order_04(self):
        """
        [Functional Test] - TC06

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is not customer location
            + repair lines has type add
            + there is 1 repair line, which has product with type is consumable and does not have current location on repair line
        - Expected Result:
            + repair order state changed to confirmed
            + there is not generated picking to transfer products from current location to customer location
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.repair_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Consumable',
                    'type': 'add',
                    'product_id': self.product_part_consu.id,
                    'product_uom_qty': 2.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 100,
                    'location_id': self.repair_location.id,
                    'location_dest_id': self.product_part_consu.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        repair.action_validate()

        self.assertTrue(repair.state == 'confirmed')
        self.assertTrue(not repair.picking_ids)

    def test_confirm_repair_order_05(self):
        """
        [Functional Test] - TC07

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is not customer location
            + repair lines has type add
            + there is 1 repair line, which has product with type is storable with enough quantity in repair location
            and does not have current location on repair line
        - Expected Result:
            + repair order state changed to confirmed
            + there is not generated picking to transfer products from current location to customer location
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.repair_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Product Enough',
                    'type': 'add',
                    'product_id': self.product_part_product_enough.id,
                    'product_uom_qty': 2.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 100,
                    'location_id': self.repair_location.id,
                    'location_dest_id': self.product_part_consu.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        repair.action_validate()

        self.assertTrue(repair.state == 'confirmed')
        self.assertTrue(not repair.picking_ids)


    def test_confirm_repair_order_06(self):
        """
        [Functional Test] - TC08

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is not customer location
            + repair lines has type add
            + there is 1 repair line, which has product with type is storable but does not have enough quantity in repair location,
            and does not have current location on repair line
        - Expected Result:
            + ValidationError occurs
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.repair_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Product',
                    'type': 'add',
                    'product_id': self.product_part_product.id,
                    'product_uom_qty': 1.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 150,
                    'location_id': self.repair_location.id,
                    'location_dest_id': self.product_part_product.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        with self.assertRaises(ValidationError):
            repair.action_validate()

    def test_confirm_repair_order_07(self):
        """
        [Functional Test] - TC09

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is not customer location
            + repair lines has type add
            + current location of repair lines are same
            + products in repair lines has type consumable or storable
            + product has type storable does not have enough quantity in repair location
        - Expected Result:
            + repair order state changed to confirmed
            + there is 1 generated picking to transfer products from current location to repair location
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.repair_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Consumable',
                    'type': 'add',
                    'product_id': self.product_part_consu.id,
                    'product_uom_qty': 2.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 100,
                    'src_location_id': self.warehouse_location.id,
                    'location_id': self.repair_location.id,
                    'location_dest_id': self.product_part_consu.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Product',
                    'type': 'add',
                    'product_id': self.product_part_product.id,
                    'product_uom_qty': 1.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 150,
                    'src_location_id': self.warehouse_location.id,
                    'location_id': self.repair_location.id,
                    'location_dest_id': self.product_part_product.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        repair.action_validate()

        self.assertTrue(repair.state == 'confirmed')
        # check picking
        self.assertTrue(repair.picking_ids and len(repair.picking_ids) == 1)
        picking = repair.picking_ids[0]
        self.assertTrue(picking.location_id == self.warehouse_location)
        self.assertTrue(picking.location_dest_id == self.repair_location)
        picking_type = self.env.ref('to_repair_supply.picking_type_repair_supply')
        self.assertTrue(len(picking.move_lines) == 2)
        self.assertTrue(picking_type == picking.picking_type_id)
        self.assertTrue(picking_type == picking.move_lines.picking_type_id)
        self.assertTrue(picking.move_lines.product_id == repair.operations.product_id)

        # check stock move of picking
        stock_move_part_consu = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_consu)[0]
        self.assertTrue(stock_move_part_consu.location_id == self.warehouse_location)
        self.assertTrue(stock_move_part_consu.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(stock_move_part_consu.product_uom_qty, 2.0, precision_digits=self.precision) == 0)

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        self.assertTrue(stock_move_part_product.location_id == self.warehouse_location)
        self.assertTrue(stock_move_part_product.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(stock_move_part_product.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

    def test_confirm_repair_order_08(self):
        """
        [Functional Test] - TC10

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is not customer location
            + repair lines has type add
            + current location of repair lines are different (2 locations)\
            + products in repair lines has type consumable or storable
            + product has type storable does not have enough quantity in repair location
        - Expected Result:
            + repair order state changed to confirmed
            + there is 2 generated picking to transfer products from current location to repair location
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.repair_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Consumable',
                    'type': 'add',
                    'product_id': self.product_part_consu.id,
                    'product_uom_qty': 2.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 100,
                    'src_location_id': self.warehouse_location_shelf1.id,
                    'location_id': self.repair_location.id,
                    'location_dest_id': self.product_part_consu.property_stock_production.id,
                }),
                (0, 0, {
                    'name': 'Product Part Product',
                    'type': 'add',
                    'product_id': self.product_part_product.id,
                    'product_uom_qty': 1.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 150,
                    'src_location_id': self.warehouse_location_shelf2.id,
                    'location_id': self.repair_location.id,
                    'location_dest_id': self.product_part_product.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        repair.action_validate()

        self.assertTrue(repair.state == 'confirmed')
        # check picking
        self.assertTrue(repair.picking_ids and len(repair.picking_ids) == 2)
        pickings = repair.picking_ids
        self.assertTrue(pickings.location_id == repair.operations.src_location_id)
        self.assertTrue(pickings.location_dest_id == self.repair_location)
        self.assertTrue(pickings[0].move_lines and len(pickings[0].move_lines) == 1)
        self.assertTrue(pickings[1].move_lines and len(pickings[1].move_lines) == 1)
        picking_type = self.env.ref('to_repair_supply.picking_type_repair_supply')
        self.assertTrue(picking_type == pickings.picking_type_id)
        self.assertTrue(picking_type == pickings.move_lines.picking_type_id)
        self.assertTrue(pickings.move_lines.product_id == repair.operations.product_id)

        # check stock move of picking
        stock_move_part_consu = pickings.move_lines.filtered(lambda m: m.product_id == self.product_part_consu)[0]
        self.assertTrue(stock_move_part_consu.location_id == self.warehouse_location_shelf1)
        self.assertTrue(stock_move_part_consu.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(stock_move_part_consu.product_uom_qty, 2.0, precision_digits=self.precision) == 0)

        stock_move_part_product = pickings.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        self.assertTrue(stock_move_part_product.location_id == self.warehouse_location_shelf2)
        self.assertTrue(stock_move_part_product.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(stock_move_part_product.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

    def test_confirm_repair_order_09(self):
        """
        [Functional Test] - TC11

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is not customer location
            + there is 1 repair line, which has type add, repair location differ from repair location of repair order
        - Expected Result:
            + ValidationError occurs
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.repair_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Consumable',
                    'type': 'add',
                    'product_id': self.product_part_consu.id,
                    'product_uom_qty': 1.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 150,
                    'location_id': self.warehouse_location.id,
                    'location_dest_id': self.product_part_product.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        with self.assertRaises(ValidationError):
            repair.action_validate()

    def test_confirm_repair_order_10(self):
        """
        [Functional Test] - TC12

        - Case: Test confirm repair order, which has product is consumable, and:
            + repair location is not customer location
            + there is 1 repair line, which has type add, repair location and current location are same
        - Expected Result:
            + ValidationError occurs
        """
        repair = self.env['repair.order'].create({
            'product_id': self.product_to_repair_consu.id,
            'product_qty': 1.0,
            'product_uom': self.uom_unit.id,
            'guarantee_limit': fields.Date.from_string('2022-09-12'),
            'location_id': self.repair_location.id,
            'operations': [
                (0, 0, {
                    'name': 'Product Part Consumable',
                    'type': 'add',
                    'product_id': self.product_part_consu.id,
                    'product_uom_qty': 1.0,
                    'product_uom': self.uom_unit.id,
                    'price_unit': 150,
                    'src_location_id': self.repair_location.id,
                    'location_id': self.repair_location.id,
                    'location_dest_id': self.product_part_product.property_stock_production.id,
                })
            ]
        })
        # confirm repair order
        with self.assertRaises(ValidationError):
            repair.action_validate()

    def test_confirm_repair_order_11(self):
        """
        [Functional Test] - TC13
        This case will be combined in TC14

        - Case: Test confirm repair order, which has product is storable, and:
            + repair location is not customer location
            + available quantity of product of repair order in repair location is not enough for repairing
            + there are some locations, which has enough quantity of this product for repairing
            + repair lines has type add and has same current location
            + available quantity of product of repair line in repair location is not enough for repairing
        - Expected Result:
            + There is a returned wizard to ask about source location of product of repair order
        """
        pass

    def test_confirm_repair_order_12(self):
        """
        [Functional Test] - TC14

        - Case: Test confirm repair order, which has product is storable, and:
            + product uom is not default unit of product
            + repair location is not customer location
            + available quantity of product of repair order in repair location is not enough for repairing
            + there are some locations, which has enough quantity of this product for repairing
            + repair lines has type add and has same current location
            + available quantity of product of repair line in repair location is not enough for repairing
        - Expected Result:
            + There is a returned wizard to ask about source location of product of repair order
        """
        # confirm repair order
        result = self.repair_with_supply2.action_validate()
        expected_result = {
            'name': self.repair_with_supply2.product_id.display_name + _(': Insufficient Quantity To Repair'),
            'view_mode': 'form',
            'res_model': 'stock.warn.insufficient.qty.repair',
            'view_id': self.env.ref('repair.stock_warn_insufficient_qty_repair_form_view').id,
            'type': 'ir.actions.act_window',
            'context': {
                    'default_product_id': self.repair_with_supply2.product_id.id,
                    'default_location_id': self.repair_with_supply2.location_id.id,
                    'default_repair_id': self.repair_with_supply2.id,
                    'default_quantity': self.repair_with_supply2.product_uom._compute_quantity(self.repair_with_supply2.product_qty, self.repair_with_supply2.product_id.uom_id),
                    'default_product_uom_name': self.repair_with_supply2.product_id.uom_name
            },
            'target': 'new'
        }
        self.assertTrue(result == expected_result)
        self.assertTrue(self.repair_with_supply.state == 'draft')

    def test_confirm_repair_order_13(self):
        """
        [Functional Test] - TC15
        This case will be combined in TC16

        - Case: Test confirm repair order, which has product is storable, and:
            + repair location is not customer location
            + available quantity of product of repair order in repair location is not enough for repairing
            + there are some locations, which has enough quantity of this product for repairing
            + repair lines has type add and has same current location
            + available quantity of product of repair line in repair location is not enough for repairing
            + after wizard is opened, select source location, which does not have enough available quantity
        - Expected Result:
            + ValidationError occurs
        """
        pass

    def test_confirm_repair_order_14(self):
        """
        [Functional Test] - TC16

        - Case: Test confirm repair order, which has product is storable, and:
            + product uom is not default unit of product
            + repair location is not customer location
            + available quantity of product of repair order in repair location is not enough for repairing
            + there are some locations, which has enough quantity of this product for repairing
            + repair lines has type add and has same current location
            + available quantity of product of repair line in repair location is not enough for repairing
            + after wizard is opened, select source location, which does not have enough available quantity
        - Expected Result:
            + ValidationError occurs
        """
        # confirm repair order
        self.repair_with_supply2.action_validate()

        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply2.product_id.id,
            'default_location_id': self.repair_with_supply2.location_id.id,
            'default_repair_id': self.repair_with_supply2.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        self.assertTrue(len(f.quant_ids) == 2)
        # increase available of product in selected location but less than required number
        self.env['stock.quant']._update_available_quantity(self.product_to_repair, self.warehouse_location_shelf2, 10)
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf2

        wizard = f.save()
        # confirm on wizard
        with self.assertRaises(ValidationError):
            wizard.action_done()

    def test_confirm_repair_order_15(self):
        """
        [Functional Test] - TC17
        This case will be combined in TC18

        - Case: Test confirm repair order, which has product is storable, and:
            + repair location is not customer location
            + available quantity of product of repair order in repair location is not enough for repairing
            + there are some locations, which has enough quantity of this product for repairing
            + repair lines has type add and has same current location
            + available quantity of product of repair line in repair location is not enough for repairing
            + after wizard is opened, select source location, which has enough available quantity
        - Expected Result:
            + repair order state changed to confirmed
            + there is 1 generated picking to transfer products from current location to repair location
            + there is 1 stock move is done to transfer product in repair order from source location to repair location
            + there is 1 stock move is reserved to transfer product on repair order from repair location to repair location
        """
        pass

    def test_confirm_repair_order_16(self):
        """
        [Functional Test] - TC18

        - Case: Test confirm repair order, which has product is storable, and:
            + product uom is not default unit of product
            + repair location is not customer location
            + available quantity of product of repair order in repair location is not enough for repairing
            + there are some locations, which has enough quantity of this product for repairing
            + repair lines has type add and has same current location
            + available quantity of product of repair line in repair location is not enough for repairing
            + after wizard is opened, select source location, which has enough available quantity
        - Expected Result:
            + repair order state changed to confirmed
            + there is 1 generated picking to transfer products from current location to repair location
            + there is 1 stock move is done to transfer product in repair order from source location to repair location
            + there is 1 stock move is reserved to transfer product on repair order from repair location to repair location
        """
        # confirm repair order
        self.repair_with_supply2.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply2.product_id.id,
            'default_location_id': self.repair_with_supply2.location_id.id,
            'default_repair_id': self.repair_with_supply2.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # increase available of product in selected location but less than required number
        self.env['stock.quant']._update_available_quantity(self.product_to_repair, self.warehouse_location_shelf1, 10)
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()

        self.assertTrue(self.repair_with_supply2.state == 'confirmed')
        # check picking
        self.assertTrue(self.repair_with_supply2.picking_ids and len(self.repair_with_supply2.picking_ids) == 1)
        picking = self.repair_with_supply2.picking_ids[0]
        self.assertTrue(picking.location_id == self.warehouse_location)
        self.assertTrue(picking.location_dest_id == self.repair_location)
        self.assertTrue(picking.move_lines and len(picking.move_lines) == 3)
        picking_type = self.env.ref('to_repair_supply.picking_type_repair_supply')
        self.assertTrue(picking_type == picking.picking_type_id)
        self.assertTrue(picking_type == picking.move_lines.picking_type_id)
        self.assertTrue(picking.move_lines.product_id == self.repair_with_supply2.operations.product_id - self.product_part_remove)

        # check stock move of picking
        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        self.assertTrue(stock_move_part_product.location_id == self.warehouse_location)
        self.assertTrue(stock_move_part_product.product_uom == self.uom_dozen)
        self.assertTrue(stock_move_part_product.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(stock_move_part_product.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        self.assertTrue(stock_move_part_lot.location_id == self.warehouse_location)
        self.assertTrue(stock_move_part_lot.product_uom == self.uom_dozen)
        self.assertTrue(stock_move_part_lot.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(stock_move_part_lot.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        self.assertTrue(stock_move_part_serial.location_id == self.warehouse_location)
        self.assertTrue(stock_move_part_serial.product_uom == self.uom_unit)
        self.assertTrue(stock_move_part_serial.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(stock_move_part_serial.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

        # check supply move of product in repair order
        supply_move = self.repair_with_supply2.supply_stock_move_id
        self.assertTrue(supply_move and supply_move.state == 'done')
        self.assertTrue(supply_move.product_id == self.product_to_repair)
        self.assertTrue(supply_move.product_uom == self.uom_dozen)
        self.assertTrue(supply_move.location_id == self.warehouse_location_shelf1)
        self.assertTrue(supply_move.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(supply_move.product_uom_qty, 1.0, precision_digits = self.precision) == 0)

        # check reserved move of product in repair order
        reseved_move = self.repair_with_supply2.reserved_completion_stock_move_id
        self.assertTrue(reseved_move and reseved_move.state == 'assigned')
        self.assertTrue(reseved_move.product_id == self.product_to_repair)
        self.assertTrue(supply_move.product_uom == self.uom_dozen)
        self.assertTrue(reseved_move.location_id == self.repair_location)
        self.assertTrue(reseved_move.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(reseved_move.product_uom_qty, 1.0, precision_digits = self.precision) == 0)

    def test_confirm_repair_order_17(self):
        """
        [Functional Test] - TC33

        - Case: Test confirm repair order, which has product is storable, and:
            + repair location is not customer location
            + available quantity of product of repair order in repair location is not enough for repairing
            + there are some locations, which has enough quantity of this product for repairing
            + repair lines has type add and has same current location, they have same product with tracking is serial, but different serial number
            + available quantity of product of repair line in repair location is not enough for repairing
            + after wizard is opened, select source location, which has enough available quantity
        - Expected Result:
            + repair order state changed to confirmed
            + there is 1 generated picking to transfer products from current location to repair location
            + there is 1 stock move is done to transfer product in repair order from source location to repair location
            + there is 1 stock move is reserved to transfer product on repair order from repair location to repair location
        """
        # confirm repair order
        self.repair_with_supply3.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply3.product_id.id,
            'default_location_id': self.repair_with_supply3.location_id.id,
            'default_repair_id': self.repair_with_supply3.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()

        self.assertTrue(self.repair_with_supply3.state == 'confirmed')
        # check picking
        self.assertTrue(self.repair_with_supply3.picking_ids and len(self.repair_with_supply3.picking_ids) == 1)
        picking = self.repair_with_supply3.picking_ids[0]
        self.assertTrue(picking.location_id == self.warehouse_location)
        self.assertTrue(picking.location_dest_id == self.repair_location)
        self.assertTrue(picking.move_lines and len(picking.move_lines) == 2)
        picking_type = self.env.ref('to_repair_supply.picking_type_repair_supply')
        self.assertTrue(picking_type == picking.picking_type_id)
        self.assertTrue(picking_type == picking.move_lines.picking_type_id)
        self.assertTrue(picking.move_lines.product_id == self.repair_with_supply3.operations.product_id)

        # check stock move of picking
        stock_move_part_serials = picking.move_lines.filtered(lambda m:
                                                              m.product_id == self.product_part_serial_not_enough)
        self.assertTrue(len(stock_move_part_serials) == 2)
        self.assertTrue(stock_move_part_serials.location_id == self.warehouse_location)
        self.assertTrue(stock_move_part_serials.product_uom == self.uom_unit)
        self.assertTrue(stock_move_part_serials.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(stock_move_part_serials[0].product_uom_qty, 1.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(stock_move_part_serials[1].product_uom_qty, 1.0, precision_digits=self.precision) == 0)

        # check supply move of product in repair order
        supply_move = self.repair_with_supply3.supply_stock_move_id
        self.assertTrue(supply_move and supply_move.state == 'done')
        self.assertTrue(supply_move.product_id == self.product_to_repair)
        self.assertTrue(supply_move.product_uom == self.uom_unit)
        self.assertTrue(supply_move.location_id == self.warehouse_location_shelf1)
        self.assertTrue(supply_move.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(supply_move.product_uom_qty, 1.0, precision_digits = self.precision) == 0)

        # check reserved move of product in repair order
        reseved_move = self.repair_with_supply3.reserved_completion_stock_move_id
        self.assertTrue(reseved_move and reseved_move.state == 'assigned')
        self.assertTrue(reseved_move.product_id == self.product_to_repair)
        self.assertTrue(supply_move.product_uom == self.uom_unit)
        self.assertTrue(reseved_move.location_id == self.repair_location)
        self.assertTrue(reseved_move.location_dest_id == self.repair_location)
        self.assertTrue(float_compare(reseved_move.product_uom_qty, 1.0, precision_digits = self.precision) == 0)

    def test_start_repair_order_01(self):
        """
        [Functional Test] - TC19

        - Case: Start repair order in case repair order has non-confirmed picking
        - Expected Result:
            + ValidationError occurs
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()

        # start repair
        with self.assertRaises(ValidationError):
            self.repair_with_supply.action_repair_start()

    def test_start_repair_order_02(self):
        """
        [Functional Test] - TC20
        - Case:
            + Confirm repair order and validate the supply picking.
            + Create a new picking to move supplied products to another location and do assign it.
        - Expected Result:
            + The supplied products is reserved for the repair order.
            + There is no products reserved for the new picking.
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()

        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()

        # Check that all supplied products have been reserved for the repair order
        reserve_move_part_product = self.repair_with_supply.move_ids.filtered(
            lambda m: m.product_id == self.product_part_product and \
                      m.location_id == self.repair_location and \
                      m.location_dest_id == self.product_part_product.property_stock_production
            )
        self.assertTrue(reserve_move_part_product, "There is no reserve move for product_part_product.")
        self.assertEqual(reserve_move_part_product.reserved_availability, 3.0, "Reserved qty for product_part_product should be 3.0.")

        reserve_move_part_lot = self.repair_with_supply.move_ids.filtered(
            lambda m: m.product_id == self.product_part_lot and \
                      m.location_id == self.repair_location and \
                      m.location_dest_id == self.product_part_lot.property_stock_production
            )
        self.assertTrue(reserve_move_part_lot, "There is no reserve move for product_part_lot.")
        self.assertEqual(reserve_move_part_lot.reserved_availability, 2.0, "Reserved qty for product_part_lot should be 3.0.")

        reserve_move_part_serial = self.repair_with_supply.move_ids.filtered(
            lambda m: m.product_id == self.product_part_serial and \
                      m.location_id == self.repair_location and \
                      m.location_dest_id == self.product_part_serial.property_stock_production
            )
        self.assertTrue(reserve_move_part_serial, "There is no reserve move for product_part_serial.")
        self.assertEqual(reserve_move_part_serial.reserved_availability, 1.0, "Reserved qty for product_part_serial should be 3.0.")

        # create new picking to transfer product to other location
        new_picking = self.env['stock.picking'].create({
            'location_id': self.repair_location.id,
            'location_dest_id': self.warehouse_location.id,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
        })

        new_move = self.env['stock.move'].create({
            'name': 'Test Stock Move',
            'location_id': self.repair_location.id,
            'location_dest_id': self.warehouse_location.id,
            'picking_id': new_picking.id,
            'product_id': self.product_part_product.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
        })
        new_picking.action_confirm()
        new_picking.action_assign()

        # There is no products reserved for new_picking
        self.assertFalse(new_picking.move_line_ids, "There should be no products reserved for new_picking.")

    def test_start_repair_order_03(self):
        """
        [Functional Test] - TC21
        - Case:
            + Confirm repair order and validate the supply picking.
            + Start the repair order.
            + Request for more supply parts.
            + Validate the new supply picking.
        - Expected Result:
            + After requesting, a new supply picking is created.
            + The requested quantities and products will be added to the repair's operations.
            + After validating the supply, the reserving move will auto reserve that parts.
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()

        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()

        # Start the repair
        self.repair_with_supply.action_repair_start()

        # Update more quantity available for parts
        self.env['stock.quant']._update_available_quantity(self.product_part_product, self.warehouse_location, 10)
        self.env['stock.quant']._update_available_quantity(self.product_part_remove, self.warehouse_location, 10)

        # Request more supplies
        f = Form(self.env['wizard.repair.request.supply'].with_context({
            'active_model': self.repair_with_supply._name,
            'active_id': self.repair_with_supply.id,
        }))
        with f.line_ids.new() as line:
            line.product_id = self.product_part_product
            line.src_location_id = self.warehouse_location
            line.location_dest_id = self.product_part_product.property_stock_production
            line.product_uom_qty = 2.0
        with f.line_ids.new() as line:
            line.product_id = self.product_part_remove
            line.src_location_id = self.warehouse_location
            line.location_dest_id = self.product_part_remove.property_stock_production
            line.product_uom_qty = 2.0
        wizard = f.save()
        wizard.action_request()

        # Check if a new supply picking is created
        new_picking = self.repair_with_supply.picking_ids - picking
        self.assertTrue(new_picking, "New supply picking should be created.")
        supply_move_part_product = new_picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)
        supply_move_part_remove = new_picking.move_lines.filtered(lambda m: m.product_id == self.product_part_remove)
        self.assertEqual(supply_move_part_product.product_uom_qty, 2.0, "New supply quantity for product_part_product should be 2.0")
        self.assertEqual(supply_move_part_remove.product_uom_qty, 2.0, "New supply quantity for product_part_remove should be 2.0")

        # Check if the requested supplies is updated on the repair's operations
        repair_line_part_product = self.repair_with_supply.operations.filtered(lambda o: o.type == 'add' and o.product_id == self.product_part_product)
        self.assertEqual(repair_line_part_product.product_uom_qty, 5.0, "The new quantity for product_part_product should be 3+2=5.")

        repair_line_part_remove = self.repair_with_supply.operations.filtered(lambda o: o.type == 'add' and o.product_id == self.product_part_remove)
        self.assertTrue(repair_line_part_remove, "There should be a new repair line for repair_line_part_remove.")
        self.assertEqual(repair_line_part_remove.product_uom_qty, 2.0, "The quantity for repair_line_part_remove should be 2.")

        # Check if the reserving stock moves have been updated
        reserve_move_part_product = self.repair_with_supply.move_ids.filtered(
            lambda m: m.product_id == self.product_part_product and \
                      m.location_id == self.repair_location and \
                      m.location_dest_id == self.product_part_product.property_stock_production
            )
        self.assertEqual(reserve_move_part_product.reserved_availability, 3.0, "Reserved quantity for product_part_product should still be 3.0.")

        reserve_move_part_remove = self.repair_with_supply.move_ids.filtered(
            lambda m: m.product_id == self.product_part_remove and \
                      m.location_id == self.repair_location and \
                      m.location_dest_id == self.product_part_remove.property_stock_production
            )
        self.assertTrue(reserve_move_part_remove, "There is no reserve move for product_part_remove.")
        self.assertEqual(reserve_move_part_remove.reserved_availability, 0.0, "Reserved quantity for product_part_remove should be 0.0.")

        # Validate the new supply picking
        supply_move_part_product.move_line_ids[0].qty_done = 2.0
        supply_move_part_remove.move_line_ids[0].qty_done = 2.0
        new_picking._action_done()

        # Check the reserving quantity for repair order again
        self.assertEqual(reserve_move_part_product.reserved_availability, 5.0, "Reserved quantity for product_part_product should still be 5.0.")
        self.assertEqual(reserve_move_part_remove.reserved_availability, 2.0, "Reserved quantity for product_part_remove should be 2.0.")

    def test_start_repair_order_04(self):
        """
        [Functional Test] - TC22

        - Case: Start repair order in case all picking of repair order are confirmed
        - Expected Result:
            + repair order state change to under_repair
            + there are reserved stock moves, which generated to reserve transfer repair line product from repair location to destination location
            when repair end
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()

        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()

        # start repair order
        self.repair_with_supply.action_repair_start()
        self.assertTrue(self.repair_with_supply.state == 'under_repair')
        # check reserved moves of products in repair lines
        part_product_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_product)[0]
        part_product_reserved_move = part_product_line.reserved_completion_stock_move_id
        self.assertTrue(part_product_reserved_move and part_product_reserved_move.state == 'assigned')
        self.assertTrue(part_product_reserved_move.location_id == self.repair_location)
        self.assertTrue(part_product_reserved_move.location_dest_id == part_product_line.location_dest_id)
        self.assertTrue(float_compare(part_product_reserved_move.product_uom_qty, 3.0, precision_digits=self.precision) == 0)

        part_lot_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_lot)[0]
        part_lot_reserved_move = part_lot_line.reserved_completion_stock_move_id
        self.assertTrue(part_lot_reserved_move and part_product_reserved_move.state == 'assigned')
        self.assertTrue(part_lot_reserved_move.location_id == self.repair_location)
        self.assertTrue(part_lot_reserved_move.location_dest_id == part_lot_line.location_dest_id)
        self.assertTrue(float_compare(part_lot_reserved_move.product_uom_qty, 2.0, precision_digits=self.precision) == 0)

        part_serial_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_serial)[0]
        part_serial_reserved_move = part_serial_line.reserved_completion_stock_move_id
        self.assertTrue(part_serial_reserved_move and part_product_reserved_move.state == 'assigned')
        self.assertTrue(part_serial_reserved_move.location_id == self.repair_location)
        self.assertTrue(part_serial_reserved_move.location_dest_id == part_serial_line.location_dest_id)
        self.assertTrue(float_compare(part_serial_reserved_move.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

    def test_cancel_repair_order_01(self):
        """
        [Functional Test] - TC23

        - Case: Cancel repair order in case:
            + all picking of repair order are not confirmed,
            + there is stock move to transfer product of repair order from source location to repair location
        - Expected Result:
            + repair cancel success
            + picking are cancelled
            + there is stock move to transfer product of repair order back from repair location to source location
        """
        # confirm repair oder
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()

        # cancel repair order
        self.repair_with_supply.action_repair_cancel()

        self.assertTrue(self.repair_with_supply.state == 'cancel')

        # check picking
        self.assertTrue(len(self.repair_with_supply.picking_ids) == 1)
        picking = self.repair_with_supply.picking_ids[0]
        self.assertTrue(picking.state == 'cancel')

        # check reserved move of product in repair order
        self.assertTrue(self.repair_with_supply.reserved_completion_stock_move_id.state == 'cancel')

        # check return move of product in repair order
        related_moves = self.repair_with_supply.move_ids
        repair_product_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_to_repair
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location_shelf1
                                                                 and float_compare(m.product_uom_qty, 2.0, precision_digits=self.precision) == 0
                                                                 and m.state =='done')
        self.assertTrue(repair_product_back_stock_moves and len(repair_product_back_stock_moves) == 1)

    def test_cancel_repair_order_02(self):
        """
        [Functional Test] - TC24

        - Case: Cancel repair order in case:
            + all picking of repair order are confirmed,
            + there is stock move to transfer product of repair order from source location to repair location
        - Expected Result:
            + repair cancel success
            + picking are kept as done
            + reserved stock move for product of repair order will be cancelled
            + there is stock move to transfer product of repair order back from repair location to source location
            + there are stock moves to transfer products of repair lines back from repair location to current location
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()

        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # cancel repair order
        self.repair_with_supply.action_repair_cancel()

        self.assertTrue(self.repair_with_supply.state == 'cancel')
        # check picking
        self.assertTrue(len(self.repair_with_supply.picking_ids) == 1)
        picking = self.repair_with_supply.picking_ids[0]
        self.assertTrue(picking.state == 'done')
        # check reserved move of product in repair order
        self.assertTrue(self.repair_with_supply.reserved_completion_stock_move_id.state == 'cancel')

        related_moves = self.repair_with_supply.move_ids
        # check return move of product in repair order
        repair_product_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_to_repair
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location_shelf1
                                                                 and float_compare(m.product_uom_qty, 2.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(repair_product_back_stock_moves and len(repair_product_back_stock_moves) == 1)

        # check return moves of products in repair lines
        part_product_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_product
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location
                                                                 and float_compare(m.product_uom_qty, 3.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_product_back_stock_moves and len(part_product_back_stock_moves) == 1)

        part_lot_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_lot
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location
                                                                 and float_compare(m.product_uom_qty, 2.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_lot_back_stock_moves and len(part_lot_back_stock_moves) == 1)

        part_serial_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_serial
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_serial_back_stock_moves and len(part_serial_back_stock_moves) == 1)

    def test_consume_repair_order_01(self):
        """
        [Functional Test] - TC25

        - Case: Consume some parts of repair order in case repair order is under repair
        - Expected Result:
            + there are new stock moves, which generated to transfer consumed parts
            + reserved stock moves, which generated to reserve transfer repair line product from repair location to destination location
            when repair end will be updated (reduce product quantity by subtracting consumed quantity)
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()
        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # start repair order
        self.repair_with_supply.action_repair_start()
        # check reserved move of products which will be consumed later
        part_product_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_product)[0]
        part_lot_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_lot)[0]
        part_serial_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_serial)[0]
        part_product_reserved_stock_move = part_product_line.reserved_completion_stock_move_id
        part_lot_reserved_stock_move = part_lot_line.reserved_completion_stock_move_id
        part_serial_reserved_stock_move = part_serial_line.reserved_completion_stock_move_id
        self.assertTrue(float_compare(part_product_reserved_stock_move.product_uom_qty, 3.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_lot_reserved_stock_move.product_uom_qty, 2.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_serial_reserved_stock_move.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

        # simulate wizard to consume products
        with Form(self.env['wizard.repair.order.consumption'].with_context({
            'default_order_id': self.repair_with_supply.id
        })) as consumed_form:
            for idx in range(len(consumed_form.line_ids)):
                with consumed_form.line_ids.edit(idx) as line:
                    if line.product_id == self.product_part_product:
                        line.request_qty = 2.0
                    elif line.product_id == self.product_part_lot:
                        line.request_qty = 1.0
                    elif line.product_id == self.product_part_serial:
                        line.request_qty = 0.0
        wizard = consumed_form.save()
        wizard = wizard.with_context({'default_order_id': False})
        # consume products
        wizard.action_consume()

        related_moves = self.repair_with_supply.move_ids
        # check consumed moves
        part_product_consumed_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_product
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == part_product_line.location_dest_id
                                                                 and float_compare(m.product_uom_qty, 2.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        part_lot_consumed_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_lot
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == part_lot_line.location_dest_id
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_product_consumed_stock_moves and len(part_product_consumed_stock_moves) == 1)
        self.assertTrue(part_lot_consumed_stock_moves and len(part_lot_consumed_stock_moves) == 1)
        self.assertTrue(float_compare(part_product_reserved_stock_move.product_uom_qty, 1.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_lot_reserved_stock_move.product_uom_qty, 1.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_serial_reserved_stock_move.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

        # simulate wizard to consume products 2nd times
        with Form(self.env['wizard.repair.order.consumption'].with_context({
            'default_order_id': self.repair_with_supply.id
        })) as consumed_form:
            for idx in range(len(consumed_form.line_ids)):
                with consumed_form.line_ids.edit(idx) as line:
                    if line.product_id == self.product_part_product:
                        line.request_qty = 1.0
                    elif line.product_id == self.product_part_lot:
                        line.request_qty = 0.0
                    elif line.product_id == self.product_part_serial:
                        line.request_qty = 1.0
        wizard = consumed_form.save()
        wizard = wizard.with_context({'default_order_id': False})
        # consume products
        wizard.action_consume()

        related_moves = self.repair_with_supply.move_ids
        # check consumed moves
        part_product_consumed_stock_moves_2 = related_moves.filtered(lambda m: m.product_id == self.product_part_product
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == part_product_line.location_dest_id
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        part_serial_consumed_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_serial
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == part_lot_line.location_dest_id
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_product_consumed_stock_moves and len(part_product_consumed_stock_moves_2) == 1)
        self.assertTrue(part_lot_consumed_stock_moves and len(part_serial_consumed_stock_moves) == 1)
        self.assertTrue(part_product_reserved_stock_move.state == 'done')
        self.assertTrue(float_compare(part_product_reserved_stock_move.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

        self.assertTrue(part_lot_reserved_stock_move.state == 'assigned')
        self.assertTrue(float_compare(part_lot_reserved_stock_move.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

        self.assertTrue(part_serial_reserved_stock_move.state == 'done')
        self.assertTrue(float_compare(part_serial_reserved_stock_move.product_uom_qty, 1.0, precision_digits=self.precision) == 0)

    def test_consume_repair_order_02(self):
        """
        [Functional Test] - TC26

        - Case: Consume some parts of repair order in case repair order is under repair
            + consume more than original quantity of repair line
            + don't select option to update quantity of repair line
        - Expected Result:
            + reserved stock moves, which generated to reserve transfer repair line product from repair location to destination location
            when repair end will be done with quantity is updated based on consumed quantity and
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()
        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # start repair order
        self.repair_with_supply.action_repair_start()
        # check reserved move of products which will be consumed later
        part_product_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_product)[0]
        part_lot_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_lot)[0]
        part_product_reserved_stock_move = part_product_line.reserved_completion_stock_move_id
        part_lot_reserved_stock_move = part_lot_line.reserved_completion_stock_move_id
        self.assertTrue(float_compare(part_product_reserved_stock_move.product_uom_qty, 3.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_lot_reserved_stock_move.product_uom_qty, 2.0, precision_digits=self.precision) == 0)

        # increase quantity of product to consume them later
        self.env['stock.quant']._update_available_quantity(self.product_part_lot, self.repair_location, 1, lot_id=self.lot6)
        self.env['stock.quant']._update_available_quantity(self.product_part_product, self.repair_location, 1)
        # simulate wizard to consume products
        with Form(self.env['wizard.repair.order.consumption'].with_context({
            'default_order_id': self.repair_with_supply.id
        })) as consumed_form:
            for idx in range(len(consumed_form.line_ids)):
                with consumed_form.line_ids.edit(idx) as line:
                    if line.product_id == self.product_part_product:
                        line.request_qty = 4.0
                    elif line.product_id == self.product_part_lot:
                        line.request_qty = 3.0
                    elif line.product_id == self.product_part_serial:
                        line.request_qty = 0.0
        wizard = consumed_form.save()
        wizard = wizard.with_context({'default_order_id': False})
        # consume products
        wizard.action_consume()

        # check consumed moves
        self.assertTrue(part_product_reserved_stock_move.state == 'done')
        self.assertTrue(float_compare(part_product_reserved_stock_move.product_uom_qty, 4.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_product_line.product_uom_qty, 3.0, precision_digits=self.precision) == 0)

        self.assertTrue(part_lot_reserved_stock_move.state == 'done')
        self.assertTrue(float_compare(part_lot_reserved_stock_move.product_uom_qty, 3.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_lot_line.product_uom_qty, 2.0, precision_digits=self.precision) == 0)

    def test_consume_repair_order_03(self):
        """
        [Functional Test] - TC27

        - Case: Consume some parts of repair order in case repair order is under repair
            + consume more than original quantity of repair line
            + select option to update quantity of repair line
        - Expected Result:
            + reserved stock moves, which generated to reserve transfer repair line product from repair location to destination location
            when repair end will be done with quantity is updated based on consumed quantity and
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()
        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # start repair order
        self.repair_with_supply.action_repair_start()
        # check reserved move of products which will be consumed later
        part_product_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_product)[0]
        part_lot_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_lot)[0]
        part_product_reserved_stock_move = part_product_line.reserved_completion_stock_move_id
        part_lot_reserved_stock_move = part_lot_line.reserved_completion_stock_move_id
        self.assertTrue(float_compare(part_product_reserved_stock_move.product_uom_qty, 3.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_lot_reserved_stock_move.product_uom_qty, 2.0, precision_digits=self.precision) == 0)

        # increase quantity of product to consume them later
        self.env['stock.quant']._update_available_quantity(self.product_part_lot, self.repair_location, 1, lot_id=self.lot6)
        self.env['stock.quant']._update_available_quantity(self.product_part_product, self.repair_location, 1)
        # simulate wizard to consume products
        with Form(self.env['wizard.repair.order.consumption'].with_context({
            'default_order_id': self.repair_with_supply.id
        })) as consumed_form:
            for idx in range(len(consumed_form.line_ids)):
                with consumed_form.line_ids.edit(idx) as line:
                    if line.product_id == self.product_part_product:
                        line.request_qty = 4.0
                        line.should_update_quantity = True
                    elif line.product_id == self.product_part_lot:
                        line.request_qty = 3.0
                        line.should_update_quantity = True
                    elif line.product_id == self.product_part_serial:
                        line.request_qty = 0.0
        wizard = consumed_form.save()
        wizard = wizard.with_context({'default_order_id': False})
        # consume products
        wizard.action_consume()

        # check consumed moves
        self.assertTrue(part_product_reserved_stock_move.state == 'done')
        self.assertTrue(float_compare(part_product_reserved_stock_move.product_uom_qty, 4.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_product_line.product_uom_qty, 4.0, precision_digits=self.precision) == 0)

        self.assertTrue(part_lot_reserved_stock_move.state == 'done')
        self.assertTrue(float_compare(part_lot_reserved_stock_move.product_uom_qty, 3.0, precision_digits=self.precision) == 0)
        self.assertTrue(float_compare(part_lot_line.product_uom_qty, 3.0, precision_digits=self.precision) == 0)

    def test_consume_repair_order_04(self):
        """
        [Functional Test] - TC34

        - Case: Consume some parts of repair order in case repair order is under repair
            + consume more than 1 product uom quantity of product in repair line
        - Expected Result:
            + ValidationError occurs
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()
        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # start repair order
        self.repair_with_supply.action_repair_start()

        # simulate wizard to consume products
        with self.assertRaises(ValidationError):
            with Form(self.env['wizard.repair.order.consumption'].with_context({
                'default_order_id': self.repair_with_supply.id
            })) as consumed_form:
                for idx in range(len(consumed_form.line_ids)):
                    with consumed_form.line_ids.edit(idx) as line:
                        if line.product_id == self.product_part_product:
                            line.request_qty = 0.0
                        elif line.product_id == self.product_part_lot:
                            line.request_qty = 0.0
                        elif line.product_id == self.product_part_serial:
                            line.request_qty = 2.0

    def test_cancel_after_consuming_repair_order_01(self):
        """
        [Functional Test] - TC28

        - Case: Consume some parts of repair order in case repair order is under repair, than cancel repair order
        - Expected Result:
            + picking are kept as done
            + reserved stock move for product of repair order will be cancelled
            + there is stock move to transfer product of repair order back from repair location to source location
            + reserved stock moves, which generated to reserve transfer repair line product from repair location to destination location
            when repair end will be cancelled
            + there are new stock moves, which generated to transfer back remain part from repair location to current location (by subtracting consumed quantity)
            + consumed stock moves, which was done will be kept.
        """
        # confirm repair oder
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()
        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # start repair order
        self.repair_with_supply.action_repair_start()

        part_product_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_product)[0]
        part_lot_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_lot)[0]
        part_serial_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_serial)[0]
        part_product_reserved_stock_move = part_product_line.reserved_completion_stock_move_id
        part_lot_reserved_stock_move = part_lot_line.reserved_completion_stock_move_id
        part_serial_reserved_stock_move = part_serial_line.reserved_completion_stock_move_id
        # simulate wizard to consume product
        with Form(self.env['wizard.repair.order.consumption'].with_context({
            'default_order_id': self.repair_with_supply.id
        })) as consumed_form:
            for idx in range(len(consumed_form.line_ids)):
                with consumed_form.line_ids.edit(idx) as line:
                    if line.product_id == self.product_part_product:
                        line.request_qty = 2.0
                    elif line.product_id == self.product_part_lot:
                        line.request_qty = 1.0
                    elif line.product_id == self.product_part_serial:
                        line.request_qty = 0.0
        wizard = consumed_form.save()
        # consume products
        wizard = wizard.with_context({'default_order_id': False})
        wizard.action_consume()

        # cancel repair order
        self.repair_with_supply.action_repair_cancel()
        # check supply move of product in repair order
        self.assertTrue(self.repair_with_supply.state == 'cancel')
        # check picking
        self.assertTrue(len(self.repair_with_supply.picking_ids) == 1)
        picking = self.repair_with_supply.picking_ids[0]
        self.assertTrue(picking.state == 'done')
        # check reserved move of product in repair order
        self.assertTrue(self.repair_with_supply.reserved_completion_stock_move_id.state == 'cancel')
        # check reserved moves of products in repair lines
        self.assertTrue(part_product_reserved_stock_move.state == 'cancel')
        self.assertTrue(part_lot_reserved_stock_move.state == 'cancel')
        self.assertTrue(part_serial_reserved_stock_move.state == 'cancel')

        related_moves = self.repair_with_supply.move_ids
        # check consumed moves will be kept
        part_product_consumed_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_product
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == part_product_line.location_dest_id
                                                                 and float_compare(m.product_uom_qty, 2.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_product_consumed_stock_moves and len(part_product_consumed_stock_moves) == 1)

        part_lot_consumed_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_lot
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == part_lot_line.location_dest_id
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_lot_consumed_stock_moves and len(part_lot_consumed_stock_moves) == 1)
        # check return move of product in repair order
        repair_product_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_to_repair
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location_shelf1
                                                                 and float_compare(m.product_uom_qty, 2.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(repair_product_back_stock_moves and len(repair_product_back_stock_moves) == 1)
        # check return moves of remain products in repair lines
        part_product_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_product
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_product_back_stock_moves and len(part_product_back_stock_moves) == 1)

        part_lot_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_lot
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_lot_back_stock_moves and len(part_lot_back_stock_moves) == 1)

        part_serial_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_serial
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_serial_back_stock_moves and len(part_serial_back_stock_moves) == 1)

    def test_end_repair_order_01(self):
        """
        [Functional Test] - TC29

        - Case: End repair order, which consumed some parts, remain some parts, and there in remove product in repair lines
            + select option create consumption when confirmation opened
        - Expected Result:
            + reserved stock moves will be done
            + there are new stock moves to transfer remove product from repair location to destination location
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()
        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # start repair order
        self.repair_with_supply.action_repair_start()

        part_product_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_product)[0]
        part_lot_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_lot)[0]
        part_serial_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_serial)[0]
        part_remove_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_remove)[0]
        part_product_reserved_stock_move = part_product_line.reserved_completion_stock_move_id
        part_lot_reserved_stock_move = part_lot_line.reserved_completion_stock_move_id
        part_serial_reserved_stock_move = part_serial_line.reserved_completion_stock_move_id
        # simulate wizard to consume products
        with Form(self.env['wizard.repair.order.consumption'].with_context({
            'default_order_id': self.repair_with_supply.id
        })) as consumed_form:
            for idx in range(len(consumed_form.line_ids)):
                with consumed_form.line_ids.edit(idx) as line:
                    if line.product_id == self.product_part_product:
                        line.request_qty = 2.0
                    elif line.product_id == self.product_part_lot:
                        line.request_qty = 1.0
                    elif line.product_id == self.product_part_serial:
                        line.request_qty = 0.0
        wizard = consumed_form.save()
        wizard = wizard.with_context({'default_order_id': False})
        # consume products
        wizard.action_consume()

        # end repair order
        result = self.repair_with_supply.with_context(check_consumption=True).action_repair_end()

        view = self.env.ref('to_repair_supply.wizard_repair_order_confirm_consumption_view_form')
        expected_result = {
            'name': 'Confirm Create Consumption',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.repair.order.confirm.consumption',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': result.get('res_id')
        }
        self.assertTrue(result == expected_result)
        f = Form(self.env['wizard.repair.order.confirm.consumption'].with_context({
            'default_repair_id': self.repair_with_supply.id
        }))
        wizard = f.save()
        wizard.process_with_consumption()

        # check reserved moves
        self.assertTrue(self.repair_with_supply.reserved_completion_stock_move_id.state == 'done')
        self.assertTrue(part_product_reserved_stock_move.state == 'done')
        self.assertTrue(part_lot_reserved_stock_move.state == 'done')
        self.assertTrue(part_serial_reserved_stock_move.state == 'done')

        related_moves = self.repair_with_supply.move_ids
        # check completion move of product in repair line, which type is remove
        part_remove_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_remove
                                                                 and m.location_id == part_remove_line.location_id
                                                                 and m.location_dest_id == part_remove_line.location_dest_id
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_remove_stock_moves and len(part_remove_stock_moves) == 1)

    def test_end_repair_order_02(self):
        """
        [Functional Test] - TC30

        - Case: End repair order, which consumed some parts, remain some parts, and there in remove product in repair lines
            + select option don't create consumption when confirmation opened
        - Expected Result:
            + reserved stock moves will be cancelled
            + there are new stock moves to transfer remove product from repair location to destination location
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()
        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # start repair order
        self.repair_with_supply.action_repair_start()

        part_product_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_product)[0]
        part_lot_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_lot)[0]
        part_serial_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_serial)[0]
        part_remove_line = self.repair_with_supply.operations.filtered(lambda op: op.product_id == self.product_part_remove)[0]
        part_product_reserved_stock_move = part_product_line.reserved_completion_stock_move_id
        part_lot_reserved_stock_move = part_lot_line.reserved_completion_stock_move_id
        part_serial_reserved_stock_move = part_serial_line.reserved_completion_stock_move_id
        # simulate wizard to consume products
        with Form(self.env['wizard.repair.order.consumption'].with_context({
            'default_order_id': self.repair_with_supply.id
        })) as consumed_form:
            for idx in range(len(consumed_form.line_ids)):
                with consumed_form.line_ids.edit(idx) as line:
                    if line.product_id == self.product_part_product:
                        line.request_qty = 2.0
                    elif line.product_id == self.product_part_lot:
                        line.request_qty = 1.0
                    elif line.product_id == self.product_part_serial:
                        line.request_qty = 0.0
        wizard = consumed_form.save()
        wizard = wizard.with_context({'default_order_id': False})
        # consume products
        wizard.action_consume()

        # end repair order
        result = self.repair_with_supply.with_context(check_consumption=True).action_repair_end()

        view = self.env.ref('to_repair_supply.wizard_repair_order_confirm_consumption_view_form')
        expected_result = {
            'name': 'Confirm Create Consumption',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.repair.order.confirm.consumption',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': result.get('res_id')
        }
        self.assertTrue(result == expected_result)
        # simulate wizard
        f = Form(self.env['wizard.repair.order.confirm.consumption'].with_context({
            'default_repair_id': self.repair_with_supply.id
        }))
        wizard = f.save()
        wizard.process_without_consumption()

        # check reserved moves
        self.assertTrue(self.repair_with_supply.reserved_completion_stock_move_id.state == 'done')
        self.assertTrue(part_product_reserved_stock_move.state == 'cancel')
        self.assertTrue(part_lot_reserved_stock_move.state == 'cancel')
        self.assertTrue(part_serial_reserved_stock_move.state == 'cancel')

        related_moves = self.repair_with_supply.move_ids
        # check completion move of product in repair line, which type is remove
        part_remove_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_part_remove
                                                                 and m.location_id == part_remove_line.location_id
                                                                 and m.location_dest_id == part_remove_line.location_dest_id
                                                                 and float_compare(m.product_uom_qty, 1.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(part_remove_stock_moves and len(part_remove_stock_moves) == 1)

    def test_confirm_delivery_for_repair_order_01(self):
        """
        [Functional Test] - TC31

        - Case: Confirm delivery for repair order, which was not done repair
        - Expected Result:
            + ValidationError occurs
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()

        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # start repair order
        self.repair_with_supply.action_repair_start()
        # delivery repair oder before end repair
        with self.assertRaises(ValidationError):
            self.repair_with_supply.action_delivery_confirm()

    def test_confirm_delivery_for_repair_order_02(self):
        """
        [Functional Test] - TC32

        - Case: Confirm delivery for repair order, which was done repair
            + and there is a stock move to transfer repair product from source location to repair location when confirm repair order
        - Expected Result:
            + state of repair order change to delivered
            + there is a stock move, which generated to transfer repair product from repair location back to source location
        """
        # confirm repair order
        self.repair_with_supply.action_validate()
        # simulate wizard
        f = Form(self.env['stock.warn.insufficient.qty.repair'].with_context({
            'default_product_id': self.repair_with_supply.product_id.id,
            'default_location_id': self.repair_with_supply.location_id.id,
            'default_repair_id': self.repair_with_supply.id,
            'default_product_uom_name': self.repair_with_supply.product_id.uom_name
        }))
        # simulate select source location
        f.src_location_id = self.warehouse_location_shelf1

        wizard = f.save()
        # confirm on wizard
        wizard.action_done()
        # confirm picking
        picking = self.repair_with_supply.picking_ids[0]
        picking.action_confirm()
        picking.action_assign()

        stock_move_part_product = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_product)[0]
        stock_move_part_product.move_line_ids[0].qty_done = 3.0

        stock_move_part_lot = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_lot)[0]
        stock_move_part_lot.move_line_ids[0].qty_done = 2.0

        stock_move_part_serial = picking.move_lines.filtered(lambda m: m.product_id == self.product_part_serial)[0]
        stock_move_part_serial.move_line_ids[0].qty_done = 1.0

        picking._action_done()
        # start repair
        self.repair_with_supply.action_repair_start()
        # end repair
        self.repair_with_supply.action_repair_end()
        # delivery repair
        self.repair_with_supply.action_delivery_confirm()

        self.assertTrue(self.repair_with_supply.state == 'delivered')
        # check all related stock moves are done
        related_moves = self.repair_with_supply.move_ids
        self.assertTrue(set(related_moves.mapped('state')) == set(['done']))
        # check return move of product in repair order after confirm delivery
        repair_product_back_stock_moves = related_moves.filtered(lambda m: m.product_id == self.product_to_repair
                                                                 and m.location_id == self.repair_location
                                                                 and m.location_dest_id == self.warehouse_location_shelf1
                                                                 and float_compare(m.product_uom_qty, 2.0, precision_digits=self.precision) == 0
                                                                 and m.state == 'done')
        self.assertTrue(repair_product_back_stock_moves and len(repair_product_back_stock_moves) == 1)
