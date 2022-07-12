from datetime import date

from odoo.tests import SingleTransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCommon(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        cls.ProductAttributeValue = cls.env['product.attribute.value']
        cls.OdooVersion = cls.env['odoo.version']

        cls.odoo_v13 = cls.env.ref('to_odoo_version.odoo_v13')
        cls.odoo_v12 = cls.env.ref('to_odoo_version.odoo_v12')

        cls.product_attribute_odoo_version = cls.env.ref('to_product_odoo_version.product_attribute_odoo_version')
        cls.product_attribute_value_create_val = {
            'name': '0.0',
            'attribute_id': cls.product_attribute_odoo_version.id,
        }

        cls.odoo_version_create_val = {
            'name': '4.4',
            'release_date': date.today()
        }
