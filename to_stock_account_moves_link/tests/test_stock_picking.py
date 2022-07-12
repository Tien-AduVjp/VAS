from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestStockPicking(Common):

    #Case 1
    def test_inventory_transfer_type_receipts(self):
        picking = self._make_in_picking(self.product_storeable)
        self.assertGreater(len(picking.account_move_ids), 0)
        self.assertGreater(len(picking.account_move_line_ids), 0)

    #Case 2
    def test_inventory_transfer_type_internal(self):
        picking = self._make_internal_picking(self.product_storeable)
        self.assertEqual(len(picking.account_move_ids), 0)
        self.assertEqual(len(picking.account_move_line_ids), 0)

    #Case 3
    def test_delivery_picking(self):
        self._make_in_picking(self.product_storeable)
        picking = self._make_out_picking(self.product_storeable)
        self.assertGreater(len(picking.account_move_ids), 0)
        self.assertGreater(len(picking.account_move_line_ids), 0)
