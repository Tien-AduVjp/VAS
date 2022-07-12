from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install')
class TestStockPicking(Common):   
       
    #Case 1
    def test_inventory_transfer_type_receipts(self):
        picking = self.create_inventory_transfer(self.product_storeable, self.picking_type_receipts)      
        self.assertGreater(len(picking.account_move_ids), 0)
        self.assertGreater(len(picking.account_move_line_ids), 0)
    
    #Case 2
    def test_inventory_transfer_type_internal(self):
        picking = self.create_inventory_transfer(self.product_storeable, self.picking_type_internal_transfers)      
        self.assertEqual(len(picking.account_move_ids), 0)
        self.assertEqual(len(picking.account_move_line_ids), 0)
