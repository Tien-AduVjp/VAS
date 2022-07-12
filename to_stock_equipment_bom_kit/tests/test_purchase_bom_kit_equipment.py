from odoo.tests import tagged
from odoo.tests.common import TransactionCase, Form


@tagged('post_install', '-at_install')
class TestPurchaseBomKitEquipment(TransactionCase):
    
    def setUp(self):
        super(TestPurchaseBomKitEquipment, self).setUp()
        self.PurchaseOrder = self.env['purchase.order']
        self.Bom = self.env['mrp.bom']
        self.product_bom_kit = self.env['product.product'].create({
            'name': 'Product Bom Kit',
            'can_be_equipment': True,
            'type': 'product',
            'tracking': 'serial'
        })
        
        self.product_bom_part_1 = self.env['product.product'].create({
            'name': 'Product Bom Part 1',
            'can_be_equipment': True,
            'type': 'product',
            'tracking': 'serial'
        })
        
        self.product_bom_part_2 = self.env['product.product'].create({
            'name': 'Product Bom Part 2',
            'can_be_equipment': True,
            'type': 'product',
            'tracking': 'serial'
        })
        
        self.bom = self.Bom.create({
            'product_id': self.product_bom_kit.id,
            'product_tmpl_id': self.product_bom_kit.product_tmpl_id.id,
            'product_uom_id': self.product_bom_kit.uom_id.id,
            'product_qty': 1.0,
            'type': 'phantom',
            'sequence': 2,
            'bom_line_ids': [
                (0, 0, {'product_id': self.product_bom_part_1.id, 'product_qty': 1}),
                (0, 0, {'product_id': self.product_bom_part_2.id, 'product_qty': 1})
            ]})
        
        puchase_form = Form(self.PurchaseOrder)
        puchase_form.partner_id = self.env.ref('base.partner_admin')
        with puchase_form.order_line.new() as line:
            line.product_id = self.product_bom_kit
            line.product_qty = 1
        self.puchase_order = puchase_form.save()
    
    def get_picking_and_move_lines_purchase_confirm(self):
        self.puchase_order.button_confirm()
        pickings = self.puchase_order.picking_ids.filtered(lambda a: a.state == 'assigned')
        move_lines = pickings.move_line_ids.filtered(lambda l: l.product_id.tracking == 'serial' and l.product_id.type == 'product')
        sequence_number = 1
        for line in move_lines:
            line.write({'lot_name': f'bom{sequence_number}', 'can_create_equipment':True, 'qty_done':1})
            sequence_number += 1
        return pickings, move_lines
        
    def test_01_check_equipment_from_purchase_order(self):
        # Purchase Order, confirm the receipt marked as can create equipment
        pickings, move_lines = self.get_picking_and_move_lines_purchase_confirm()
        pickings.button_validate()
        self.assertEqual(len(move_lines.equipment_id), len(move_lines))
        self.assertTrue(move_lines.equipment_id.parent_id)
    
    def test_02_check_equipment_from_purchase_order(self):
        # Purchase Order, confirm the receipt marked as can create equipment, unmarked create equipment for parent product
        pickings, move_lines = self.get_picking_and_move_lines_purchase_confirm()
        pickings.product_set_line_ids.write({'can_create_equipment': False})
        pickings.button_validate()
        self.assertEqual(len(move_lines.equipment_id), len(move_lines))
        self.assertFalse(move_lines.equipment_id.parent_id)
    
    def test_03_check_equipment_from_purchase_order(self):
        # Purchase Order, BOM component products are not tracking serial, unmarked can be equipment
        self.product_bom_part_1.write({'can_be_equipment': False, 'tracking': 'none'})
        self.product_bom_part_2.write({'can_be_equipment': False, 'tracking': 'none'})
        self.puchase_order.button_confirm()
        pickings = self.puchase_order.picking_ids.filtered(lambda a: a.state == 'assigned')
        move_lines = pickings.move_line_ids
        move_lines.write({'can_create_equipment':True, 'qty_done':1})
        pickings.button_validate()
        self.assertNotEqual(len(move_lines.equipment_id), len(move_lines))
