from . import test_common

from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestOdooModuleVersion(test_common.TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestOdooModuleVersion, cls).setUpClass()

        cls.odoo_module_version = cls.env['odoo.module.version']

    def test_get_recursive_dependencies(self):
        dependency_name = self.test_omv_test_sale_template_12.get_recursive_dependencies().mapped('technical_name')
        dependency_name.sort()
        self.assertEqual(first=dependency_name,
                         second=['to_test', 'to_test_sale'],
                         msg="Dependency Module Of Test Sale Template Should Be 'to_test' & 'to_test_sale'")

    def test_download_module_free(self):
        odoo_module_version = self.odoo_module_version.create(self.odoo_module_version_create_val)
        public_user = self.env.ref('base.public_user')
        self.assertEqual(odoo_module_version.with_context(partner=public_user.partner_id).can_download, False)

    def test_download_module_free_depend_module_with_fee(self):
        self.odoo_module_version.create({
            'name': 'Odoo Module Version With Fee',
            'technical_name': 'odoo_module_version_with_fee',
            'odoo_version_id': self.odoo_version_13.id,
            'git_branch_id': self.test_git_branch_13.id,
            'currency_id': self.currency.id,
            'license_version_id': self.product_license_version.id,
            'version': '0.8',
            'price_currency': 5.0
        })
        odoo_module_version_free_create_val = self.odoo_module_version_create_val.copy()
        odoo_module_version_free_create_val['depends'] = 'odoo_module_version_with_fee'
        odoo_module_version_free = self.odoo_module_version.create(odoo_module_version_free_create_val)
        self.assertEqual(odoo_module_version_free.with_context(partner=self.partner).can_download, False)
