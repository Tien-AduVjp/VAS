from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestVoucherProduct(TestCommon):
    
    def test_01_onchange_promotion_product(self):
        # Marked as promotional product
        self.assertEqual(self.voucher_product.is_promotion_voucher, True, "Not Is Voucher Product")
        self.assertEqual(self.voucher_product.type, 'product', "Type is not storable product")
        self.assertEqual(self.voucher_product.categ_id.id, self.product_category.id, "Product catalog is not promotion voucher")
        self.assertEqual(self.voucher_product.tracking, 'serial', "Product is not tracked by serial number")
        
    def test_02_onchange_promotion_product(self):
        # Not marked as promotional product
        self.voucher_product.write({'is_promotion_voucher': False})
        self.assertEqual(self.voucher_product.is_promotion_voucher, False, "Not is Voucher Product")
        
    def test_03_check_constrains_voucher_product(self):
        # Marked as promotional product, type is not storable product
        with self.assertRaises(ValidationError):
            self.voucher_product.write({'type': 'service'})
    
    def test_04_check_constrains_voucher_product(self):
        # Marked as promotional product, tracking is not serial
        with self.assertRaises(ValidationError):
            self.voucher_product.write({'tracking': 'lot'})
