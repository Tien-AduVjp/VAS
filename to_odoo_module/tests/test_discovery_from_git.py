from odoo.tests import tagged
from odoo.addons.to_git.tests import common


@tagged('post_install', '-at_install')
class TestGitBranchDiscovery(common.TestGitCommon):

    def test_action_discover_odoo_module(self):
        self.public_repo.scan_for_branches()
        git_branch = self.env['git.branch'].search([('name', '=', '11.0'), ('repository_id', '=', self.public_repo.id)])
        git_branch.write({
                'generate_app_products': True,
            })
        git_branch.checkout()
        git_branch.action_discover_odoo_modules()
        self.assertAlmostEqual(first=git_branch.odoo_module_versions_count,
                               second=2, delta=5,
                               msg='Public branch 11.0 of Viindoo backend theme should have around 2 (0 to 7) modules')
        self.assertEqual(first=self.public_repo.app_product_templates_count,
                         second=self.public_repo.odoo_module_versions_count,
                         msg='After discovering, the number of odoo_module_version and product should be the same')
        for omv in git_branch.odoo_module_version_ids:
            product = omv.product_id
            self.assertEqual(first=product.default_code,
                             second=omv.technical_name,
                             msg="While discovering, odoo_module_version's technical_name should be equal to its product_product's default_code")
        git_branch.un_checkout()
