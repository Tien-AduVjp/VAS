import hmac
import hashlib
import logging

from werkzeug import urls

from odoo import models, fields, api
from odoo.tools.float_utils import float_round

from ..controllers.main import MoMoController, MOMO_PAYMENT_PROCESS_ROUTE

_logger = logging.getLogger(__name__)

MOMO_SUPPORTED_CURRENCIES = [
    'VND',  # Vietnam Dong [1]
    # [1] This currency does not support decimals. If you pass a decimal amount, an error occurs.
    ]


class PaymentAcquirerMoMo(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _default_currency(self):
        if MOMO_SUPPORTED_CURRENCIES:
            return self.env.ref('base.VND', raise_if_not_found=False) or self.env['res.currency'].with_context(active_test=False).search([('name', 'in', MOMO_SUPPORTED_CURRENCIES)], limit=1)
        else:
            return super(PaymentAcquirerMoMo, self)._default_currency()

    provider = fields.Selection(selection_add=[('momo', 'MoMo')])
    momo_partner_code = fields.Char('MoMo Partner Code', required_if_provider='momo', groups='base.group_user',
                                    help='Information to identify a business account')
    momo_access_key = fields.Char('MoMo Access Key', required_if_provider='momo', groups='base.group_user',
                                    help='Grant access to the MoMo system')
    momo_secret_key = fields.Char('MoMo Secret Key', required_if_provider='momo', groups='base.group_user',
                                    help='Used to create digital signatures')
    
    # Default MoMo fees
    fees_dom_fixed = fields.Float(default=0.0)
    fees_dom_var = fields.Float(default=0.0)
    fees_int_fixed = fields.Float(default=0.0)
    fees_int_var = fields.Float(default=0.0)
    
    def _get_momo_urls(self, environment):
        if environment == 'prod':
            return {
                'momo_gw_url': 'https://payment.momo.vn/gw_payment/transactionProcessor',
                }
        else:
            return {
                'momo_gw_url': 'https://test-payment.momo.vn/gw_payment/transactionProcessor',
                }

    def _get_feature_support(self):
        """Get advanced feature support by acquirer."""
        res = super(PaymentAcquirerMoMo, self)._get_feature_support()
        res['fees'].append('momo')
        return res

    def momo_compute_fees(self, amount, currency_id, country_id):
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
        # round as NganLuong requires int or float with precision_digits=0
        return float_round(fees, precision_digits=0)
    
    def momo_form_generate_values(self, values):
        base_url = self.get_base_url()
        if base_url.find('https') == -1:
            base_url = base_url.replace('http', 'https')
        
        amount = values.get('amount', 0)
        fees = values.get('fees', 0)
        extra_data = {"serverinfo":"odoo", "itemid":values.get('reference', ''), "itemprice":amount, "fee_shipping":fees, "itemquantity":1}
        
        momo_tx_values = dict(values)
        
        original_currency = self.env['res.currency'].search([('id', '=', momo_tx_values['currency_id'])], limit=1)
        
        # if the currency is not accepted by MoMo and there is an accepted currency defined for the MoMo acquirer
        if original_currency not in self.supported_currency_ids and self.default_converted_currency_id:
            # convert the amount in the original currency to the pre-configured currency supported by MoMo
            amount = int(original_currency._convert(amount,
                                                    self.default_converted_currency_id,
                                                    self.company_id, fields.Date.today()))
            fees = int(original_currency._convert(fees,
                                                  self.default_converted_currency_id,
                                                  self.company_id, fields.Date.today()))
        
        order_id = values.get('reference', '').replace('/', '.')
        order_info = '%s %s (%s) pays order #%s' % (
                values.get('billing_partner_first_name', ''),
                values.get('billing_partner_last_name', ''),
                values.get('billing_partner_email', ''),
                values.get('reference', '')
                )
        return_url = urls.url_join(base_url, MoMoController._return_url)
        notify_url = urls.url_join(base_url, MoMoController._notify_url)
        # MM+time create order (unix timestamp)+orderId
        request_id = 'MM%s_%s' % (int(fields.Datetime.now().timestamp()), order_id)

        # partnerCode=$partnerCode&accessKey=$accessKey&requestId=$requestId
        # &amount=$amount&orderId=$orderId&orderInfo=$orderInfo&returnUrl=$returnUrl
        # &notifyUrl=$notifyUrl&extraData=$extraData
        msg = 'partnerCode=%s&accessKey=%s&requestId=%s&amount=%s&orderId=%s&orderInfo=%s&returnUrl=%s&notifyUrl=%s&extraData=%s' % (
            self.momo_partner_code, self.momo_access_key, request_id, int(amount + fees),
            order_id, order_info, return_url, notify_url, extra_data)
        
        momo_tx_values.update({
            'partnerCode': self.momo_partner_code,
            'accessKey': self.momo_access_key,
            'requestId': request_id,
            'amount': int(amount + fees),
            'orderId': order_id,
            'orderInfo': order_info,
            'returnUrl': return_url,
            'notifyUrl': notify_url,
            'requestType': 'captureMoMoWallet',
            'signature': hmac.new(
                            str(self.momo_secret_key).encode(),
                            str(msg).encode(),
                            hashlib.sha256
                            ).hexdigest(),
            'extraData': extra_data,
        })
        return momo_tx_values

    def momo_get_form_action_url(self):
        self.ensure_one()
        return MOMO_PAYMENT_PROCESS_ROUTE

    @api.model
    def _fill_momo_supported_currencies(self):
        """
        To be called by post_init_hook to fill supprted currencies for MoMo Acquirer
        """
        currency_map_vals_list = []

        supported_currencies = self.env['res.currency'].with_context(active_test=False).search([('name', 'in', MOMO_SUPPORTED_CURRENCIES)])
        for acquirer in self.search([('provider', '=', 'momo')]):
            currency_map_vals_list += [{'acquirer_id': acquirer.id, 'currency_id': currency.id} for currency in supported_currencies
                                        if currency not in acquirer.supported_currency_map_ids.currency_id]

        if currency_map_vals_list:
            return self.env['payment.acquirer.supported.currency.map'].create(currency_map_vals_list)
        return self.env['payment.acquirer.supported.currency.map']
