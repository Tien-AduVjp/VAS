from odoo.tests.common import Form, tagged
from odoo.exceptions import ValidationError

from .test_stock_product_allocation_common import TestStockProductAllocationCommon


@tagged('post_install', '-at_install')
class TestStockAllocationRequest(TestStockProductAllocationCommon):
    
    # ============================Form Test==========================
    def test_01_method_default_value(self):
        allocation_request_form = Form(self.env['stock.allocation.request'])
        # Check default get
        self.assertTrue(allocation_request_form.warehouse_id, "The field source warehouse does not set the default value")
        self.assertTrue(allocation_request_form.scheduled_date, "The field scheduled date does not set the default value")
        self.assertTrue(allocation_request_form.responsible_id, "The field approval user does not set the default value")
        
        allocation_request_form.save()
        
    # =======================Test Functional==========================
    # Case 1
    def test_11_constraints(self):
        # Check Source and Destination Warehouse cannot be the same
        # Update stock product allocation
        with self.assertRaises(ValidationError):
            self.allocation_request_1.line_ids.write({'warehouse_id': self.warehouse_1.id})
        
        # Create stock product allocation
        with self.assertRaises(ValidationError):
            # Prepare the dict of values to stock allocaton request line
            val_1 = {
                'product_id':  self.product_2.id,
                'quantity': 5,
                'warehouse_id': self.warehouse_1.id,
                'uom_id': self.product_2.uom_id.id
                }
            
            val_2 = {
                'product_id':  self.product_2.id,
                'quantity': 6,
                'warehouse_id': self.warehouse_1.id,
                'uom_id': self.product_2.uom_id.id
                }
            
            self.env['stock.allocation.request'].create({
            'warehouse_id': self.warehouse_1.id,
            'line_ids': [(0, 0, val_1), (0, 0, val_2)]
            })
    # Case 3
    def test_12_create_stock_allocation_request(self):
        self.assertTrue(self.allocation_request_1, "Create stock product allocation, not success")
        
    def test_13_method_action_confirm(self):
        self.allocation_request_1.with_user(self.user_stock_manager).action_confirm()
        
        # Check to create pickings when confirming stock allocation request
        self.assertTrue(self.allocation_request_1.picking_ids, "Confirm stock product allocation, not success") 
        
        # Check pickings count link stock product allocation
        self.assertEqual(self.allocation_request_1.pickings_count, 3, "The number of pickings incorrect")
        
        # Check product, quantity on pickings mapped with stock allocation request
        move_lines = self.allocation_request_1.picking_ids.mapped('move_lines')
        move_line = move_lines.filtered(lambda r: r.product_id.id == self.product_2.id)[:1]
        
        # Compare value allocation request with picking
        self.assertRecordValues(move_line, [
            {'product_id': self.product_2.id, 'product_qty': 10, 'product_uom': self.product_2.uom_id.id}
            ])
    
    # Case 4
    def test_14_method_check_done(self):
        # Set quantity of allocation request line to 0.0
        self.allocation_request_2.line_ids.write({'quantity': 0.0})
        
        # Check test raise 'You must have at least one non-zero quantity line to submit for approval'
        with self.assertRaises(ValidationError):
            self.allocation_request_2.with_user(self.user_stock_manager).action_confirm()
    
    # Case 5
    def test_15_method_action_done(self):
        self.allocation_request_1.with_user(self.user_stock_manager).action_confirm()
        # Get pickings link allocation request
        picking_ids = self.allocation_request_1.picking_ids
        # Validate picking step 1
        pickings_confirm_1 = picking_ids.filtered(lambda r: r.state == 'confirmed')
        moves = pickings_confirm_1.move_lines
        for move in moves:
            move.write({'quantity_done': move.product_uom_qty})
        for pick in pickings_confirm_1:
            pick.button_validate()
        
        # Test click button Mark as Done to fail
        with self.assertRaises(ValidationError):
            self.allocation_request_1.with_user(self.user_stock_manager).action_done()
            
        # Validate picking step 2
        pickings_confirm_2 = self.allocation_request_1.picking_ids.filtered(lambda r: r.state == 'assigned')
        moves = pickings_confirm_2.move_lines
        for move in moves:
            move.write({'quantity_done': move.product_uom_qty})
            
        for pick in pickings_confirm_2:
            pick.button_validate()
        self.assertTrue(self.allocation_request_1.state == 'done', "The Test click button mark as done to fail")
