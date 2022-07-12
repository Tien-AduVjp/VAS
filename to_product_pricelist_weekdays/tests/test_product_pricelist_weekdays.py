from odoo.tests import tagged, common
from odoo import fields


@tagged('post_install', '-at_install')
class TestProductPricelistWeekdays(common.TransactionCase):

    def setUp(self):
        super(TestProductPricelistWeekdays, self).setUp()
        self.partner_1 = self.env['res.partner'].create({'name': 'partner_1'})
        self.product_1 = self.env['product.template'].create(
            {
                'name': 'product_1',
                'list_price': 10000000.0,
                'standard_price': 10000000
            })
        self.product_2 = self.env['product.template'].create(
            {
                'name': 'product_2',
                'list_price': 20000000.0,
                'standard_price': 20000000
            })
        self.pricelist_1 = self.env['product.pricelist'].create({
            'name': 'Ghost month',
            'item_ids': [(0, 0, {
                'date_start': "2021-08-01",
                'date_end': "2021-08-31",
                'applied_on': '1_product',
                'product_tmpl_id': self.product_1.id,
                'days_of_week': True,
                'wed': True,
                'mon': True,
                'compute_price': 'fixed',
                'fixed_price': 5000000,
            })]
        })

    def test_00_get_product_price(self):

        def _check_pricelist(price_discount):
            self.assertEqual(price_discount,
                             self.pricelist_1.get_product_price(self.product_1, 1, self.partner_1, fields.Date.to_date('2021-08-18')),
                             'to_product_pricelist_weekdays: Pricelist not working')
            self.assertEqual(price_discount,
                             self.pricelist_1.get_product_price(self.product_1, 1, self.partner_1, fields.Date.to_date('2021-08-16')),
                             'to_product_pricelist_weekdays: Pricelist not working')
            self.assertEqual(10000000,
                             self.pricelist_1.get_product_price(self.product_1, 1, self.partner_1, fields.Date.to_date('2021-08-12')),
                             'to_product_pricelist_weekdays: Pricelist not working')
            self.assertEqual(20000000,
                             self.pricelist_1.get_product_price(self.product_2, 1, self.partner_1, fields.Date.to_date('2021-08-18')),
                             'to_product_pricelist_weekdays: Pricelist not working')

        _check_pricelist(5000000)
        self.pricelist_1.item_ids.write({
            'compute_price': 'percentage',
            'percent_price': 10,
        })
        _check_pricelist(9000000)

        self.pricelist_1.item_ids.write({
            'compute_price': 'formula',
            'price_discount': 20,
        })
        _check_pricelist(8000000)
