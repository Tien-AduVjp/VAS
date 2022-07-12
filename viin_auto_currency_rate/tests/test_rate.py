from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import SavepointCase


@tagged('post_install', '-at_install', 'external', '-standard')
class RateTest(SavepointCase):

    def setUp(self):
        super(RateTest, self).setUp()

        self.company_us = self.env['res.company'].create({
            'name': 'Test Company (US)',
            'currency_id': self.env.ref('base.USD').id
            })

        self.company_vn = self.env['res.company'].create({
            'name': 'Test Company (VN)',
            'currency_id': self.env.ref('base.VND').id,
            })

        self.bank = self.env['res.bank'].create({
            'name': 'Bank',
            'auto_rate_update': False,
            'auto_rate_update_provider': False,
            })

        self.env['res.currency.rate'].search([]).unlink()

        self.currency_vnd = self.env.ref('base.VND')
        self.currency_usd = self.env.ref('base.USD')

    def test_10_acb_configuration(self):
        self.assertEqual(self.bank.auto_rate_update_provider, False, 'Service provider %s instead of False' % self.bank.auto_rate_update_provider)
        self.assertEqual(self.bank.auto_rate_last_sync, False, 'Last Synchronization Date %s instead of False' % self.bank.auto_rate_last_sync)
