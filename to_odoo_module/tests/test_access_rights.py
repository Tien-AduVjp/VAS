from . import test_common
from .test_common import odoo_module_new_user

from odoo.exceptions import AccessError
from odoo.tests import tagged


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(test_common.TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRights, cls).setUpClass()

        cls.odoo_module = cls.env['odoo.module']
        cls.odoo_module_version = cls.env['odoo.module.version']
        cls.odoo_module_version_download_stat = cls.env['odoo.module.version.download.stat']
        cls.ir_module_category = cls.env['ir.module.category']

    def test_access_rights_portal(self):
        portal = odoo_module_new_user(self.env, login='test_portal', groups='base.group_portal')

        # Test permission with model odoo.module
        odoo_module_with_portal = self.odoo_module.create(self.odoo_module_create_val).with_user(portal)
        self.assertEqual(odoo_module_with_portal.technical_name, 'odoo_module')
        with self.assertRaises(AccessError):
            odoo_module_with_portal.read()
        with self.assertRaises(AccessError):
            odoo_module_with_portal.unlink()
        with self.assertRaises(AccessError):
            odoo_module_with_portal.write({'name': 'Odoo Module'})
        with self.assertRaises(AccessError):
            self.odoo_module.with_user(portal).create(self.odoo_module_create_val)

    def test_access_rights_internal_user(self):
        internal_user = odoo_module_new_user(self.env, login='test_internal_user', groups='base.group_user')

        # Test permission with model ir.module.category
        module_category_hidden_with_internal_user = self.env.ref('base.module_category_hidden').with_user(internal_user)
        self.assertEqual(module_category_hidden_with_internal_user.name, 'Technical')
        with self.assertRaises(AccessError):
            module_category_hidden_with_internal_user.unlink()
        with self.assertRaises(AccessError):
            module_category_hidden_with_internal_user.write({'name': 'TS'})
        with self.assertRaises(AccessError):
            self.ir_module_category.with_user(internal_user).create(self.ir_module_category_create_val)

        # Test permission with model odoo.module
        odoo_module_with_internal_user = self.odoo_module.create(self.odoo_module_create_val).with_user(internal_user)
        self.assertEqual(odoo_module_with_internal_user.technical_name, 'odoo_module')
        with self.assertRaises(AccessError):
            odoo_module_with_internal_user.unlink()
        with self.assertRaises(AccessError):
            odoo_module_with_internal_user.write({'name': 'Odoo Module'})
        with self.assertRaises(AccessError):
            self.odoo_module.with_user(internal_user).create(self.odoo_module_create_val)

        # Test permission with model odoo.module.version
        odoo_module_version_with_internal_user = self.odoo_module_version.create(self.odoo_module_version_create_val).with_user(internal_user)
        self.assertEqual(odoo_module_version_with_internal_user.technical_name, 'odoo_module_version')
        with self.assertRaises(AccessError):
            odoo_module_version_with_internal_user.unlink()
        with self.assertRaises(AccessError):
            odoo_module_version_with_internal_user.write({'name': 'OMV'})
        with self.assertRaises(AccessError):
            self.odoo_module_version.with_user(internal_user).create(self.odoo_module_version_create_val)

    def test_access_rights_user(self):
        user = odoo_module_new_user(self.env, login='test_user', groups='to_odoo_module.odoo_module_user')

        # Test permission with model odoo.module.version.download.stat
        self.odoo_module_version_download_stat_create_val.update({
            'user_id': user.id
        })
        odoo_module_version_download_stat = self.odoo_module_version_download_stat.with_user(user) \
            .create(self.odoo_module_version_download_stat_create_val)
        self.assertEqual(odoo_module_version_download_stat.odoo_module_version_id, self.test_omv_test)
        with self.assertRaises(AccessError):
            odoo_module_version_download_stat.write({'odoo_module_version_id': self.test_omv_test_sale.id})
        with self.assertRaises(AccessError):
            odoo_module_version_download_stat.unlink()
