from odoo import fields
from odoo.tests import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestReverseMoveLine(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestReverseMoveLine, cls).setUpClass()
        cls.partner = cls.env.ref("base.res_partner_2")
        cls.currency_usd_id = cls.env.ref("base.USD").id
        cls.product = cls.env.ref("product.product_product_4")
        cls.invoice = cls.env['account.move'].with_context(tracking_disable=True).create({
            'move_type': 'out_invoice',
            'partner_id': cls.partner.id,
            'currency_id': cls.currency_usd_id,
            'invoice_date': fields.Date.to_date('2021-11-30'),
            'invoice_line_ids': [
                (0, 0, {'product_id': cls.product.id, 'quantity': 1, 'price_unit': '10000'})
            ],
        })
        cls.invoice._post(soft=False)

    def test_reverse_move_line(self):
        wizard = self.env['account.move.reversal'].create({
            'reason': 'no reason',
            'refund_method': 'cancel',
        })
        reversed_invoice = self.invoice._reverse_moves([wizard._prepare_default_reversal(self.invoice)], cancel=True)
        self.assertEqual(self.invoice.invoice_line_ids, reversed_invoice.invoice_line_ids.reversed_move_line_id)
