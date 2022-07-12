from odoo.exceptions import AccessError
from odoo.tests import new_test_user, tagged

from .config_section_common import ConfigSectionCommon


@tagged('access_rights')
class TestConfigSectionAccessRights(ConfigSectionCommon):

    def setUp(self):
        super(TestConfigSectionAccessRights, self).setUp()

    def test_01_access_rights__user(self):
        config_section = self.config_section.sudo().create(self.create_val)
        user = new_test_user(self.env, login='user', groups='base.group_user')

        self.assertEqual(config_section.name, self.create_val['name'])

        with self.assertRaises(AccessError):
            self.config_section.with_user(user).create(self.create_val)

        with self.assertRaises(AccessError):
            config_section.with_user(user).write({'name': 'CONFIG SECTION'})

        with self.assertRaises(AccessError):
            config_section.with_user(user).unlink()

    def test_11_access_rights__manager(self):
        val_change = {'name': 'CONFIG SECTION'}
        manager = new_test_user(self.env, login='manager', groups='base.group_user,to_config_management.group_manager')

        config_section = self.config_section.with_user(manager).create(self.create_val)
        config_section.with_user(manager).write(val_change)
        self.assertEqual(config_section.name, val_change['name'])
        self.assertTrue(config_section.with_user(manager).unlink(), 'Deleting a config section should be possible')
