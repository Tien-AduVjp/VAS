import datetime

from odoo import fields

from odoo.addons.payment.tests.common import PaymentAcquirerCommon


class MoMoCommon(PaymentAcquirerCommon):

    def setUp(self):
        super(MoMoCommon, self).setUp()

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
            'rate': 1 / 25000,
            'currency_id': self.currency_euro.id
        }])

        self.currency_usd.rate_ids = Rate.create([{
            'name': fields.Date.today() - datetime.timedelta(days=2),
            'rate': 1 / 23000,
            'currency_id': self.currency_usd.id
        }])

        self.momo = self.env.ref('payment_momo.payment_acquirer_momo')
        self.momo.write({
            'momo_partner_code': 'MOMO',
            'momo_access_key': 'F8BBA842ECF85',
            'momo_secret_key': 'K951B6PE1waDMi640xX08PD3vg6EkVlz',
            'state': 'test',
            })
