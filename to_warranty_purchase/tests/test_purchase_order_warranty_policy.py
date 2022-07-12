from odoo.tests import tagged

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestPurchaseOrderWarrantyPolicy(TestBase):

    def test_confirm_purchase_order_01(self):
        """
        [Functional Test] - TC01
        """
        order_lines = self.po1.order_line
        for line in order_lines:
            self.assertTrue(line.warranty_policy_ids == line.product_id.warranty_policy_ids.filtered(lambda x: x.apply_to == 'purchase'))
