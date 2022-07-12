import requests
import logging

from datetime import timedelta
from lxml import html, etree

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ResBank(models.Model):
    _inherit = 'res.bank'

    auto_rate_last_sync = fields.Date(string='Last Synchronization Date', readonly=True)

    def _get_data_from_service_provider(self, url, parser='xml'):
        self.ensure_one()
        res = requests.get(url)
        res.encoding = 'utf-8'

        if parser == 'xml':
            return etree.fromstring(res.text)
        elif parser == 'html':
            return html.fromstring(res.content)
        return False

    def _prepare_raw_data(self, rates, date, source_currency_id, to_currency_id):
        """
        This method to prepare input data for _parse_raw_data method
        :param rates list of currency rates
            [
                {
                    'exchange_type': exchange_type,
                    'inverse_rate': inverse_rate,
                },
                {
                    'exchange_type': exchange_type,
                    'inverse_rate': inverse_rate,
                },
            ]
        :return list of values for passing into _parse_raw_data method
        """
        self.ensure_one()
        for rate in rates:
            rate.update({
                'date': date,
                'source_currency': source_currency_id,
                'to_currency': to_currency_id,
                })
        return rates

    def _parse_raw_data(self, rates_data):
        """
        This method to process input data before passing self.env ['res.currency.rate'].create(vals_list)
        :param rates_data list of currency rates
            [
                {
                    'date': date,
                    'source_currency': source_currency_id,
                    'to_currency': to_currency_id,
                    'inverse_rate': inverse_rate,
                    'exchange_type': exchange_type,
                },
                {
                    'date': date,
                    'source_currency': source_currency_id,
                    'to_currency': to_currency_id,
                    'inverse_rate: inverse_rate,
                    'exchange_type': exchange_type,
                },
            ]
        """
        self.ensure_one()

        vals_list = []
        for company in self.env['res.company'].search([]):
            # The case that a company uses Euro, USD but does not have VND,
            # while the exchange rate is only USD/VND, EURO/VND,
            # that is to convert through an intermediary VND."""
            inter_rate = False
            for rate in rates_data:
                if rate['to_currency'] == company.currency_id.id:
                    if not rate['inverse_rate']:
                        continue
                    inter_rate = float(rate['inverse_rate'])
                    break

            for rate in rates_data:
                if not rate['inverse_rate']:
                    continue
                inverse_rate = float(rate['inverse_rate'])
                vals = {
                    'name': rate['date'],
                    'company_id': company.id,
                    'currency_id': rate['to_currency'],
                    'bank_id': self.id,
                    'exchange_type': rate['exchange_type'],
                    'inverse_rate': inverse_rate,
                    }
                if company.currency_id.id == rate['to_currency']:
                    vals.update({
                        'currency_id': rate['source_currency'],
                        'inverse_rate': 1.0 / inverse_rate,
                        })
                # that is to convert through an intermediary rate.
                elif inter_rate:
                    vals.update({
                        'inverse_rate': inverse_rate / inter_rate,
                        })
                vals_list.append(vals)
        return vals_list

    def _prepare_currency_rate_sync_vals_list(self, rate_date=False):
        """
        This method dynamically calls the custom method `'_%s_sync_currency_rate' % service_provider_name`
        to retrieve the provider specific currency rate values list for passing into the currency rate creation method,
        e.g. self.env['res.currency.rate'].with_context(force_company=r.id).create(rates_vals_list)
        For each extending module for a specific currency rate provider, please do NOT forget to implement the
        method `'_%s_sync_currency_rate' % service_provider_name`

        :return list of values for passing into currency rate creation method
        :rtype: [{'field1': val1, 'field2': val2}, {'field1': val3, 'field2': val4},...]
        """
        self.ensure_one()
        rate_date = rate_date or fields.Date.today()
        rates_vals_list = []
        service_provider = self.auto_rate_update_provider
        currency_rate_update_method_name = '_%s_sync_currency_rate' % service_provider
        if hasattr(self, currency_rate_update_method_name):
            try:
                rates_vals_list.extend(getattr(self, currency_rate_update_method_name)(rate_date=rate_date))
            except Exception as e:
                _logger.error(_('Auto Currency Rates Update Service Provider "%s" failed to obtain data since %s. '
                                   'Here is the debugging information:\n%s') % (service_provider, rate_date, str(e)))
        return rates_vals_list

    def _sync_currency_rate(self):
        self.write({'auto_rate_last_sync': fields.Date.today()})
        Rate = self.env['res.currency.rate']

        rates_vals_list = []
        for r in self:
            last_rate = Rate.search([('bank_id', '=', r.id)], limit=1)
            if last_rate:
                days_to_get_rate = (fields.Date.today() - last_rate.name).days
            else:
                days_to_get_rate = 1
            for i in range(0, days_to_get_rate):
                currency_rate_date = fields.Date.today() - timedelta(days=i)
                rates_vals_list.extend(r._prepare_currency_rate_sync_vals_list(rate_date=currency_rate_date))
        if rates_vals_list:
            Rate.create(rates_vals_list)

    @api.model
    def _cron_currency_rate_sync(self):
        banks = self.env['res.bank'].search([('auto_rate_update', '=', True)])
        banks._sync_currency_rate()
