from .test_common import TestCommon

from psycopg2 import IntegrityError
from datetime import date

from odoo.tests import Form, tagged
from odoo.tools import mute_logger
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestOdooVersion(TestCommon):

    def setUp(self):
        super(TestOdooVersion, self).setUpClass()

        self.odoo_version_form = Form(self.env['odoo.version'])
        self.odoo_version_form.release_date = '2019-03-10'

    def test_odoo_version_duplicate_name(self):
        self.odoo_version_form.name = '13.0'
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                self.odoo_version_form.save()

    def test_odoo_version_wrong_name(self):
        self.odoo_version_form.name = '13'
        with self.assertRaises(ValidationError):
            self.odoo_version_form.save()

    def test_odoo_version_new(self):
        self.odoo_version_form.name = '0.0'
        odoo_version = self.odoo_version_form.save()
        self.assertEqual(odoo_version.end_of_functional_support, date(2022, 3, 10))
        self.assertEqual(odoo_version.end_of_life, date(2024, 3, 10))
