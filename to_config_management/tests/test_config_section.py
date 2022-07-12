import psycopg2
try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    UniqueViolation = psycopg2.IntegrityError

from odoo.tools import mute_logger

from .config_section_common import ConfigSectionCommon


class TestConfigSection(ConfigSectionCommon):

    def setUp(self):
        super(TestConfigSection, self).setUp()

    def test_name_unique(self):
        vals_list = [self.create_val for _ in range(2)]

        with self.assertRaises(UniqueViolation), mute_logger('odoo.sql_db'):
            self.config_section.create(vals_list)

    def test_name_description(self):
        create_val = self.create_val.copy()
        create_val.update({'description': self.create_val['name']})

        with self.assertRaises(psycopg2.IntegrityError), mute_logger('odoo.sql_db'):
            self.config_section.create(create_val)

