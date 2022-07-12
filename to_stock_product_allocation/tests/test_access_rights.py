from odoo.tests import tagged
from odoo.exceptions import AccessError

from .test_stock_product_allocation_common import TestStockProductAllocationCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestStockProductRequestAccessRights(TestStockProductAllocationCommon):
    
    def test_01_access_rights_with_stock_user(self):
        # Check access rights delete stock product allocation
        with self.assertRaises(AccessError):
            self.allocation_request_2.with_user(self.user_stock_user).unlink()
