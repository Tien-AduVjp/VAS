from odoo.tests import tagged, Form

from odoo.addons.to_odoo_module.tests import test_common


@tagged('post_install', '-at_install')
class TestCart(test_common.TestCommon):
    @classmethod
    def setUpClass(cls):
        super(TestCart, cls).setUpClass()

        cls.odoo_version_14 = cls.env.ref('to_odoo_version.odoo_v14')
        cls.test_git_branch_14 = cls.env['git.branch'].create({
            'name': '14.0',
            'repository_id': cls.test_git_repo.id,
            'odoo_version_id': cls.odoo_version_14.id,
            'generate_app_products': True,
        })

        cls.odoo_module_version_c = cls.env['odoo.module.version'].create({
            'name': 'Odoo Module Version C',
            'technical_name': 'omv_c',
            'odoo_version_id': cls.odoo_version_14.id,
            'git_branch_id': cls.test_git_branch_14.id,
            'price': 1.0,
            'license_version_id': cls.product_license_version.id,
            'version': '0.1',
            'depends': '',
        })

        cls.odoo_module_version_d = cls.env['odoo.module.version'].create({
            'name': 'Odoo Module Version D',
            'technical_name': 'omv_d',
            'odoo_version_id': cls.odoo_version_14.id,
            'git_branch_id': cls.test_git_branch_14.id,
            'price': 1.0,
            'license_version_id': cls.product_license_version.id,
            'version': '0.1',
            'depends': '',
        })

        cls.odoo_module_version_f = cls.env['odoo.module.version'].create({
            'name': 'Odoo Module Version F',
            'technical_name': 'omv_f',
            'odoo_version_id': cls.odoo_version_14.id,
            'git_branch_id': cls.test_git_branch_14.id,
            'price': 1.0,
            'license_version_id': cls.product_license_version.id,
            'version': '0.1',
            'depends': ''
        })

        cls.odoo_module_version_b = cls.env['odoo.module.version'].create({
            'name': 'Odoo Module Version B',
            'technical_name': 'omv_b',
            'odoo_version_id': cls.odoo_version_14.id,
            'git_branch_id': cls.test_git_branch_14.id,
            'price': 1.0,
            'license_version_id': cls.product_license_version.id,
            'version': '0.1',
            'depends': 'omv_c',
        })

        cls.odoo_module_version_a = cls.env['odoo.module.version'].create({
            'name': 'Odoo Module Version A',
            'technical_name': 'omv_a',
            'odoo_version_id': cls.odoo_version_14.id,
            'git_branch_id': cls.test_git_branch_14.id,
            'price': 1.0,
            'license_version_id': cls.product_license_version.id,
            'version': '0.1',
            'depends': 'omv_d,omv_b',
        })

        cls.odoo_module_version_e = cls.env['odoo.module.version'].create({
            'name': 'Odoo Module Version E',
            'technical_name': 'omv_e',
            'odoo_version_id': cls.odoo_version_14.id,
            'git_branch_id': cls.test_git_branch_14.id,
            'price': 1.0,
            'license_version_id': cls.product_license_version.id,
            'version': '0.1',
            'depends': 'omv_f,omv_c',
        })

    def test_cart_1(self):
        so_form = Form(self.env['sale.order'])
        so_form.partner_id = self.partner

        # Case 1: Add items to cart
        # Expect: Auto load app dependencies

        # Add A to cart
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.odoo_module_version_a.product_id
        so = so_form.save()
        omv_name_list = so.order_line.odoo_module_version_id.mapped('technical_name')
        omv_name_list = sorted(omv_name_list)
        self.assertEqual(omv_name_list, ['omv_a', 'omv_b', 'omv_c', 'omv_d'])

        # Case 2: Remove items from cart

        # If you delete an app that has another app that depends on it, that app will automatically be re-added.
        # Remove b failed
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_b)
        self.assertEqual(omv_name_list, ['omv_a', 'omv_b', 'omv_c', 'omv_d'])

        # Remove c failed
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_c)
        self.assertEqual(omv_name_list, ['omv_a', 'omv_b', 'omv_c', 'omv_d'])

        # Remove d failed
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_d)
        self.assertEqual(omv_name_list, ['omv_a', 'omv_b', 'omv_c', 'omv_d'])

        apps_dependency, apps_not_dependency = self.get_app_dependency_or_not_from_so(so)
        self.assertEqual(apps_not_dependency, ['omv_a'])
        self.assertEqual(apps_dependency, ['omv_b', 'omv_c', 'omv_d'])

        # If you delete an app that has no dependencies on it, that app will be deleted.
        # Remove a successfully
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_a)
        self.assertEqual(omv_name_list, ['omv_b', 'omv_c', 'omv_d'])

        apps_dependency, apps_not_dependency = self.get_app_dependency_or_not_from_so(so)
        self.assertEqual(apps_not_dependency, ['omv_b', 'omv_d'])
        self.assertEqual(apps_dependency, ['omv_c'])

        # Remove d successfully, because it not dependency
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_d)
        self.assertEqual(omv_name_list, ['omv_b', 'omv_c'])

        apps_dependency, apps_not_dependency = self.get_app_dependency_or_not_from_so(so)
        self.assertEqual(apps_not_dependency, ['omv_b'])
        self.assertEqual(apps_dependency, ['omv_c'])

        # Remove c failed, because b depends on it
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_c)
        self.assertEqual(omv_name_list, ['omv_b', 'omv_c'])

        # Remove b successfully, because it not dependency
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_b)
        self.assertEqual(omv_name_list, ['omv_c'])

        # Remove c successfully, because it not dependency
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_c)
        self.assertEqual(omv_name_list, [])

    def test_cart_2(self):
        so_form = Form(self.env['sale.order'])
        so_form.partner_id = self.partner

        # Case 1: Add items to cart
        # Expect: Auto load app dependencies

        # Add A to cart
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.odoo_module_version_a.product_id
        so = so_form.save()
        omv_name_list = so.order_line.odoo_module_version_id.mapped('technical_name')
        omv_name_list = sorted(omv_name_list)
        self.assertEqual(omv_name_list, ['omv_a', 'omv_b', 'omv_c', 'omv_d'])

        # Add E to cart
        with so_form.order_line.new() as line_form:
            line_form.product_id = self.odoo_module_version_e.product_id
        so = so_form.save()
        omv_name_list = so.order_line.odoo_module_version_id.mapped('technical_name')
        omv_name_list = sorted(omv_name_list)
        self.assertEqual(omv_name_list, ['omv_a', 'omv_b', 'omv_c', 'omv_d', 'omv_e', 'omv_f'])

        apps_dependency, apps_not_dependency = self.get_app_dependency_or_not_from_so(so)
        self.assertEqual(apps_not_dependency, ['omv_a', 'omv_e'])
        self.assertEqual(apps_dependency, ['omv_b', 'omv_c', 'omv_d', 'omv_f'])

        # Case 2: Remove items from cart

        # If you delete an app that has no dependencies on it, that app will be deleted.
        # Remove a successfully
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_a)
        self.assertEqual(omv_name_list, ['omv_b', 'omv_c', 'omv_d', 'omv_e', 'omv_f'])

        apps_dependency, apps_not_dependency = self.get_app_dependency_or_not_from_so(so)
        self.assertEqual(apps_not_dependency, ['omv_b', 'omv_d', 'omv_e'])
        self.assertEqual(apps_dependency, ['omv_c', 'omv_f'])

        # Remove b successfully
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_b)
        self.assertEqual(omv_name_list, ['omv_c', 'omv_d', 'omv_e', 'omv_f'])

        apps_dependency, apps_not_dependency = self.get_app_dependency_or_not_from_so(so)
        self.assertEqual(apps_not_dependency, ['omv_d', 'omv_e'])
        self.assertEqual(apps_dependency, ['omv_c', 'omv_f'])

        # Remove d successfully
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_d)
        self.assertEqual(omv_name_list, ['omv_c', 'omv_e', 'omv_f'])

        # If you delete an app that has another app that depends on it, that app will automatically be re-added.
        # Remove c failed
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_c)
        self.assertEqual(omv_name_list, ['omv_c', 'omv_e', 'omv_f'])

        # Remove f failed
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_f)
        self.assertEqual(omv_name_list, ['omv_c', 'omv_e', 'omv_f'])

        # Remove e successfully
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_e)
        self.assertEqual(omv_name_list, ['omv_c', 'omv_f'])

        apps_dependency, apps_not_dependency = self.get_app_dependency_or_not_from_so(so)
        self.assertEqual(apps_not_dependency, ['omv_c', 'omv_f'])
        self.assertEqual(apps_dependency, [])

        # Remove c successfully
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_c)
        self.assertEqual(omv_name_list, ['omv_f'])

        # Remove f successfully
        omv_name_list = self.remove_line_from_so_and_return_omv(so_form, self.odoo_module_version_f)
        self.assertEqual(omv_name_list, [])

    @staticmethod
    def indices(_list, _filter=lambda x: bool(x)):
        """
        Get list index of value from list.
        """
        return [i for i, x in enumerate(_list) if _filter(x)]

    @staticmethod
    def get_app_dependency_or_not_from_so(so):
        # Check app not dependency
        lines_not_dependency = so.order_line.filtered(lambda line: line.odoo_app_dependency is False)
        omv_name_list = lines_not_dependency.odoo_module_version_id.mapped('technical_name')
        apps_not_dependency = sorted(omv_name_list)

        # Check app dependency
        lines_dependency = so.order_line - lines_not_dependency
        omv_name_list = lines_dependency.odoo_module_version_id.mapped('technical_name')
        apps_dependency = sorted(omv_name_list)

        return apps_dependency, apps_not_dependency

    def remove_line_from_so_and_return_omv(self, so_form, odoo_module_version):
        """
        Remove sale.order.line from sale.order by odoo module version, and return list of odoo.module.version's name in so.
        """
        line_index = self.indices(so_form.order_line._records, lambda line: line['name'] == odoo_module_version.product_id.display_name)[0]
        so_form.order_line.remove(line_index)
        so = so_form.save()
        omv_name_list = so.order_line.odoo_module_version_id.mapped('technical_name')
        omv_name_list = sorted(omv_name_list)
        return omv_name_list
