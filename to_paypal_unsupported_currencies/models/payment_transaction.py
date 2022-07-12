import json

from odoo import models, api
from odoo.tools import float_compare


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _paypal_form_get_invalid_parameters(self, data):
        """
        This method modifies the mc_gross and mc_currency (mc_gross is amount + fees)
        to its original values they were before being converted to a Paypal accepted currency
        Without this, mc_gross and mc_currency will be considered as invalid. For example,

        Invoice is 23000 VND and this amount was converted to US$100 for Paypal payment processing.
        When Paypal notifies Odoo, it returns mc_gross and mc_currency as $100 and USD correspondingly.
        After that, Odoo would compare mc_gross and mc_currency with 23000 and VND correspondingly, then this will simply failed.
        """
        invalid_conversion_paramters = []
        if self.converted_currency_id and self.converted_amount:
            expected_amount = self.converted_amount + self.converted_fee
            if float_compare(float(data.get('mc_gross', '0.0')), expected_amount, 2):
                invalid_conversion_paramters.append(('mc_gross', data.get('mc_gross'), expected_amount))

        custom = data['custom']
        if 'unsupported_currency_code' in custom and 'unsupported_currency_amount' in custom:
            # convert custom from json string to dict
            custom = json.loads(custom)

            # then modify the mc_gross and mc_currency to the values they were before conversion for Paypal
            data.update({
                'mc_gross': custom['unsupported_currency_amount'],
                'mc_currency': custom['unsupported_currency_code']
                })

        invalid_paramters = super(PaymentTransaction, self)._paypal_form_get_invalid_parameters(data)
        return invalid_conversion_paramters + invalid_paramters
