from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase, Form, tagged
from odoo.tools.misc import mute_logger


@tagged('post_install', '-at_install')
class TestToProductLicense(SavepointCase):

    def setUp(self):
        super(TestToProductLicense, self).setUp()
        self.license1 = self.env['product.license'].create({
            'name': 'License 1 Test ABC',
            'short_name': 'ABC'
        })
        self.license2 = self.env['product.license'].create({
            'name': 'License 2 Test XYZ',
            'short_name': 'XYZ'
        })
        self.license_version_test = self.env['product.license.version'].create({
            'name': '2.0.0',
            'date_released': '2021-01-01',
            'license_id': self.license1.id
        })


    def test_name_license_id_unique(self):
        self.env['product.license.version'].create({
            'name': '1.0',
            'date_released': '2021-01-01',
            'license_id': self.license1.id
        })
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['product.license.version'].create({
                'name': '1.0',
                'date_released': '2021-01-01',
                'license_id': self.license1.id
            })

    def test_validate_version_string(self):
        with self.assertRaises(ValidationError):
            self.license_version_test.name = '1.'

        with self.assertRaises(ValidationError):
            self.license_version_test.name = '1.x'

        with self.assertRaises(ValidationError):
            self.license_version_test.name = 'x.x.x'

        with self.assertRaises(ValidationError):
            self.license_version_test.name = '1,1'

        with self.assertRaises(ValidationError):
            self.license_version_test.name = '1.0.0.0'

        with self.assertRaises(ValidationError):
            self.license_version_test.name = 'name test'

    def test_write(self):
        license_version_test = self.env['product.license.version'].create({
            'name': '1.1.1',
            'date_released': '2021-01-01',
            'license_id': self.license1.id
        })
        product1 = self.env['product.product'].create({
            'name': 'Produck 1',
            'product_license_version_ids': license_version_test
        })
        with self.assertRaises(ValidationError):
            license_version_test.license_id = self.license2

    def test_onchange_name(self):
        with Form(self.env['product.license']) as license_form:
            license_form.name = 'License ABC'
            self.assertEqual(license_form.short_name, 'LA')

            license_form.name = 'License 1 abc  X'
            self.assertEqual(license_form.short_name, 'L1aX')

    def test_compute_product_license_version_ids(self):
        product1 = self.env['product.product'].create({
            'name': 'product 1',
            'product_license_version_ids': self.license_version_test
        })

        product_tmpl = product1.product_tmpl_id
        self.assertEqual(product1.product_license_version_ids, product_tmpl.product_license_version_ids)

        self.env['product.product'].create({
            'name': 'product 2',
            'product_tmpl_id': product_tmpl.id
        })
        self.assertFalse(product_tmpl.product_license_version_ids)
