from odoo.addons.to_odoo_module.tests.test_common import TestCommon
from odoo.tests import Form, tagged


@tagged('post_install', '-at_install')
class TestSaleOrderTemplate(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderTemplate, cls).setUpClass()

        cls.module_category_sale = cls.env['ir.module.category'].create({
            'name': 'Sale Test',
        })
        cls.test_omv_test_sale.write({'ir_module_category_id': cls.module_category_sale.id})

        cls.module_category_sale_project = cls.env['ir.module.category'].create({
            'name': 'Sale Project Test',
        })
        cls.test_omv_test_sale_project.write({'ir_module_category_id': cls.module_category_sale_project.id})
        cls.test_omv_test_sale_template_13.write({'ir_module_category_id': cls.module_category_sale_project.id})

        cls.module_category_sale_template = cls.env['ir.module.category'].create({
            'name': 'Test Sale Template',
        })
        cls.test_omv_test_sale_template_12.write({'ir_module_category_id': cls.module_category_sale_template.id})

    def test_sale_order_template(self):
        so_template_form = Form(self.env['sale.order.template'])
        so_template_form.name = 'Default Template'
        so_template_form.odoo_version_id = self.odoo_version_12

        """TC 1: Add new line, then check autoload_odoo_apps = True
        """
        so_template_form.autoload_odoo_apps = False
        with so_template_form.sale_order_template_line_ids.new() as line:
            line.product_id = self.test_omv_test_sale.product_id
        so_template_form.autoload_odoo_apps = True
        self.assertEqual(len(so_template_form.sale_order_template_line_ids._records), 0)

        """TC 2: Add new line, save form, then check autoload_odoo_apps = True
        """
        so_template_form.autoload_odoo_apps = False
        with so_template_form.sale_order_template_line_ids.new() as line:
            line.product_id = self.test_omv_test_sale.product_id
        so_template_form.save()
        with so_template_form.sale_order_template_line_ids.new() as line:
            line.product_id = self.test_omv_test_sale_project.product_id
        so_template_form.autoload_odoo_apps = True
        self.assertEqual(list(map(lambda x: x['product_id'], so_template_form.sale_order_template_line_ids._records)), self.test_omv_test_sale.product_id.ids)

        """TC 3: When autoload_odoo_apps = True, odoo_version_id must be required
        """
        so_template_form.autoload_odoo_apps = True
        self.assertEqual(so_template_form._get_modifier('odoo_version_id', 'required'), True)

        """TC 4: Add new App Categories
        """
        so_template_form.ir_module_category_ids.add(self.module_category_sale_project)
        omv_list = self.test_omv_test_sale.product_id | self.test_omv_test_sale_project.product_id
        self.assertEqual(list(map(lambda x: x['product_id'], so_template_form.sale_order_template_line_ids._records)), omv_list.ids)

        """TC 5: Add new App Categories
        """
        so_template_form.ir_module_category_ids.add(self.module_category_sale_template)
        omv_list |= self.test_omv_test_sale_template_12.product_id
        self.assertEqual(list(map(lambda x: x['product_id'], so_template_form.sale_order_template_line_ids._records)), omv_list.ids)

        """TC 6: Change odoo_version_id
        """
        so_template_form.odoo_version_id = self.odoo_version_13
        omv_list = self.test_omv_test_sale.product_id | self.test_omv_test_sale_template_13.product_id
        self.assertEqual(list(map(lambda x: x['product_id'], so_template_form.sale_order_template_line_ids._records)), omv_list.ids)
