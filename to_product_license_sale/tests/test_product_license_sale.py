from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestProductLicenseSale(SavepointCase):

    def setUp(self):
        super(TestProductLicenseSale, self).setUp()
        self.license1 = self.env['product.license'].create({
            'name': 'License ABC Test 1',
            'short_name': 'ABC'
        })
        self.license_1_version_1 = self.env['product.license.version'].create({
            'name': '1.0',
            'date_released': '2021-01-01',
            'license_id': self.license1.id
        })
        self.license2 = self.env['product.license'].create({
            'name': 'License ABC Test 2',
            'short_name': 'ABC2'
        })
        self.license_2_version_1 = self.env['product.license.version'].create({
            'name': '1.0',
            'date_released': '2021-01-01',
            'license_id': self.license2.id
        })

        self.product1 = self.env['product.template'].create({
            'name': 'Produck',
        })
        self.product1.product_license_version_ids = self.license_1_version_1
        self.sale_order1 = self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'Partner Test'}).id
        })
        self.sale_order_line1 = self.env['sale.order.line'].create({
            'order_id': self.sale_order1.id,
            'product_id': self.product1.product_variant_id.id,
        })

    def test_compute_product_license_version_ids(self):
        self.sale_order_line1._compute_product_license_version_ids()
        self.assertEqual(self.sale_order_line1.product_license_version_ids, self.license_1_version_1)
        self.assertTrue(self.license_1_version_1.display_name in self.sale_order_line1.name)

    def test_refresh_for_licenses(self):
        with self.assertRaises(UserError):
            self.sale_order_line1.state = 'done'
            self.sale_order_line1._refresh_for_licenses()
        with self.assertRaises(UserError):
            self.sale_order_line1.state = 'cancel'
            self.sale_order_line1._refresh_for_licenses()

        self.sale_order_line1.state = 'draft'
        self.sale_order_line1._refresh_for_licenses()

    def test_inactive_license(self):
        self.product1.product_license_version_ids = [(4, self.license_2_version_1.id, 0)]
        self.sale_order1.action_refresh_for_licenses()

        self.assertTrue(self.license1.name in self.sale_order_line1.name)
        self.assertTrue(self.license2.name in self.sale_order_line1.name)
        self.assertEqual(self.sale_order1.product_license_versions_count, 2)

        self.license1.toggle_active()

        self.sale_order1.action_refresh_for_licenses()
        self.assertTrue(self.license_1_version_1.display_name not in self.sale_order_line1.name)
        self.assertTrue(self.license_2_version_1.display_name in self.sale_order_line1.name)
        self.assertEqual(self.sale_order1.product_license_versions_count, 1)

    def test_button_refresh_for_licenses(self):
        self.product1.product_license_version_ids = [(5, 0, 0)]
        self.sale_order1.action_refresh_for_licenses()
        self.product1.product_license_version_ids = self.license_1_version_1

        self.assertTrue(self.license_1_version_1.display_name not in self.sale_order_line1.name)
        self.sale_order1.action_refresh_for_licenses()
        self.assertTrue(self.license_1_version_1.display_name in self.sale_order_line1.name)

    def test_action_view_sale_lines(self):
        # case 5:
        self.license_1_version_1.sale_line_ids = self.sale_order_line1
        self.sale_order1.action_confirm()

        action = self.license_1_version_1.action_view_sale_lines()
        self.assertEqual(action['type'], 'ir.actions.act_window')
        self.assertEqual(action['res_model'], 'sale.order.line')
        self.assertEqual(action['domain'], "[('id', 'in', [%s])]" % self.sale_order_line1.id)
