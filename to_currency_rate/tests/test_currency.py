from odoo.tests import tagged
from odoo.tests.common import TransactionCase

@tagged('post_install', '-at_install')
class TestCurrency(TransactionCase):

    def setUp(self):
        super(TestCurrency, self).setUp()
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

    def test_compute_inverse_rate(self):
        self.currency_rate.write({'rate': 0.00004})
        self.assertAlmostEqual(self.currency.inverse_rate, 25000.0)

    def test_compute_inverse_rate_rounding(self):
        self.currency_rate.write({'rate': 0.0000434338827719})
        self.assertAlmostEqual(self.currency.inverse_rate, 23023.5, places=self.currency.decimal_places)

