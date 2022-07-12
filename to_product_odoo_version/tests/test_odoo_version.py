from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestOdooVersion(TestCommon):

    def test_odoo_version(self):
        '''Case 1: Two odoo versions assigned to a product attribute value
                Exceptation: Raise exception
        '''
        product_attribute_value = self.ProductAttributeValue.create(self.product_attribute_value_create_val)

        odoo_vesrions = self.odoo_v13 | self.odoo_v12
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                odoo_vesrions.write({'product_attribute_value_id': product_attribute_value.id})
                self.OdooVersion.flush()

        '''Case 2: Change the name of odoo version
                Expectation: The name of product attribute value must change accordingly
        '''
        odoo_version = self.env['odoo.version'].search([('name', '=', '0.0')])
        odoo_version.write({'name': '1.0'})
        self.assertEqual(odoo_version.product_attribute_value_id.name, odoo_version.name)

        '''Case 3: Unlink odoo version
                Expectation: Product attribute value must unlink accordingly
        '''
        odoo_version.unlink()
        product_attribute_value = self.env['odoo.version'].search([('name', '=', '1.0')])
        self.assertEqual(len(product_attribute_value), 0)

        '''Case 4: Create new odoo version, product attribute value not exists
                Exceptation: Product attribute value must create accordingly
        '''
        odoo_version = self.OdooVersion.create(self.odoo_version_create_val)
        self.assertEqual(odoo_version.product_attribute_value_id.name, self.odoo_version_create_val['name'])
