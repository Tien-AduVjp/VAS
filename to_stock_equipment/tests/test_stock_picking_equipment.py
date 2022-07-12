from odoo.tests import tagged
from odoo.exceptions import UserError

from .common import Common


@tagged('post_install', '-at_install')
class TestStockEquipment(Common):

    def test_01_check_stock_picking_equipment(self):
        # Transfer has type receiving, marked as can create equipment on each line
        self.picking.button_validate()
        self.assertEqual(self.picking.state, 'done')
        self.assertTrue(all(self.picking.move_line_ids.mapped('can_create_equipment')))
        equipments = self.env['maintenance.equipment'].search([('id', 'in', self.picking.move_line_ids.equipment_id.ids)])
        self.assertEqual(len(equipments), len(self.picking.move_line_ids))

    def test_02_check_stock_picking_equipment(self):
        # Transfer has type receiving, not marked as can create equipment on each line
        self.move_line_1.write({'can_create_equipment': False})
        self.move_line_2.write({'can_create_equipment': False})
        self.picking.button_validate()
        self.assertEqual(self.picking.state, 'done')
        self.assertFalse(all(self.picking.move_line_ids.mapped('can_create_equipment')))
        equipments = self.env['maintenance.equipment'].search([('id', 'in', self.picking.move_line_ids.equipment_id.ids)])
        self.assertFalse(equipments)

    def test_03_check_stock_picking_equipment(self):
        # Transfer has type receiving, some lines are marked as can create equipment
        self.move_line_1.write({'can_create_equipment': False})
        self.picking.button_validate()
        self.assertEqual(self.picking.state, 'done')
        self.assertFalse(all(self.picking.move_line_ids.mapped('can_create_equipment')))
        equipments = self.env['maintenance.equipment'].search([('id', 'in', self.picking.move_line_ids.equipment_id.ids)])
        self.assertEqual(len(equipments), 1)

    def test_04_check_stock_picking_equipment(self):
        # Transfer has type receiving, marked as can create equipment on each line, Product not marked as can be equipment
        self.picking.button_validate()
        self.product.write({'can_be_equipment': False})
        self.assertEqual(self.picking.state, 'done')
        self.assertTrue(all(self.picking.move_line_ids.mapped('can_create_equipment')))
        equipments = self.env['maintenance.equipment'].search([('id', 'in', self.picking.move_line_ids.equipment_id.ids)])
        self.assertEqual(len(equipments), len(self.picking.move_line_ids))

    def test_05_check_stock_picking_equipment(self):
        # Operation Type not marked as Create New Lots/Serial Numbers
        self.picking_type_in.write({'use_create_lots': False})
        with self.assertRaises(UserError):
            self.picking.button_validate()

    def test_06_check_stock_picking_equipment(self):
        # Operation Type marked as Create New Lots/Serial Numbers, unmark Can create equipment
        self.picking_type_in.write({'can_create_equipment': False})
        with self.assertRaises(UserError):
            self.picking.button_validate()
