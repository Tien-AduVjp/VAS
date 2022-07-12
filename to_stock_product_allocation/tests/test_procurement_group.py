from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_stock_product_allocation_common import TestStockProductAllocationCommon


@tagged('post_install', '-at_install')
class TestProcurementRequest(TestStockProductAllocationCommon):
    
    # ==========================Test Functional=================================
    # Case 2:
    def test_11_constraints(self):
        self.allocation_request_1.with_user(self.user_stock_manager).action_confirm()
        self.allocation_request_2.with_user(self.user_stock_manager).action_confirm()
        
        procurement_group_id = self.allocation_request_2.procurement_group_ids[:1]
        # Check constraints
        with self.assertRaises(ValidationError):
            allocation_request_lines = self.allocation_request_1.line_ids
            allocation_request_lines.write({'procurement_group_id': procurement_group_id.id})
            procurement_group_id._check_allocation_request_lines()
    
    def test_21_method_compute_allocation_request_id(self):
        self.allocation_request_2.with_user(self.user_stock_manager).action_confirm()
        # Test compute value for the field stock allocation request
        procurement_group_id = self.allocation_request_2.procurement_group_ids[:1]
        self.assertTrue(procurement_group_id.stock_allocation_request_id,
                        "The Method compute value for the field stock allocation request to fail")
