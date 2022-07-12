from odoo.tests import tagged
from odoo.tests.common import Form
from odoo.exceptions import ValidationError

from .common import Common


@tagged('post_install', '-at_install')
class TestProduct(Common):
    
    def test_01_onchange_product(self):
        product_form = Form(self.product)
        product_form.can_be_equipment = True
        product = product_form.save()

        self.assertEqual(product.type, 'product')
        self.assertEqual(product.tracking, 'serial')

    def test_01_constrains_product(self):
        # Create Can be Equipment is True
        self.assertTrue(self.product.can_be_equipment)
        self.assertEqual(self.product.type, 'product')  
        self.assertEqual(self.product.tracking, 'serial')

    def test_02_constrains_product(self):
        # Can be Equipment is True, Type not is product
        with self.assertRaises(ValidationError):
            self.product.write({'type': 'service'})
        
        with self.assertRaises(ValidationError):
            self.product.write({'type': 'consu'})
    
    def test_03_constrains_product(self):
        # Can be Equipment is True, tracking not is serial
        with self.assertRaises(ValidationError):
            self.product.write({'tracking': 'lot'})
        
        with self.assertRaises(ValidationError):
            self.product.write({'tracking': 'none'})
