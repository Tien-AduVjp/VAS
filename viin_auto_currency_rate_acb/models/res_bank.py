import requests
from lxml import html

from odoo import fields, models

ACB_SUPPORTED_CURRENCIES = [
    'IDR',
    'NZD',
    'TWD',
    'THB',
    'HKD',
    'CAD',
    'SGD',
    'AUD',
    'GBP',
    'CHF',
    'EUR',
    'JPY',
    'USD',
    ]


class ResBank(models.Model):
    _inherit = 'res.bank'

    auto_rate_update_provider = fields.Selection(selection_add=[('acb', 'Asia Commercial Bank')])

    def _acb_sync_currency_rate(self, rate_date=False):
        self.ensure_one()
        rate_date = rate_date or fields.Date.today()
        vnd_id = self.env.ref('base.VND').id
        currencies = self.env['res.currency'].search([('name', 'in', ACB_SUPPORTED_CURRENCIES)])

        url = 'https://www.acb.com.vn/ACBComponent/jsp/html/en/exchange/getlan.jsp?txtngaynt=%s&cmd=EXCHANGE' % rate_date.strftime('%d/%m/%Y')
        res = requests.get(url)
        doc = html.fromstring(res.content)
        lannt = max(map(int, doc.xpath('//option/text()')))

        url = 'https://www.acb.com.vn/ACBComponent/jsp/html/en/exchange/getlisttygia.jsp?txtngaynt=%s&lannt=%s' % (rate_date.strftime('%d/%m/%Y'), lannt)

        dom = self._get_data_from_service_provider(url, parser='html')

        exrates = dom.xpath('//div[@class="wrap-content-search-small"]/table/tr')
        exrates.pop()

        raw_data = []
        for currency in currencies:
            for exrate in exrates:

                data = exrate.getchildren()[1].getchildren()
                name = data[0].text_content().strip()
                if name == 'USD(50,100)':
                    name = 'USD'
                elif name == 'TWD (TaiwanDollar)':
                    name = 'TWD'
                elif name == 'Indo Rupi':
                    name = 'IDR'
                if name == currency.name:
                    values = data[1].getchildren()
                    rates = [
                        {
                            'exchange_type': 'buy_rate',
                            'inverse_rate': values[0].getchildren()[1].text_content().replace(',', '')
                            },
                        {
                            'exchange_type': 'transfer_rate',
                            'inverse_rate': values[1].getchildren()[1].text_content().replace(',', '')
                            },
                        {
                            'exchange_type': 'sell_rate',
                            'inverse_rate': values[3].getchildren()[1].text_content().replace(',', '')
                            }
                        ]

                    raw_data.extend(self._prepare_raw_data(rates, rate_date, vnd_id, currency.id))
                    exrates.remove(exrate)
        return self._parse_raw_data(raw_data)
