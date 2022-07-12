from odoo.tests.common import Form, tagged
from odoo.exceptions import ValidationError

from .test_stock_product_allocation_common import TestStockProductAllocationCommon


@tagged('post_install', 'at_install')
class TestStockAllocationRequest(TestStockProductAllocationCommon):

    # ============================Form Test==========================
    def test_01_method_default_value(self):
        allocation_request_form = Form(self.env['approval.request'])
        # Check default get
        self.assertTrue(allocation_request_form.warehouse_id, "The field source warehouse does not set the default value")
        self.assertTrue(allocation_request_form.scheduled_date, "The field scheduled date does not set the default value")

    # =======================Test Functional==========================
    # Case 1
    def test_11_constraints(self):
        # Check Source and Destination Warehouse cannot be the same
        # Update stock product allocation
        with self.assertRaises(ValidationError):
            self.allocation_request_1.allocation_request_line_ids.write({'warehouse_id': self.warehouse_1.id})

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

            self.env['approval.request'].create({
            'warehouse_id': self.warehouse_1.id,
            'allocation_request_line_ids': [(0, 0, val_1), (0, 0, val_2)],
            'approval_type_id': self.stock_location_approval_type.id,
            'employee_id': self.env.ref('hr.employee_al').id,
            'currency_id': self.env.company.currency_id.id,
            })
    # Case 3
    def test_12_create_stock_allocation_request(self):
        self.assertTrue(self.allocation_request_1, "Create stock product allocation, not success")

    def test_13_method_action_confirm(self):
        self.allocation_request_1.action_confirm()
        self.allocation_request_1.with_context(force_approval=True).action_validate()

        # Check to create pickings when confirming stock allocation request
        self.assertTrue(self.allocation_request_1.pickings_id, "Approve stock product allocation, not success")

        # Check pickings count link stock product allocation
        self.assertEqual(self.allocation_request_1.picking_count, 3, "The number of pickings incorrect")

        # Check product, quantity on pickings mapped with stock allocation request
        move_lines = self.allocation_request_1.pickings_id.mapped('move_lines')
        move_line = move_lines.filtered(lambda r: r.product_id.id == self.product_2.id)[:1]

        # Compare value allocation request with picking
        self.assertRecordValues(move_line, [
            {'product_id': self.product_2.id, 'product_qty': 10, 'product_uom': self.product_2.uom_id.id}
            ])

    # Case 4
    def test_14_method_check_done(self):
        # Set quantity of allocation request line to 0.0
        self.allocation_request_2.allocation_request_line_ids.write({'quantity': 0.0})

        # Check test raise 'You must have at least one non-zero quantity line to submit for approval'
        with self.assertRaises(ValidationError):
            self.allocation_request_2.action_confirm()

    def test_15_method_action_done(self):
        self.allocation_request_1.action_confirm()
        self.allocation_request_1.with_context(force_approval=True).action_validate()

        # Validate picking OUT
        pickings_confirm_out = self.allocation_request_1.pickings_id.filtered(lambda r: r.state == 'assigned')
        moves = pickings_confirm_out.move_lines
        for move in moves:
            move.write({'quantity_done': move.product_uom_qty})

        for pick in pickings_confirm_out:
            pick.button_validate()

        # Validate picking IN
        pickings_confirm_in = self.allocation_request_1.pickings_id.filtered(lambda r: r.state == 'assigned')
        moves = pickings_confirm_in.move_lines
        for move in moves:
            move.write({'quantity_done': move.product_uom_qty})
        for pick in pickings_confirm_in:
            pick.button_validate()

        self.assertTrue(self.allocation_request_1.state == 'done')
