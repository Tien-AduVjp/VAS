from odoo.tests import tagged
from odoo.exceptions import UserError

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestConfigSection(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestConfigSection, cls).setUpClass()

        cls.config_section_create_val = {
            'name': 'Config Section'
        }

    def test_write_config_section(self):
        """ Case 1: Change name's Config Section when the config version has been assigned with odoo version
                Expectation: Raise exception
        """
        self.config_section_create_val['odoo_version_config_ids'] = [(0, 0, self.odoo_version_config_create_val)]
        self.config_section = self.ConfigSection.create(self.config_section_create_val)

        with self.assertRaises(UserError):
            self.config_section.write({'name': 'Change Config Section Name'})
