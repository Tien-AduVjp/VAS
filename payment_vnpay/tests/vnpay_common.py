import datetime

from odoo import fields

from odoo.addons.payment.tests.common import PaymentAcquirerCommon


class VNPayCommon(PaymentAcquirerCommon):

    def setUp(self):
        super(VNPayCommon, self).setUp()

        self.currency_vnd = self.env.ref('base.VND')
        if not self.currency_vnd.active:
            self.currency_vnd.active = True
        self.currency_usd = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)

        self.country_vn = self.env['res.country'].search([('code', 'like', 'VN')], limit=1)

        self.env.company._write({'currency_id': self.currency_vnd.id})

        Rate = self.env['res.currency.rate']
        self.currency_vnd.rate_ids.unlink()

        self.currency_vnd.rate_ids = Rate.create({
            'name': fields.Date.today(),
            'rate': 1,
            'currency_id': self.currency_vnd.id
        })

        self.currency_euro.rate_ids = Rate.create([{
            'name': fields.Date.today() - datetime.timedelta(days=1),
            'inverse_rate': 25000,
            'currency_id': self.currency_euro.id
        }])

        self.currency_usd.rate_ids = Rate.create([{
            'name': fields.Date.today() - datetime.timedelta(days=2),
            'inverse_rate': 23000,
            'currency_id': self.currency_usd.id
        }])

        self.vnpay = self.env.ref('payment_vnpay.payment_acquirer_vnpay')
        self.vnpay.write({
            'vnpay_tmn_code': 'CHUQJ682', # VNPay Website Code
            'vnpay_hash_secret': 'VHSSRMBFCMBPBCEULEHVYCAUDWYODPNJ', # VNPay Hash Secret
            'state': 'test',
            })
