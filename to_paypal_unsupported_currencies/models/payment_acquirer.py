import json

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

PAYPAL_SUPPORTED_CURRENCIES = [
    'AUD',  # Australian dollar
    'BRL',  # Brazilian real, [2]
    'CAD',  # Canadian dollar
    'CZK',  # Czech koruna
    'DKK',  # Danish krone
    'EUR',  # Euro
    'HKD',  # Hong Kong dollar
    'HUF',  # Hungarian forint [1]
    'INR',  # Indian rupee [3]
    'ILS',  # Israeli new shekel
    'JPY',  # Japanese yen [1]
    'MYR',  # Malaysian ringgit [2]
    'MXN',  # Mexican peso
    'TWD',  # New Taiwan dollar [1]
    'NZD',  # New Zealand dollar
    'NOK',  # Norwegian krone
    'PHP',  # Philippine peso
    'PLN',  # Polish złoty
    'GBP',  # Pound sterling
    'RUB',  # Russian ruble
    'SGD',  # Singapore dollar
    'SEK',  # Swedish krona
    'CHF',  # Swiss franc
    'THB',  # Thai baht
    'USD',  # United States dollar
    # [1] This currency does not support decimals. If you pass a decimal amount, an error occurs.
    # [2] This currency is supported as a payment currency and a currency balance for in-country PayPal accounts only.
    # [3] This currency is supported as a payment currency and a currency balance for in-country PayPal India accounts only.
    ]


class AcquirerPaypal(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _default_paypal_currency(self):
        return self.env.ref('base.USD', raise_if_not_found=False) or self.env['res.currency'].with_context(active_test=False).search([('name', '=', 'USD')], limit=1)

    def paypal_form_generate_values(self, values):
        """
        This override is to customize transaction values send to Paypal
        """
        paypal_tx_values = super(AcquirerPaypal, self).paypal_form_generate_values(values)

        # if the currency is not accepted by Paypal and there is an accepted currency defined for the paypal acquirer
        if paypal_tx_values['currency_code'] not in self.supported_currency_ids.mapped('name') and self.default_converted_currency_id:
            # modify the value of the custom key of the paypal_tx_values
            custom = paypal_tx_values.get('custom', '{}')
            custom = json.loads(custom)
            custom.update({
                'unsupported_currency_amount': paypal_tx_values['amount'],
                'unsupported_currency_code': paypal_tx_values['currency_code'],
                })

            # modify the paypal_tx_values with the predefined currency that is accepted by Paypal and the newly converted amount in that currency,
            # plus custom data that include the original unsuppoted currency and amount in that currency
            paypal_tx_values.update({
                'amount': paypal_tx_values.get('converted_amount', paypal_tx_values['amount']),
                'currency_code': self.default_converted_currency_id.name,
                'custom': json.dumps(custom),
                })
        return paypal_tx_values

    @api.model
    def fill_paypal_supported_currencies(self):
        """
        To be called by post_init_hook to fill supprted currencies for Paypal Acquirer
        """
        supported_currencies = self.env['res.currency'].with_context(active_test=False).search([('name', 'in', PAYPAL_SUPPORTED_CURRENCIES)])
        for acquirer in self.search([('provider', '=', 'paypal')]):
            currency_map_vals_list = [{'acquirer_id': acquirer.id, 'currency_id': currency.id} for currency in supported_currencies
                                      if currency not in acquirer.supported_currency_map_ids.currency_id]
            self.env['payment.acquirer.supported.currency.map'].create(currency_map_vals_list)

