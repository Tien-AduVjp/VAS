from unittest.mock import patch
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from odoo import fields
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo.addons.viin_auto_currency_rate.tests.test_rate import RateTest


@tagged('post_install', '-at_install')
class ACBTest(RateTest):

    def setUp(self):
        super(ACBTest, self).setUp()
        
        self.bank_acb = self.env['res.bank'].create({
            'name': 'ACB',
            'auto_rate_update': True,
            'auto_rate_update_provider': 'acb',
            })
    
    def _prepare_domain_get_currency_rate(self, date, currency):
        return [('name', '=', date), ('currency_id', '=', currency.id)]
    
    def _get_currency_rate(self, date, currency):
        return self.env['res.currency.rate'].search(self._prepare_domain_get_currency_rate(date, currency), limit=1)
    
    def _test_acb_cron_currency_rate_sync(self, date):
        rate_usd = self._get_currency_rate(date, self.currency_usd)
        self.assertNotEqual(rate_usd.name, date, 'ACB: Rate date %s instead of False' % rate_usd.name)
        try:
            self.bank_acb._cron_currency_rate_sync()
            self.assertEqual(self.bank_acb.auto_rate_last_sync, date, 'ACB: Last sync date %s instead of %s' % (self.bank_acb.auto_rate_last_sync, date))
            rate_usd = self._get_currency_rate(date, self.currency_usd)
            self.assertEqual(rate_usd.name, date, 'ACB: Last sync date %s instead of %s' % (rate_usd.name, date))
        except:
            self.assertFalse(self._get_currency_rate(date, self.currency_usd))
    
    def test_dynamic_method_availability(self):
        self.assertTrue(hasattr(self.env['res.bank'], '_acb_sync_currency_rate'), "The method `_acb_sync_currency_rate()` is not implemented yet.")

    def test_10_acb_configuration(self):
        self.assertEqual(self.bank_acb.auto_rate_update_provider, 'acb', 'ACB: Service provider %s instead of acb' % self.bank_acb.auto_rate_update_provider)

    @mute_logger('odoo.addons.viin_auto_currency_rate.models.res_bank')
    def test_20_acb_cron_currency_rate_sync(self):
        date = fields.Date.today()
        self._test_acb_cron_currency_rate_sync(date)

    @patch('odoo.addons.viin_auto_currency_rate_acb.models.res_bank.fields')
    @patch('odoo.addons.viin_auto_currency_rate.models.res_bank.fields')
    def test_30_acb_cron_past_day_currency_rate(self, mock_obj1, mock_obj2):
        mock_obj1.Date.today.return_value = date(2021, 5, 20)
        mock_obj2.Date.today.return_value = date(2021, 5, 20)
        mock_obj2.Date.today.strftime('%d/%m/%Y').return_value = '20/05/2021'
        
        self._test_acb_cron_currency_rate_sync(date(2021, 5, 20))
    
    @patch('odoo.addons.viin_auto_currency_rate_acb.models.res_bank.fields')
    @patch('odoo.addons.viin_auto_currency_rate.models.res_bank.fields')
    def test_40_acb_cron_future_day_currency_rate(self, mock_obj1, mock_obj2):
        date = fields.Date.today() + relativedelta(days=+1, weekday=calendar.FRIDAY)
        mock_obj1.Date.today.return_value = date
        mock_obj1.Datetime.today.return_value = fields.Datetime.to_datetime(date)
        mock_obj2.Date.today.return_value = date
        mock_obj2.Date.today.strftime('%d/%m/%Y').return_value = date.strftime('%d/%m/%Y')
        
        rate_usd = self._get_currency_rate(date, self.currency_usd)
        self.assertNotEqual(rate_usd.name, date, 'ACB: Rate date %s instead of False' % rate_usd.name)
        
        message = 'ERROR:odoo.addons.viin_auto_currency_rate.models.res_bank:Auto Currency Rates Update Service Provider "%s" failed to obtain data since %s.' \
            % (self.bank_acb.auto_rate_update_provider, date)
        logger = 'odoo.addons.viin_auto_currency_rate.models.res_bank'
        with self.assertLogs(logger, level='ERROR') as e:
            self.bank_acb._cron_currency_rate_sync()
            self.assertTrue(any(message in msg for msg in e.output))
            
            rate_usd = self._get_currency_rate(date, self.currency_usd)
            self.assertFalse(rate_usd)

    @mute_logger('odoo.addons.viin_auto_currency_rate.models.res_bank')
    def test_50_cron_currency_rate_not_active(self):
        date = fields.Date.today()
        self.currency_usd.active = False
        currency_idr = self.env.ref('base.IDR')
        self.bank_acb._cron_currency_rate_sync()
        
        self.assertFalse(self._get_currency_rate(date, self.currency_usd))
        self.assertFalse(self._get_currency_rate(date, currency_idr))
    
    def test_60_cron_currency_rate_bank_not_support(self):
        date = fields.Date.today()
        self.bank_acb.write({
            'auto_rate_update': False,
            'auto_rate_update_provider': '',})
        self.bank_acb._cron_currency_rate_sync()
        self.assertNotEqual(self.bank_acb.auto_rate_last_sync, date, 'ACB: Last sync date %s instead of %s' % (self.bank_acb.auto_rate_last_sync, date))
        self.assertFalse(self._get_currency_rate(date, self.currency_usd).filtered(lambda b: b.bank_id == self.bank_acb.id))

    @mute_logger('odoo.addons.viin_auto_currency_rate.models.res_bank')
    def test_70_cron_currency_rate_exist(self):
        date = fields.Date.today()
        self.env['res.currency.rate'].create({
            'name': date,
            'exchange_type': 'buy_rate',
            'rate': 999,
            'currency_id': self.currency_usd.id
            })
        self.bank_acb._cron_currency_rate_sync()
        
        transfer_rate_usd = self._get_currency_rate(date, self.currency_usd).filtered(lambda c: c.exchange_type == 'transfer_rate')
        self.assertFalse(transfer_rate_usd)
        
        sell_rate_usd = self._get_currency_rate(date, self.currency_usd).filtered(lambda c: c.exchange_type == 'sell_rate')
        self.assertFalse(sell_rate_usd)

    @mute_logger('odoo.addons.viin_auto_currency_rate.models.res_bank')
    def test_80_cron_curency_rate_multi_banks(self):
        date = fields.Date.today()
        self.env['res.bank'].create([
            {
            'name': 'ACB Bank Test 2',
            'auto_rate_update': True,
            'auto_rate_update_provider': 'acb',
            },
            {
            'name': 'ACB Bank Test 3',
            'auto_rate_update': True,
            'auto_rate_update_provider': 'acb',
            }])
        banks = self.env['res.bank'].search([
            ('auto_rate_update', '=', True), 
            ('auto_rate_update_provider', '=', 'acb'), 
            ('auto_rate_last_sync', '!=', date)])
        try:
            self.bank_acb._cron_currency_rate_sync()
            rates_usd = self.env['res.currency.rate'].search(self._prepare_domain_get_currency_rate(date, self.currency_usd))
            
            buy_rates_usd = rates_usd.filtered(lambda r: r.exchange_type == 'buy_rate')
            self.assertEqual(len(buy_rates_usd), len(banks))
            
            transfer_rates_usd = rates_usd.filtered(lambda r: r.exchange_type == 'transfer_rate')
            self.assertEqual(len(transfer_rates_usd), len(banks))
            
            sell_rates_usd = rates_usd.filtered(lambda r: r.exchange_type == 'sell_rate')
            self.assertEqual(len(sell_rates_usd), len(banks))
        except:
            self.assertFalse(self._get_currency_rate(date, self.currency_usd))

    @mute_logger('odoo.addons.viin_auto_currency_rate.models.res_bank')
    def test_90_acb_cron_currency_rate_last_3_days_to_sync(self):
        date = fields.Date.today()

        self.env['res.currency.rate'].search([
            ('name', '>=', date - timedelta(days=3)),
            ('bank_id', '=', self.bank_acb.id)
            ]).unlink()
        self.env['res.currency.rate'].create({
            'name': date - timedelta(days=3),
            'exchange_type': 'buy_rate',
            'rate': 999,
            'currency_id': self.currency_usd.id,
            'bank_id': self.bank_acb.id,
            })

        self._test_acb_cron_currency_rate_sync(date)
