from odoo.tests import new_test_user, SavepointCase, tagged
from functools import partial

odoo_module_new_user = partial(new_test_user, context={
    'mail_create_nolog': True,
    'mail_create_nosubscribe': True,
    'mail_notrack': True,
    'no_reset_password': True
})


@tagged('-at_install', 'post_install')
class TestCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        test_url = 'https://github.com/Viindoo/backend_theme.git'
        test_git_repo_name = 'backend_theme'
        cls.product_license_version = cls.env.ref('to_product_license.license_lgpl')
        cls.company = cls.env.company
        cls.currency = cls.company.currency_id
        cls.test_git_repo = cls.env['git.repository'].create({
                'remote_url': test_url,
                'name': test_git_repo_name,
                'company_id': cls.company.id,
            })
        cls.odoo_version_12 = cls.env.ref('to_odoo_version.odoo_v12')
        cls.test_git_branch_12 = cls.env['git.branch'].create({
                'name': '12.0',
                'repository_id': cls.test_git_repo.id,
                'odoo_version_id': cls.odoo_version_12.id,
                'generate_app_products': True,
            })
        cls.portal_user = odoo_module_new_user(cls.env, login='portal_user', groups='base.group_portal')
        cls.partner = cls.portal_user.partner_id
        cls.test_omv_test = cls.env['odoo.module.version'].create({
                'name': 'test',
                'technical_name': 'to_test',
                'odoo_version_id': cls.odoo_version_12.id,
                'git_branch_id': cls.test_git_branch_12.id,
                'price': 4.9,
                'currency_id': cls.currency.id,
                'license_version_id': cls.product_license_version.id,
                'version': '0.8',
            })
        cls.test_omv_test_sale = cls.env['odoo.module.version'].create({
                'name': 'test sale',
                'technical_name': 'to_test_sale',
                'odoo_version_id': cls.odoo_version_12.id,
                'git_branch_id': cls.test_git_branch_12.id,
                'price': 4.9,
                'currency_id': cls.currency.id,
                'license_version_id': cls.product_license_version.id,
                'version': '0.8',
                'depends': 'to_test,sale',
            })
        cls.test_omv_test_sale_project = cls.env['odoo.module.version'].create({
                'name': 'test sale project',
                'technical_name': 'to_test_sale_project',
                'odoo_version_id': cls.odoo_version_12.id,
                'git_branch_id': cls.test_git_branch_12.id,
                'price': 4.9,
                'currency_id': cls.currency.id,
                'license_version_id': cls.product_license_version.id,
                'version': '0.8',
                'depends': 'to_test_sale,sale_timesheet',
            })
        cls.test_omv_test_sale_template_12 = cls.env['odoo.module.version'].create({
                'name': 'test sale template',
                'technical_name': 'to_test_sale_template',
                'odoo_version_id': cls.odoo_version_12.id,
                'git_branch_id': cls.test_git_branch_12.id,
                'price': 4.9,
                'currency_id': cls.currency.id,
                'license_version_id': cls.product_license_version.id,
                'version': '0.8',
                'depends': 'to_test_sale,sale_management',
            })
        cls.odoo_version_13 = cls.env.ref('to_odoo_version.odoo_v13')
        cls.test_git_branch_13 = cls.env['git.branch'].create({
                'name': '13.0',
                'repository_id': cls.test_git_repo.id,
                'odoo_version_id': cls.odoo_version_13.id,
            })
        cls.test_omv_test_sale_template_13 = cls.env['odoo.module.version'].create({
                'name': 'test sale template',
                'technical_name': 'to_test_sale_template',
                'odoo_version_id': cls.odoo_version_13.id,
                'git_branch_id': cls.test_git_branch_13.id,
                'price': 4.9,
                'currency_id': cls.currency.id,
                'license_version_id': cls.product_license_version.id,
                'version': '0.8',
                'depends': 'sale_management',
            })
        cls.test_om = cls.env['odoo.module'].search([('technical_name', '=', 'to_test_sale_template')], limit=1)

    def setUp(self):
        super(TestCommon, self).setUp()

        self.ir_module_category_create_val = {
            'name': 'Ir Module Category'
        }
        self.odoo_module_create_val = {
            'technical_name': 'odoo_module'
        }
        self.odoo_module_version_create_val = {
            'name': 'Odoo Module Version',
            'technical_name': 'odoo_module_version',
            'odoo_version_id': self.odoo_version_13.id,
            'git_branch_id': self.test_git_branch_13.id,
            'currency_id': self.currency.id,
            'license_version_id': self.product_license_version.id,
            'version': '0.8'
        }
        self.odoo_module_version_download_stat_create_val = {
            'odoo_module_version_id': self.test_omv_test.id,
            'by_internal_user': False,
            'free_download': False
        }
