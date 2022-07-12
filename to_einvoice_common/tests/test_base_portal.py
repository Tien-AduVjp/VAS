from odoo import fields
from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestEInvoicePortalCommon(AccountingTestCase):

    def setUp(self):
        super(TestEInvoicePortalCommon, self).setUp()
        self.partner_agrolait = self.env.ref("base.res_partner_2")
        self.currency_usd_id = self.env.ref("base.USD").id
        self.product = self.env.ref("product.product_product_4")
        self.invoice = self.env['account.move'].create({
            'type': 'out_invoice',
            'partner_id': self.partner_agrolait.id,
            'currency_id': self.currency_usd_id,
            'invoice_date': fields.Date.to_date('2021-07-30'),
            'invoice_line_ids': [
                (0, 0, {'product_id': self.product.id, 'quantity': 1, 'price_unit': '10000'})
            ],
        })
        self.invoice.post()
        self.invoice.write({'einvoice_state': 'issued'})
