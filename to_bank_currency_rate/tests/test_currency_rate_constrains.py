try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    import psycopg2
    UniqueViolation = psycopg2.IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger

from .common import Common


@tagged('post_install', '-at_install')
class TestCurrencyRates(Common):

    @mute_logger('odoo.sql_db')
    def test_01_currency_rate_constrains(self):
        self.create_rate(self.vnd, 2.0, self.bank_default, 'buy_rate', '2010-01-01')
        with self.assertRaises(UniqueViolation):
            self.create_rate(self.vnd, 1.0, self.bank_default, 'buy_rate', '2010-01-01')
