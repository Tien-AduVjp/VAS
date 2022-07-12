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
        self.ensure_one()

        vnd_id = self.env.ref('base.VND').id
        currencies = self.env['res.currency'].search([('name', 'in', VCB_SUPPORTED_CURRENCIES)])

        dom = self._get_data_from_service_provider('https://portal.vietcombank.com.vn/UserControls/TVPortal.TyGia/pListTyGia.aspx?txttungay=%s'%rate_date.strftime("%d/%m/%y"), parser='html')

        raw_data = []
        exrates = dom.xpath("//tr[@class='odd']")
        for currency in currencies:
            for exrate in exrates:
                if exrate[1].text == currency.name:
                    rates = [
                        {
                            'exchange_type': 'buy_rate',
                            'inverse_rate': float(exrate[2].text.replace(',',''))
                            },
                        {
                            'exchange_type': 'transfer_rate',
                            'inverse_rate': float(exrate[3].text.replace(',',''))
                            },
                        {
                            'exchange_type': 'sell_rate',
                            'inverse_rate': float(exrate[4].text.replace(',',''))
                            }
                        ]

                    raw_data.extend(self._prepare_raw_data(rates, rate_date, vnd_id, currency.id))
                    exrates.remove(exrate)
        return self._parse_raw_data(raw_data)
