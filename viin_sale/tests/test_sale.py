from unittest.mock import patch
from datetime import datetime

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSale(TransactionCase):

    def test_compute_days_to_confirm(self):
        sale_order = self.env.ref('sale.sale_order_1')
        with patch('odoo.fields.Datetime.now', return_value=datetime(2021, 9, 29, 14, 0, 0)):
            sale_order.action_confirm()
        delta = sale_order.date_order - sale_order.create_date
        days_to_confirm = delta.days + delta.seconds / 3600 / 24
        self.assertEqual(sale_order.days_to_confirm, days_to_confirm)
