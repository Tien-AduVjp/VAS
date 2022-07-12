import logging
from datetime import datetime

from odoo import fields, models


_logger = logging.getLogger(__name__)

VCB_SUPPORTED_CURRENCIES = [
    'AUD',
    'CAD',
    'CHF',
    'CNY',
    'DKK',
    'EUR',
    'GBP',
    'HKD',
    'INR',
    'JPY',
    'KRW',
    'KWD',
    'MYR',
    'NOK',
    'RUB',
    'SAR',
    'SEK',
    'SGD',
    'THB',
    'USD',
    ]

class ResBank(models.Model):
    _inherit = 'res.bank'

    auto_rate_update_provider = fields.Selection(selection_add=[('vcb', 'Vietcombank')])

    def _vcb_sync_currency_rate(self, rate_date=False):
        # TODOS: with the current code, it is not possible to get the rate by day
        # improve this method in odoo 14 to allow to get the rate by day
        self.ensure_one()
        
        vnd_id = self.env.ref('base.VND').id
        currencies = self.env['res.currency'].search([('name', 'in', VCB_SUPPORTED_CURRENCIES)])
        
        dom = self._get_data_from_service_provider('https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx', parser='xml')
        
        rate_date = datetime.strptime(dom.xpath('//DateTime/text()')[0], '%m/%d/%Y %I:%M:%S %p')
        rate_date = fields.Date.to_date(rate_date)
        
        raw_data = []
        exrates = dom.xpath('//Exrate')
        for currency in currencies:
            for exrate in exrates:
                if exrate.get('CurrencyCode') == currency.name:
                    rates = [
                        {
                            'exchange_type': 'buy_rate',
                            'inverse_rate': exrate.get('Buy').replace(',', '')
                            },
                        {
                            'exchange_type': 'transfer_rate',
                            'inverse_rate': exrate.get('Transfer').replace(',', '')
                            },
                        {
                            'exchange_type': 'sell_rate',
                            'inverse_rate': exrate.get('Sell').replace(',', '')
                            }
                        ]
                    
                    raw_data.extend(self._prepare_raw_data(rates, rate_date, vnd_id, currency.id))
                    exrates.remove(exrate)
        return self._parse_raw_data(raw_data)
