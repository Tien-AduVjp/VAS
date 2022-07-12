from odoo.tests import Form, tagged

from odoo.addons.to_odoo_module.tests import test_common


@tagged('post_install', '-at_install')
class TestSaleOrder(test_common.TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()

        so_write_val = {
            'price_currency': 5.0
        }
        cls.test_omv_test_sale.write(so_write_val)
        cls.test_omv_test_sale_project.write(so_write_val)
        cls.account_move = cls.env['account.move']

    def test_onchange_order_line_and_partner(self):
        account_move_line = {
            'product_id': self.test_omv_test.product_id.id,
            'name': self.test_omv_test.product_id.name,
        }
        paid_ai = self.account_move.create({
            'type': 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_line_ids': [(0, 0, account_move_line)],
            'journal_id': self.account_move.with_context(default_type='out_invoice')._get_default_journal().id,
        })
        paid_ai.action_post()

        self.partner.write({'exclude_already_purchased_apps': True})
        so_form = Form(self.env['sale.order'])
        so_form.partner_id = self.partner

        with so_form.order_line.new() as line:
            line.product_id = self.test_omv_test_sale.product_id
            line.product_uom_qty = 1.0
        so = so_form.save()
        omv_list = self.test_omv_test_sale
        self.assertEqual(so.odoo_module_version_ids, omv_list)
        self.assertEqual(so.amount_untaxed, 5.0, "The sales order should have the total price of four modules: 'test sale'")

        with so_form.order_line.new() as line:
            line.product_id = self.test_omv_test_sale_project.product_id
            line.product_uom_qty = 1.0
        so = so_form.save()
        omv_list = self.test_omv_test_sale_project | self.test_omv_test_sale
        self.assertEqual(so.odoo_module_version_ids, omv_list)
        self.assertEqual(so.amount_untaxed, 10.0, "The sales order should have the total price of four modules: 'test sale' & 'test sale project'")

        so_form.exclude_already_purchased_apps = False
        with so_form.order_line.new() as line:
            line.product_id = self.test_omv_test_sale.product_id
            line.product_uom_qty = 1.0
        so = so_form.save()
        omv_list = self.test_omv_test_sale_project | self.test_omv_test_sale | self.test_omv_test
        self.assertEqual(so.odoo_module_version_ids, omv_list)
        self.assertEqual(so.amount_untaxed, 15.0, "The sales order should have the total price of four modules: 'test sale', 'test sale' & 'test sale project'")
