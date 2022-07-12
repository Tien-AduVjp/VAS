from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged
from odoo import fields


@tagged('post_install', '-at_install')
class PricelistRecurring(TransactionCase):
    def setUp(self):
        super(PricelistRecurring, self).setUp()
        self.partner_1 = self.env['res.partner'].create({
            'name': 'Contact A',
            'company_type': 'company'
        })
        self.datacard = self.env.ref('product.product_delivery_02')
        self.usb_adapter = self.env.ref('product.product_delivery_01')

        self.usb_adapter.write({
            'list_price': 10000000.0,
            'standard_price': 10000000.0,
        })
        self.datacard.write({
            'list_price': 20000000.0,
            'standard_price': 20000000.0,
        })
        self.product_1 = self.env['product.template'].create({
            'name': 'product_1',
            'list_price': 10000000.0,
            'standard_price': 10000000.0,
        })
        self.product_2 = self.env['product.template'].create({
            'name': 'product_2',
            'list_price': 20000000.0,
            'standard_price': 20000000.0,
        })
        self.pricelist_1 = self.env['product.pricelist'].create({
            'name': 'Ghost month',
            'item_ids': [(0, 0, {
                'date_start': "2021-08-01",
                'date_end': "2022-08-31",
                'recurring': True,
                'applied_on': '1_product',
                'product_tmpl_id': self.product_1.id,
                'recurring_period': 'monthly',
                'recurring_day_from': 1,
                'recurring_day_to': 31,
                'compute_price': 'fixed',
                'fixed_price': 5000000,
            }), (0, 0, {
                'date_start': "2022-09-01",
                'date_end': "2050-07-31",
                'recurring': True,
                'applied_on': '1_product',
                'product_tmpl_id': self.product_1.id,
                'recurring_period': 'annually',
                'recurring_day_from': 1,
                'recurring_month_from': '8',
                'recurring_day_to': 31,
                'recurring_month_to': '9',
                'compute_price': 'fixed',
                'fixed_price': 6000000,
            })]
        })

    def test_1000_check_validate(self):
        item_1 = self.pricelist_1.item_ids[0]
        item_2 = self.pricelist_1.item_ids[1]
        """1<= recurring_day_from, recurring_day_to <=31
            recurring_day_from, recurring_day_to is integer"""
        self.assertRaises(ValueError, item_1.write, {'recurring_day_from': 'a'})
        self.assertRaises(ValueError, item_1.write, {'recurring_day_to': 'a'})
        self.assertRaises(ValidationError, item_1.write, {'recurring_day_from': -1})
        self.assertRaises(ValidationError, item_1.write, {'recurring_day_to': -1})
        self.assertRaises(ValidationError, item_1.write, {'recurring_day_from': 32})
        self.assertRaises(ValidationError, item_1.write, {'recurring_day_to': 32})
        self.assertRaises(ValidationError, item_1.write, {'recurring_day_from': 10,
                                                          'recurring_day_to': 9})
        self.assertRaises(ValueError, item_2.write, {'recurring_day_from': 'a'})
        self.assertRaises(ValueError, item_2.write, {'recurring_day_to': 'a'})
        self.assertRaises(ValidationError, item_2.write, {'recurring_day_from': -1})
        self.assertRaises(ValidationError, item_2.write, {'recurring_day_to': -1})
        self.assertRaises(ValidationError, item_2.write, {'recurring_day_from': 32})
        self.assertRaises(ValidationError, item_2.write, {'recurring_day_to': 32})
        self.assertRaises(ValidationError, item_2.write, {'recurring_month_from': '1',
                                                          'recurring_month_to': '1',
                                                          'recurring_day_from': 10,
                                                          'recurring_day_to': 9})
        self.assertRaises(ValidationError, item_2.write, {'recurring_month_from': '2',
                                                          'recurring_month_to': '1',
                                                          'recurring_day_from': 10,
                                                          'recurring_day_to': 9})
        self.assertRaises(ValidationError, item_2.write, {'recurring_month_from': '2',
                                                          'recurring_month_to': '1',
                                                          'recurring_day_from': 10,
                                                          'recurring_day_to': 11})
        self.assertRaises(ValidationError, item_2.write, {'recurring_month_from': '2',
                                                          'recurring_month_to': '1',
                                                          'recurring_day_from': 10,
                                                          'recurring_day_to': 10})
        item_1.write({
            'recurring_day_from': 1
        })
        item_1.write({
            'recurring_day_to': 1
        })
        item_1.write({
            'recurring_day_to': 15
        })
        item_1.write({
            'recurring_day_to': 31
        })
        item_1.write({
            'recurring_day_from': 31
        })
        item_1.write({
            'recurring_day_from': 15
        })
        item_1.write({
            'recurring_day_from': 10,
            'recurring_day_to': 11
        })
        item_1.write({
            'recurring_day_from': 10,
            'recurring_day_to': 10
        })

        item_2.write({
            'recurring_month_from': '1',
            'recurring_month_to': '1',
            'recurring_day_from': 10,
            'recurring_day_to': 11
        })
        item_2.write({
            'recurring_month_from': '1',
            'recurring_month_to': '1',
            'recurring_day_from': 10,
            'recurring_day_to': 10
        })

        item_2.write({
            'recurring_month_from': '1',
            'recurring_month_to': '2',
            'recurring_day_from': 10,
            'recurring_day_to': 11
        })
        item_2.write({
            'recurring_month_from': '1',
            'recurring_month_to': '2',
            'recurring_day_from': 10,
            'recurring_day_to': 10
        })
        item_2.write({
            'recurring_month_from': '1',
            'recurring_month_to': '2',
            'recurring_day_from': 10,
            'recurring_day_to': 9
        })
        item_2.write({
            'recurring_day_from': 1
        })
        item_2.write({
            'recurring_day_to': 1
        })
        item_2.write({
            'recurring_day_to': 15
        })
        item_2.write({
            'recurring_day_to': 31
        })
        item_2.write({
            'recurring_day_from': 31
        })
        item_2.write({
            'recurring_day_from': 15
        })

    def test_1001_get_product_price_monthly(self):
        self.pricelist_1.item_ids[0].write({
            'recurring_day_to': 15
        })
        self.assertEqual(5000000,
                         self.pricelist_1.get_product_price(self.product_1, 1, self.partner_1, fields.Date.to_date('2021-08-11')),
                         'viin_pricelist_recurring: Pricelist not working')
        self.assertEqual(5000000,
                         self.pricelist_1.get_product_price(self.product_1, 1, self.partner_1, fields.Date.to_date('2021-09-01')),
                         'viin_pricelist_recurring: Pricelist not working')
        self.assertEqual(10000000,
                         self.pricelist_1.get_product_price(self.product_1, 1, self.partner_1, fields.Date.to_date('2021-08-16')),
                         'viin_pricelist_recurring: Pricelist not working')
        self.assertEqual(20000000,
                         self.pricelist_1.get_product_price(self.product_2, 1, self.partner_1, fields.Date.to_date('2021-08-11')),
                         'viin_pricelist_recurring: Pricelist not working')

    def test_1002_get_product_price_annually(self):
        self.pricelist_1.item_ids[1].write({
            'recurring_day_from': 1,
            'recurring_month_from': '1',
            'recurring_day_to': 15,
            'recurring_month_to': '2',
        })
        self.assertEqual(10000000,
                         self.pricelist_1.get_product_price(self.product_1, 1, self.partner_1, fields.Date.to_date('2023-08-18')),
                         'viin_pricelist_recurring: Pricelist not working')
        self.assertEqual(6000000,
                         self.pricelist_1.get_product_price(self.product_1, 1, self.partner_1, fields.Date.to_date('2023-01-02')),
                         'viin_pricelist_recurring: Pricelist not working')
        self.assertEqual(20000000,
                         self.pricelist_1.get_product_price(self.product_2, 1, self.partner_1, fields.Date.to_date('2023-01-02')),
                         'viin_pricelist_recurring: Pricelist not working')
