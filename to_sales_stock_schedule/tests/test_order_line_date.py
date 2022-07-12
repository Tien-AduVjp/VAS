
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged
from odoo import fields

@tagged('post_install', '-at_install')
class TestOrderLineExpectedDate(TransactionCase):

    def setUp(self):
        super(TestOrderLineExpectedDate, self).setUp()

        self.sale_order = self._get_new_sale_order()
        self.order_line = self.sale_order.order_line[:1]

    @patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2021-09-12 09:01:02'))
    def _get_new_sale_order(self, amount=10.0):
        test_partner = self.env.ref('base.res_partner_1')
        test_product = self.env.ref('product.product_delivery_01')
        vals = {
            'partner_id': test_partner.id,
            'partner_invoice_id': test_partner.id,
            'partner_shipping_id': test_partner.id,
            'date_order': fields.Datetime.now(),
            'order_line': [(0, 0, {
                'name': test_product.name,
                'product_id': test_product.id,
                'product_uom_qty': amount,
                'product_uom': test_product.uom_id.id,
                'price_unit': 100})],
        }
        sale_order = self.env['sale.order'].create(vals)
        return sale_order

    @patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2021-09-12 09:01:02'))
    def test_01_compute_expected_date(self):
        self.assertEqual(self.order_line.date_expected, fields.Datetime.now())

    @patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2021-09-12 09:01:02'))
    def test_02_compute_expected_date(self):
        new_date_expected = fields.Datetime.from_string('2021-09-02 09:01:02')
        self.order_line.date_expected = fields.Datetime.to_string(new_date_expected)

        self.assertEqual(self.order_line.customer_lead, -10)

        new_date_expected = fields.Datetime.from_string('2021-09-22 09:01:02')
        self.order_line.date_expected = fields.Datetime.to_string(new_date_expected)

        self.assertEqual(self.order_line.customer_lead, 10)

        now = fields.Datetime.now()
        self.order_line.date_expected = now
        self.assertEqual(self.order_line.date_expected, now)
        self.assertEqual(self.order_line.customer_lead, 0)

    @patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2021-09-12 09:01:02'))
    def test_03_compute_expected_date(self):

        self.sale_order.date_order = fields.Datetime.to_datetime('2021-09-05 09:01:02')
        self.order_line.customer_lead = 3
        self.assertEqual(self.order_line.date_expected, fields.Datetime.to_datetime('2021-09-08 09:01:02'))

        self.sale_order.action_confirm()
        self.assertEqual(self.order_line.date_expected, fields.Datetime.to_datetime('2021-09-15 09:01:02'))
