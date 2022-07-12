from odoo.tests import tagged
from odoo.exceptions import ValidationError, UserError

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestProdctAttributeValue(TestCommon):

    def test_product_attribute_value(self):
        '''Case 1: Create new product attribute value, odoo version not exists
                Exceptation: Odoo version must create accordingly
        '''
        pav_create_val = self.product_attribute_value_create_val.copy()
        pav_create_val.update({'name': '1.0'})
        product_attribute_value = self.ProductAttributeValue.create(pav_create_val)
        self.assertEqual(product_attribute_value.odoo_version_id.name, '1.0')

        '''Case 2: Change attribute_id of product attribute value when attribute_id is odoo version
                Expectation: Raise exception
        '''
        with self.assertRaises(UserError):
            product_attribute_value.write({'attribute_id': False})

        '''Case 3: Change the name of product attribute value
                Expectation: The name of odoo version must change accordingly
        '''
        product_attribute_value.write({'name': '2.0'})
        self.assertEqual(product_attribute_value.odoo_version_id.name, '2.0')

        '''Case 4: Unlink product attribute value
                Expectation: Odoo version must unlink accordingly
        '''
        product_attribute_value.unlink()
        odoo_version = self.env['odoo.version'].search([('name', '=', '2.0')])
        self.assertEqual(len(odoo_version), 0)

        '''Case 5: attribute_id is odoo version, change the name of product attribute value to malformed name
                Expectation: Raise exception
        '''
        pav_create_val.update({'name': '0'})
        with self.assertRaises(ValidationError):
            self.ProductAttributeValue.create(pav_create_val)
