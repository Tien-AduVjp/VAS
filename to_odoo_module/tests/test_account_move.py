from . import test_common

from odoo.tests import tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestAccountMove(test_common.TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestAccountMove, cls).setUpClass()
        cls.company.chart_template_id = cls.env['account.chart.template'].search([], limit=1)
        if not cls.company.chart_template_id:
            # follow https://github.com/odoo/odoo/blob/1d4460bcc80e31e9198b19502951d68b447a136a/addons/account/tests/account_test_savepoint.py#L36
            # skip account move test when there is no default chart of account
            # chart of account holds lots of things: account journal, income account for product category
            cls.tearDownClass()
            cls.skipTest(cls, "Accounting Tests skipped because the user's company has no chart of accounts.")
        cls.account_move = cls.env['account.move']
        cls.account_payment_method_manual_in = cls.env.ref('account.account_payment_method_manual_in')
        cls.product_category_apps = cls.env.ref('to_odoo_module.product_category_odoo_apps')
        cls.account_income = cls.product_category_apps.property_account_income_categ_id

    @classmethod
    def create_account_move(cls, buy_omvs=None, paid_omvs=None):
        paid_omvs = paid_omvs or []
        buy_omvs = buy_omvs or []
        if paid_omvs:
            lines_to_create = []
            for test_omv in paid_omvs:
                account_move_line = {
                        'product_id': test_omv.product_id.id,
                        'name': test_omv.product_id.name,
                        'price_unit': test_omv.product_id.price,
                        'account_id': cls.account_income
                    }
                lines_to_create.append((0, 0, account_move_line))
            paid_ai = cls.account_move.create({
                    'move_type': 'out_invoice',
                    'partner_id': cls.partner.id,
                    'invoice_line_ids': lines_to_create,
                    'journal_id': cls.account_move.with_context(default_move_type='out_invoice')._get_default_journal().id,
                })
            paid_ai.action_post()
        lines_to_create = []
        for test_omv in buy_omvs:
            account_move_line = {
                    'product_id': test_omv.product_id.id,
                    'name': test_omv.product_id.name,
                    'price_unit': test_omv.product_id.price,
                    'account_id': cls.account_income
                }
            lines_to_create.append((0, 0, account_move_line))
        test_account_move = cls.account_move.create({
                'move_type': 'out_invoice',
                'partner_id': cls.partner.id,
                'invoice_line_ids': lines_to_create,
                'journal_id': cls.account_move.with_context(default_move_type='out_invoice')._get_default_journal().id,
            })
        test_account_move._compute_odoo_module_versions()
        test_account_move._update_odoo_module_dependency_lines()
        test_account_move.action_post()
        return test_account_move

    def test_constrains_app_download_token_lifetime(self):
        with self.assertRaises(ValidationError):
            self.portal_user.company_id.app_download_token_lifetime = -1.0

    def test_update_odoo_module_dependency_lines_buy_omv_test(self):
        account_move = self.create_account_move(buy_omvs=[self.test_omv_test])
        name_list = account_move.odoo_module_version_ids.mapped('name')
        name_list.sort()
        self.assertEqual(first=name_list,
                         second=['test'],
                         msg="Buy 'test' should get only 'test'")

    def test_update_odoo_module_dependency_lines_buy_omv_test_sale(self):
        account_move = self.create_account_move(buy_omvs=[self.test_omv_test_sale])
        name_list = account_move.odoo_module_version_ids.mapped('name')
        name_list.sort()
        self.assertEqual(first=name_list,
                         second=['test', 'test sale'],
                         msg="Buy 'test sale' should get 'test' & 'test sale'")
        self.assertEqual(first=self.test_omv_test_sale.with_context(partner=self.partner).can_download,
                         second=True,
                         msg="After buy 'test sale' program should let partner download app")

    def test_update_odoo_module_dependency_lines_buy_omv_test_sale_project(self):
        account_move = self.create_account_move(buy_omvs=[self.test_omv_test_sale_project])
        name_list = account_move.odoo_module_version_ids.mapped('name')
        name_list.sort()
        self.assertEqual(first=name_list,
                         second=['test', 'test sale', 'test sale project'],
                         msg="Buy 'test sale project' should get 'test', 'test sale' & 'test sale project'")
        self.assertEqual(first=self.test_omv_test_sale_project.with_context(partner=self.partner).can_download,
                         second=True,
                         msg="After buy 'test sale project' program should let partner download app")

    def test_update_odoo_module_dependency_lines_buy_omv_test_sale_template(self):
        account_move = self.create_account_move(buy_omvs=[self.test_omv_test_sale_template_12])
        name_list = account_move.odoo_module_version_ids.mapped('name')
        name_list.sort()
        self.assertEqual(first=name_list,
                         second=['test', 'test sale', 'test sale template'],
                         msg="Buy 'test sale template' should get 'test', 'test sale' & 'test sale template'")
        self.assertEqual(first=self.test_omv_test_sale_template_12.with_context(partner=self.partner).can_download,
                         second=True,
                         msg="After buy 'test sale template' program should let partner download app")

    def test_update_odoo_module_dependency_lines_all(self):
        account_move = self.create_account_move(buy_omvs=[self.test_omv_test_sale_template_12, self.test_omv_test_sale_project])
        name_list = account_move.odoo_module_version_ids.mapped('name')
        name_list.sort()
        self.assertEqual(first=name_list,
                         second=['test', 'test sale', 'test sale project', 'test sale template'],
                         msg="Buy 'test sale template' & 'test sale project' should get 'test', 'test sale', 'test sale project' & 'test sale template'")
        self.assertEqual(first=[self.test_omv_test.with_context(partner=self.partner).can_download,
                                self.test_omv_test_sale.with_context(partner=self.partner).can_download,
                                self.test_omv_test_sale_project.with_context(partner=self.partner).can_download,
                                self.test_omv_test_sale_template_12.with_context(partner=self.partner).can_download],
                         second=[True, True, True, True],
                         msg='After buy all modules program should let partner download all app')

    def test_update_odoo_module_dependency_lines_buy_omv_test_sale_paid_omv_test(self):
        account_move = self.create_account_move(buy_omvs=[self.test_omv_test_sale],
                                                paid_omvs=[self.test_omv_test])
        name_list = account_move.odoo_module_version_ids.mapped('name')
        name_list.sort()
        self.assertEqual(first=name_list,
                         second=['test sale'],
                         msg="Buy 'test sale' after buying 'test' should get 'test sale'")

    def test_update_odoo_module_dependency_lines_buy_omv_test_sale_project_paid_omv_test_sale(self):
        account_move = self.create_account_move(buy_omvs=[self.test_omv_test_sale_project],
                                                paid_omvs=[self.test_omv_test_sale])
        name_list = account_move.odoo_module_version_ids.mapped('name')
        name_list.sort()
        self.assertEqual(first=name_list,
                         second=['test', 'test sale project'],
                         msg="Buy 'test sale project' after buying 'test sale' should get 'test' & 'test sale project'")

    def test_update_odoo_module_dependency_lines_buy_omv_test_sale_template_paid_omv_test_sale_project(self):
        account_move = self.create_account_move(buy_omvs=[self.test_omv_test_sale_template_12],
                                                paid_omvs=[self.test_omv_test, self.test_omv_test_sale, self.test_omv_test_sale_project])
        name_list = account_move.odoo_module_version_ids.mapped('name')
        name_list.sort()
        self.assertEqual(first=name_list,
                         second=['test sale template'],
                         msg="Buy 'test sale template' after buying 'test sale project' should get 'test sale template'")

    def test_update_odoo_module_dependency_lines_all_paid_omv_test(self):
        account_move = self.create_account_move(buy_omvs=[self.test_omv_test_sale_project, self.test_omv_test_sale_template_12],
                                                paid_omvs=[self.test_omv_test])
        name_list = account_move.odoo_module_version_ids.mapped('name')
        name_list.sort()
        self.assertEqual(first=name_list,
                         second=['test sale', 'test sale project', 'test sale template'],
                         msg="Buy 'test sale project' & 'test sale template' after buying 'test' should get 'test sale', 'test sale project' & 'test sale template'")

