from odoo.tests import tagged
from odoo.exceptions import AccessError

from .common import TestCommon

@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestCommon):
    
    def test_access_right_repair_manager(self):
        """ 
        [Security Test] - TC01
        
        - Case: Test access rights of repair manager group on stock picking model
        - Expected Result: repair manager group has create/read/update permissions on stock picking model
        """
        picking = self.env['stock.picking'].with_user(self.repair_manager).create({
            'location_id': self.stock_location.id,
            'location_dest_id': self.stock_location.id,
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
        })

        picking.with_user(self.repair_manager).read(['id'])

        picking.with_user(self.repair_manager).write({'location_dest_id': self.warehouse_location.id})

        """ 
        [Security Test] - TC02
        
        - Case: Test access rights of repair manager group on stock picking model
        - Expected Result: repair manager group doesn't have delete permissions on stock picking model
        """
        with self.assertRaises(AccessError):
            picking.with_user(self.repair_manager).unlink()
            
        
        """ 
        [Security Test] - TC03
        
        - Case: Test access rights of repair manager group on stock scrap model
        - Expected Result: repair manager group has read permissions on stock scrap model
        """
        scrap = self.env['stock.scrap'].create({
            'product_id': self.product_part_product.id,
            'product_uom_id':self.uom_unit.id,
            'scrap_qty': 1,
        })
        scrap.with_user(self.repair_manager).read(['id'])
        
        """ 
        [Security Test] - TC04
        
        - Case: Test access rights of repair manager group on stock scrap model
        - Expected Result: repair manager group doesn't have create/update/delete permissions on stock scrap model
        """
        with self.assertRaises(AccessError):
            self.env['stock.scrap'].with_user(self.repair_manager).create({
                'product_id': self.product_part_product.id,
                'product_uom_id': self.uom_unit.id,
                'scrap_qty': 1,
            })
        
        with self.assertRaises(AccessError):
            scrap.with_user(self.repair_manager).write({'scrap_qty': 2})
            
        with self.assertRaises(AccessError):
            scrap.with_user(self.repair_manager).unlink()
