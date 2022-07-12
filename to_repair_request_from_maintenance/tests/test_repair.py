from odoo.tests import Form
from odoo.tests import tagged

from .test_common import TestCommon

@tagged('post_install', '-at_install')
class TestRepair(TestCommon):
    
    def test_onchange_maintenance_request_id_01(self):
        """
        [Form Test] - TC01
        - Case: Change maintenance request of repair order, in which equipment of maintenance request has lot and product data
        - Expected Result: 
            + lot of repair order will be set based on lot of equipment
            + product of repair order will be set based on product of equipment
            + partner of repair oder will be set based on customer on lot
        """
        
        with Form(self.env['repair.order']) as f:
            f.maintenance_request_id = self.maintenance_request1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product_to_repair1)
            self.assertTrue(f.partner_id == self.partner_a)
            f.maintenance_request_id = self.maintenance_request2
            self.assertTrue(f.lot_id == self.lot2)
            self.assertTrue(f.product_id == self.product_to_repair2)
            self.assertTrue(f.partner_id == self.partner_b)

    def test_onchange_maintenance_request_id_02(self):
        """
        [Form Test] - TC02
        - Case: Change maintenance request of repair order, in which equipment of maintenance request only has product data
        - Expected Result: 
            + lot of repair order will be reset
            + product of repair order will be set based on product of equipment
        """
        
        with Form(self.env['repair.order']) as f:
            f.maintenance_request_id = self.maintenance_request1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product_to_repair1)
            self.assertTrue(f.partner_id == self.partner_a)
            f.maintenance_request_id = self.maintenance_request3
            self.assertTrue(not f.lot_id)
            self.assertTrue(f.product_id == self.product_to_repair3)
            self.assertFalse(f.partner_id)
            # Because lot_id is required if selected product is tracking by lot/serial, so we need to select lot for this repair
            f.lot_id = self.lot3
            self.assertTrue(f.partner_id == self.partner_c)
            
    def test_onchange_maintenance_request_id_03(self):
        """
        [Form Test] - TC03
        - Case: Change maintenance request of repair order, in which maintenance request doesn't have equipment
        - Expected Result: 
            + lot of repair order will be reset
            + product of repair order will be kept as previous
        """
        
        with Form(self.env['repair.order']) as f:
            f.maintenance_request_id = self.maintenance_request1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product_to_repair1)
            self.assertTrue(f.partner_id == self.partner_a)
            f.maintenance_request_id = self.maintenance_request4
            self.assertTrue(not f.lot_id)
            self.assertTrue(f.product_id == self.product_to_repair1)
            self.assertFalse(f.partner_id)
            # Because lot_id is required if selected product is tracking by lot/serial, so we need to select lot for this repair
            f.lot_id = self.lot1
            self.assertTrue(f.partner_id == self.partner_a)
            
    def test_onchange_product_id_01(self):
        """
        [Form Test] - TC04
        - Case: Change product of repair order, in which new product is different from product of lot
        - Expected Result: 
            + lot of repair order will be reset
        """
        
        with Form(self.env['repair.order']) as f:
            f.maintenance_request_id = self.maintenance_request1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product_to_repair1)
            self.assertTrue(f.partner_id == self.partner_a)
            f.product_id = self.product_to_repair2
            self.assertTrue(not f.lot_id)
            self.assertFalse(f.partner_id)
            # Because lot_id is required if selected product is tracking by lot/serial, so we need to select lot for this repair
            f.lot_id = self.lot2
            self.assertTrue(f.partner_id == self.partner_b)
            
    def test_onchange_product_id_02(self):
        """
        [Form Test] - TC05
        - Case: Change product of repair order, in which new product is same from product of lot on equipment of maintenance request
        - Expected Result: 
            + lot of repair order will be set based on lot on maintenance request
            + partner of repair order will be set based on customer on lot
        """
        
        with Form(self.env['repair.order']) as f:
            f.maintenance_request_id = self.maintenance_request1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product_to_repair1)
            self.assertTrue(f.partner_id == self.partner_a)
            f.product_id = self.product_to_repair2
            self.assertTrue(not f.lot_id)
            self.assertFalse(f.partner_id)
            f.product_id = self.product_to_repair1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.partner_id == self.partner_a)
            
    def test_onchange_product_id_03(self):
        """
        [Form Test] - TC06
        - Case: Unselect product of repair order
        - Expected Result: 
            + lot, partner of repair order will be kept as previous
        """
        
        with Form(self.env['repair.order']) as f:
            f.maintenance_request_id = self.maintenance_request1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product_to_repair1)
            self.assertTrue(f.partner_id == self.partner_a)
            f.product_id = self.env['product.product']
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.partner_id == self.partner_a)
            f.product_id = self.product_to_repair1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.partner_id == self.partner_a)
