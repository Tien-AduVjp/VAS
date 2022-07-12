from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestViinSaleProductDuplicationWarning(TransactionCase):

    def setUp(self):
        super(TestViinSaleProductDuplicationWarning, self).setUp()
        self.product1 = self.env['product.template'].create({
            'name': 'Produck Test 1'
        })
        self.product2 = self.env['product.template'].create({
            'name': 'Produck Test 2'
        })
        self.sale_order1 = self.env['sale.order'].create({
            'partner_id': self.env['res.partner'].create({'name': 'Partner Test'}).id
        })
        self.env['sale.order.line'].create({
            'product_id': self.product1.product_variant_id.id,
            'order_id': self.sale_order1.id
        })

    def test_compute_product_duplication_warning(self):
        self.assertEquals(self.sale_order1.product_duplication_warning, False)
        self.env['sale.order.line'].create({
            'product_id': self.product1.product_variant_id.id,
            'order_id': self.sale_order1.id
        })
        self.assertNotEqual(self.sale_order1.product_duplication_warning, False)

    def test_ignore_product_duplication_warning(self):
        self.product1.ignore_product_duplication_warning = True
        self.env['sale.order.line'].create({
            'product_id': self.product1.product_variant_id.id,
            'order_id': self.sale_order1.id
        })
        self.assertEqual(self.sale_order1.product_duplication_warning, False)
