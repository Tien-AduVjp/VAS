from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestVersionConfig(TestCommon):

    def test_version_config(self):
        """ Case 1: Create two versions config with the same name
                Expectation: Raise exception
        """
        odoo_version_config_create_vals = [self.odoo_version_config_create_val for _ in range(2)]
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            with self.env.cr.savepoint():
                self.OdooVersionConfig.create(odoo_version_config_create_vals)

        """ Case 2: Create two versions config with the same odoo_version_id
                Expectation: Raise exception
        """
        odoo_version_config_create_vals[0]['name'] = 'Odoo Version Config 2'
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.OdooVersionConfig.create(odoo_version_config_create_vals)
