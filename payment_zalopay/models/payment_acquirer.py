import hmac
import hashlib
import json
import logging

from odoo import models, fields, api
from odoo.tools.float_utils import float_round

from ..controllers.main import ZALOPAY_PAYMENT_PROCESS_ROUTE

_logger = logging.getLogger(__name__)

ZALOPAY_SUPPORTED_CURRENCIES = [
    'VND', #Vietnam Dong [1]
    # [1] This currency does not support decimals. If you pass a decimal amount, an error occurs.
    ]

class PaymentAcquirerZaloPay(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _default_currency(self):
        if ZALOPAY_SUPPORTED_CURRENCIES:
            return self.env.ref('base.VND', raise_if_not_found=False) or self.env['res.currency'].with_context(active_test=False).search([('name', 'in', ZALOPAY_SUPPORTED_CURRENCIES)], limit=1)
        else:
            return super(PaymentAcquirerZaloPay, self)._default_currency()

    provider = fields.Selection(selection_add=[('zalopay', 'ZaloPay')], ondelete={'zalopay': 'set default'})
    zalopay_appid = fields.Integer('ZaloPay App ID', groups="base.group_user", help="A positive integer, the identifier for the application during checkout with the ZaloPay system.")
    zalopay_key1 = fields.Char('Secret Key 1', groups="base.group_user", help="The secret key used to generate authentication data for the order.")
    zalopay_key2 = fields.Char('Secret Key 2', groups="base.group_user", help="The secret key used to authenticate data sent by ZaloPayServer via AppServer at callback.")

    # Default ZaloPay fees
    fees_dom_fixed = fields.Float(default=0.0)
    fees_dom_var = fields.Float(default=0.0)
    fees_int_fixed = fields.Float(default=0.0)
    fees_int_var = fields.Float(default=0.0)

    def _get_feature_support(self):
        """Get advanced feature support by acquirer.
        """
        res = super(PaymentAcquirerZaloPay, self)._get_feature_support()
        res['fees'].append('zalopay')
        return res

    def _get_zalopay_urls(self, environment):
        """ZaloPay urls"""
        if environment == 'prod':
            return {
                'zalopay_checkout_url_large_payload': 'https://zalopay.com.vn/v001/tpe/createorder',
                'zalopay_get_status_by_apptransid': 'https://zalopay.com.vn/v001/tpe/getstatusbyapptransid',
                }
        else:
            return {
                'zalopay_checkout_url_large_payload': 'https://sandbox.zalopay.com.vn/v001/tpe/createorder',
                'zalopay_get_status_by_apptransid': 'https://sandbox.zalopay.com.vn/v001/tpe/getstatusbyapptransid',
                }

    def zalopay_compute_fees(self, amount, currency_id, country_id):
        """Compute ZaloPay fees."""
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount) + fixed / (1 - percentage / 100.0)
        return float_round(fees, precision_digits=0)

    def zalopay_form_generate_values(self, values):
        """Method that generates the values used to render the form button template."""
        # Original currency
        amount = values.get('amount')
        fees = values.get('fees', 0)

        zalopay_tx_values = dict(values)
        original_currency = self.env['res.currency'].search([('id', '=', zalopay_tx_values['currency_id'])], limit=1)
        custom = {'serverinfo':'odoo'}

        # if the currency is not accepted by ZaloPay and there is an accepted currency defined for the ZaloPay acquirer
        if original_currency not in self.supported_currency_ids and self.default_converted_currency_id:
            # convert the amount in the original currency to the pre-configured currency supported by ZaloPay
            amount = int(original_currency._convert(amount,
                                                    self.default_converted_currency_id,
                                                    self.company_id, fields.Date.today()))
            fees = int(original_currency._convert(fees,
                                                  self.default_converted_currency_id,
                                                  self.company_id, fields.Date.today()))

            # modify the value of the custom key of the zalopay_tx_values
            custom.update({
                'unsupported_currency_amount': zalopay_tx_values['amount'],
                'unsupported_currency_code': original_currency.name,
                })

        date_now = fields.Date.to_string(fields.Date.today())
        date_now = date_now[2:4] + date_now[5:7] + date_now[8:]

        # transaction code (yymmdd_ordercode)
        apptransid = '%s_%s' % (date_now, values.get('reference').replace('/', '.'))
        # id/username/name/phone/email of user
        appuser = '%s/%s/%s/%s/%s' % (
                values.get('billing_partner_id'),
                values.get('billing_partner_email'),
                values.get('billing_partner_first_name'),
                values.get('billing_partner_phone'),
                values.get('billing_partner_email'))

        # time create order (unix timestamp in milisecond)
        apptime = int(fields.Datetime.now().timestamp() * 1000)
        embeddata = json.dumps(custom)
        item = json.dumps([{"itemid":values.get('reference'), "itemprice":int(amount), "fee_shipping":int(fees), "itemquantity":1}])

        # appid +”|”+ apptransid +”|”+ appuser +”|”+ amount +"|" + apptime +”|”+ embeddata +"|" +item
        msg = '%s|%s|%s|%s|%s|%s|%s' % (self.zalopay_appid, apptransid, appuser, int(amount + fees), apptime, embeddata, item)

        mac = hmac.new(
            str(self.zalopay_key1).encode(),
            str(msg).encode(),
            hashlib.sha256
        ).hexdigest()

        zalopay_tx_values.update({
            'appid': self.zalopay_appid,
            'appuser': appuser,
            'apptime': apptime,
            'amount': int(amount + fees),
            'apptransid': apptransid,
            'embeddata': embeddata,
            'item': item,
            'description': '%s %s (%s) pays order #%s' % (
                values.get('billing_partner_first_name'),
                values.get('billing_partner_last_name'),
                values.get('billing_partner_email'),
                values.get('reference')
                 ),
            'mac': mac,
            'bankcode': 'zalopayapp',
        })
        return zalopay_tx_values

    def zalopay_get_form_action_url(self):
        """Method that returns the url of the button form."""
        self.ensure_one()
        return ZALOPAY_PAYMENT_PROCESS_ROUTE

    @api.model
    def _fill_zalopay_supported_currencies(self):
        """
        To be called by post_init_hook to fill supprted currencies for ZaloPay Acquirer
        """
        currency_map_vals_list = []

        supported_currencies = self.env['res.currency'].with_context(active_test=False).search([('name', 'in', ZALOPAY_SUPPORTED_CURRENCIES)])
        for acquirer in self.search([('provider', '=', 'zalopay')]):
            currency_map_vals_list += [{'acquirer_id': acquirer.id, 'currency_id': currency.id} for currency in supported_currencies
                                       if currency not in acquirer.supported_currency_map_ids.currency_id]
        if currency_map_vals_list:
            return self.env['payment.acquirer.supported.currency.map'].create(currency_map_vals_list)
        return self.env['payment.acquirer.supported.currency.map']
