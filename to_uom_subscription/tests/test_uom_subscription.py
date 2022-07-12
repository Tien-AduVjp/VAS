import datetime

from odoo.exceptions import UserError
from odoo.tests.common import tagged, SingleTransactionCase


@tagged('post_install', '-at_install')
class TestUomSubscription(SingleTransactionCase):

    def test_01_calculate_subscription_month_quantity(self):
        result = self.env['uom.uom'].calculate_subscription_month_quantity(
            dt_start=datetime.datetime(2019, 1, 1),
            dt_end=datetime.datetime(2019, 1, 31)
        )
        self.assertEqual(result, 1.0, "to_uom_subscription: wrong calculate_subscription_month_quantity")

    def test_02_calculate_subscription_month_quantity(self):
        result = self.env['uom.uom'].calculate_subscription_month_quantity(
            dt_start=datetime.datetime(2019, 1, 2),
            dt_end=datetime.datetime(2019, 1, 31)
        )
        self.assertEqual(result, 1.0, "to_uom_subscription: wrong calculate_subscription_month_quantity")

    def test_03_calculate_subscription_month_quantity(self):
        result = self.env['uom.uom'].calculate_subscription_month_quantity(
            dt_start=datetime.datetime(2019, 1, 3),
            dt_end=datetime.datetime(2019, 3, 31)
        )
        self.assertEqual(result, 3.0, "to_uom_subscription: wrong calculate_subscription_month_quantity")

    def test_04_calculate_subscription_month_quantity(self):
        result = self.env['uom.uom'].calculate_subscription_month_quantity(
            dt_start=datetime.datetime(2019, 1, 3),
            dt_end=datetime.datetime(2019, 3, 14)
        )
        self.assertEqual(result, 2.465, "to_uom_subscription: wrong calculate_subscription_month_quantity")

    def test_05_delete_referenced_uom(self):
        with self.assertRaises(UserError):
            self.env.ref('to_uom_subscription.uom_categ_subscription').unlink()
        with self.assertRaises(UserError):
            self.env.ref('to_uom_subscription.uom_categ_subscription_user').unlink()
