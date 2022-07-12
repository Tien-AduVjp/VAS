from unittest import mock
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo.addons.viin_auto_currency_rate.tests.test_rate import RateTest


@tagged('post_install', '-at_install', 'external', '-standard')
class VCBTest(RateTest):

    def setUp(self):
        super(VCBTest, self).setUp()

        self.bank_vcb = self.env['res.bank'].create({
            'name': 'VCB',
            'auto_rate_update': True,
            'auto_rate_update_provider': 'vcb',
            })

    def _prepare_domain_get_currency_rate(self, date, currency):
        return [('name', '=', date), ('currency_id', '=', currency.id)]

    def _get_currency_rate(self, date, currency):
        return self.env['res.currency.rate'].search(self._prepare_domain_get_currency_rate(date, currency), limit=1)

    def _test_vcb_cron_currency_rate_sync(self, date):
        rate_usd = self._get_currency_rate(date, self.currency_usd)
        self.assertNotEqual(rate_usd.name, date, 'VCB: Rate date %s instead of False' % rate_usd.name)
        self.bank_vcb._cron_currency_rate_sync()
        self.assertEqual(self.bank_vcb.auto_rate_last_sync, date, 'VCB: Last sync date %s instead of %s' % (self.bank_vcb.auto_rate_last_sync, date))
        rate_usd = self._get_currency_rate(date, self.currency_usd)
        self.assertEqual(rate_usd.name, date, 'VCB: Last sync date %s instead of %s' % (rate_usd.name, date))

    def test_dynamic_method_availability(self):
        self.assertTrue(hasattr(self.env['res.bank'], '_vcb_sync_currency_rate'), "The method `_vcb_sync_currency_rate()` is not implemented yet.")

    def test_10_vcb_configuration(self):
        self.assertEqual(self.bank_vcb.auto_rate_update_provider, 'vcb', 'VCB: Service provider %s instead of vcb' % self.bank_vcb.auto_rate_update_provider)

    @mute_logger('odoo.addons.viin_auto_currency_rate.models.res_bank')
    def test_20_vcb_cron_currency_rate_sync(self):
        date = fields.Date.today()
        self._test_vcb_cron_currency_rate_sync(date)

    def test_30_cron_currency_rate_not_active(self):
        date = fields.Date.today()
        self.currency_usd.active = False
        currency_idr = self.env.ref('base.IDR')
        self.bank_vcb._cron_currency_rate_sync()

        self.assertFalse(self._get_currency_rate(date, self.currency_usd))
        self.assertFalse(self._get_currency_rate(date, currency_idr))

    def test_40_cron_currency_rate_bank_not_support(self):
        date = fields.Date.today()
        self.bank_vcb.write({
            'auto_rate_update': False,
            'auto_rate_update_provider': '',})
        self.bank_vcb._cron_currency_rate_sync()
        self.assertNotEqual(self.bank_vcb.auto_rate_last_sync, date, 'VCB: Last sync date %s instead of %s' % (self.bank_vcb.auto_rate_last_sync, date))
        self.assertFalse(self._get_currency_rate(date, self.currency_usd).filtered(lambda b: b.bank_id == self.bank_vcb.id))

    @mute_logger('odoo.addons.viin_auto_currency_rate.models.res_bank')
    def test_50_cron_currency_rate_exist(self):
        date = fields.Date.today()
        self.env['res.currency.rate'].create({
            'name': date,
            'exchange_type': 'buy_rate',
            'rate': 999,
            'currency_id': self.currency_usd.id
            })
        self.bank_vcb._cron_currency_rate_sync()
        transfer_rate_usd = self._get_currency_rate(date, self.currency_usd).filtered(lambda c: c.exchange_type == 'transfer_rate')
        self.assertFalse(transfer_rate_usd)
        sell_rate_usd = self._get_currency_rate(date, self.currency_usd).filtered(lambda c: c.exchange_type == 'sell_rate')
        self.assertFalse(sell_rate_usd)

    @mute_logger('odoo.addons.viin_auto_currency_rate.models.res_bank')
    def test_60_cron_curency_rate_multi_banks(self):
        date = fields.Date.today()
        self.env['res.bank'].create([
            {
            'name': 'VCB Bank Test 2',
            'auto_rate_update': True,
            'auto_rate_update_provider': 'vcb',
            },
            {
            'name': 'VCB Bank Test 3',
            'auto_rate_update': True,
            'auto_rate_update_provider': 'vcb',
            }])
        banks = self.env['res.bank'].search([
            ('auto_rate_update', '=', True),
            ('auto_rate_update_provider', '=', 'vcb'),
            ('auto_rate_last_sync', '!=', date)])
        self.bank_vcb._cron_currency_rate_sync()
        rates_usd = self.env['res.currency.rate'].search(self._prepare_domain_get_currency_rate(date, self.currency_usd))

        buy_rates_usd = rates_usd.filtered(lambda r: r.exchange_type == 'buy_rate')
        self.assertEqual(len(buy_rates_usd), len(banks))

        transfer_rates_usd = rates_usd.filtered(lambda r: r.exchange_type == 'transfer_rate')
        self.assertEqual(len(transfer_rates_usd), len(banks))

        sell_rates_usd = rates_usd.filtered(lambda r: r.exchange_type == 'sell_rate')
        self.assertEqual(len(sell_rates_usd), len(banks))

    def test_70_vcb_server_connection_failed(self):
        date = fields.Date.today()
        with mock.patch('odoo.addons.viin_auto_currency_rate.models.res_bank.ResBank._get_data_from_service_provider') as mocked:
            mocked.return_value = False
            message = 'ERROR:odoo.addons.viin_auto_currency_rate.models.res_bank:Auto Currency Rates Update Service Provider "%s" failed to obtain data since %s.' \
                % (self.bank_vcb.auto_rate_update_provider, date)
            logger = 'odoo.addons.viin_auto_currency_rate.models.res_bank'
            with self.assertLogs(logger, level='ERROR') as e:
                self.bank_vcb._cron_currency_rate_sync()
                self.assertTrue(message in e.output)

                rate_usd = self._get_currency_rate(date, self.currency_usd)
                self.assertFalse(rate_usd)

    def test_80_cron_currency_rate_backdate(self):
        date = fields.Date.today()

        self.env['res.currency.rate'].search([
            ('name', '>=', date - timedelta(days=3)),
            ('bank_id', '=', self.bank_vcb.id)
            ]).unlink()
        self.env['res.currency.rate'].create({
            'name': date - timedelta(days=3),
            'exchange_type': 'buy_rate',
            'rate': 999,
            'currency_id': self.currency_usd.id,
            'bank_id': self.bank_vcb.id,
            })
        self.bank_vcb._cron_currency_rate_sync()

        rate_backdate = self.env['res.currency.rate'].search([
            ('name', '=', date - timedelta(days=2)),
            ('bank_id', '=', self.bank_vcb.id)
            ])
        self.assertTrue(rate_backdate)
