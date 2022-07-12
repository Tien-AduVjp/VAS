from psycopg2 import IntegrityError

from odoo.tools import mute_logger
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestCurrencyRate(TransactionCase):

    def setUp(self):
        super(TestCurrencyRate, self).setUp()
        self.currency = self.env['res.currency'].create({
            'name': 'TEST',
            'symbol': '@',
            'rounding': 0.01
        })

        self.currency_rate = self.env['res.currency.rate'].create({
            'name': '2020-01-01',
            'rate': 1.0,
            'currency_id': self.currency.id
        })

    def test_set_integer_inverse_rate(self):
        self.currency_rate.write({'inverse_rate': 25000})
        self.assertAlmostEqual(self.currency_rate.rate, 0.00004)

    def test_set_float_inverse_rate(self):
        self.currency_rate.write({'inverse_rate': 23023.5})
        self.assertAlmostEqual(self.currency_rate.rate, 0.00004343388277195, places=16)

    def test_set_zero_inverse_rate(self):
        self.currency_rate.write({'inverse_rate': 0.0})
        self.assertEqual(self.currency_rate.rate, 1.0)

    def test_set_almost_zero_inverse_rate(self):
        self.currency_rate.write({'inverse_rate': 0.00000000000000001})
        self.assertEqual(self.currency_rate.rate, 1.0)

    @mute_logger('odoo.sql_db')
    def test_set_negative_inverse_rate(self):
        with self.assertRaises(IntegrityError):
            self.currency_rate.write({'inverse_rate':-1.0})
            self.currency_rate.flush()

    def test_compute_inverse_rate(self):
        self.currency_rate.write({'rate': 0.00004})
        self.assertAlmostEqual(self.currency_rate.inverse_rate, 25000.0)

    def test_compute_inverse_rate_rounding(self):
        self.currency_rate.write({'rate': 0.0000434338827719})
        self.assertAlmostEqual(self.currency_rate.inverse_rate, 23023.5, places=self.currency.decimal_places)

    @mute_logger('odoo.sql_db')
    def test_compute_inverse_rate_zero(self):
        with self.assertRaises(IntegrityError):
            self.currency_rate.write({'rate': 0.0})
            self.currency.flush()

    @mute_logger('odoo.sql_db')
    def test_compute_inverse_rate_negative(self):
        with self.assertRaises(IntegrityError):
            self.currency_rate.write({'rate':-1.0})
            self.currency.flush()
