from odoo.tests import tagged, TransactionCase
from odoo.exceptions import ValidationError


@tagged('-at_install', 'post_install')
class TestConstrains(TransactionCase):
    
    def setUp(self):
        super(TestConstrains, self).setUp()
        self.product_1 = self.env['product.product'].with_context(tracking_disable=True).create({
            'name': 'Product 1',
            'default_code': 'UNIQUE'
        })
    
    def test_01_constrains(self):
        # Checking unique Product Default Code is False
        self.assertFalse(self.env.company.check_unique_product_default_code)
        # Create a product with an existing reference code
        product = self.env['product.product'].with_context(tracking_disable=True).create({
            'name': 'Product Test',
            'default_code': 'UNIQUE'
        })
    
    def test_02_constrains(self):
        # Checking unique Product Default Code is True, 
        self.env.company.check_unique_product_default_code = True
        # Create a product with an existing reference code
        with self.assertRaises(ValidationError):
            product = self.env['product.product'].with_context(tracking_disable=True).create({
                'name': 'Product Test',
                'default_code': 'UNIQUE'
            })
    
    def test_03_constrains(self):
        # Checking unique Product Default Code is True
        self.env.company.check_unique_product_default_code = True
        # Create a product that does not match an existing reference code
        product = self.env['product.product'].with_context(tracking_disable=True).create({
            'name': 'Product Test',
            'default_code': 'P01'
        })
    
    def test_04_constrains(self):
        # Checking unique Product Default Code is True
        self.env.company.check_unique_product_default_code = True
        # Edit the reference code to coincide with another product, 'DESK0006' is the reference code of a demo product
        with self.assertRaises(ValidationError):
            self.product_1.with_context(tracking_disable=True).write({'default_code': 'DESK0006'})
