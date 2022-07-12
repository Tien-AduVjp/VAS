import logging
import hashlib
import hmac


from werkzeug import urls
from datetime import datetime
from urllib.parse import quote

from odoo import fields, models, api
from odoo.http import request
from odoo.tools.float_utils import float_round

from ..controllers.main import VnpayController, VNPAY_PAYMENT_PROCESS_ROUTE

_logger = logging.getLogger(__name__)

VNPAY_SUPPORTED_CURRENCIES = [
    'VND',  # Vietnam Dong [1]
    # [1] This currency does not support decimals. If you pass a decimal amount, an error occurs.
    ]


class PaymentAcquirerVNPay(models.Model):
    _inherit = 'payment.acquirer'

    @api.model
    def _default_currency(self):
        if VNPAY_SUPPORTED_CURRENCIES:
            return self.env.ref('base.VND', raise_if_not_found=False) or self.env['res.currency'].with_context(active_test=False).search([('name', 'in', VNPAY_SUPPORTED_CURRENCIES)], limit=1)
        else:
            return super(PaymentAcquirerVNPay, self)._default_currency()

    provider = fields.Selection(selection_add=[('vnpay', 'VNPay')], ondelete={'vnpay': 'set default'})
    vnpay_tmn_code = fields.Char('VNPay Website Code', required_if_provider='VNPay', groups='base.group_user', help="The Website Code provided by VNPay")
    vnpay_hash_secret = fields.Char('VNPay Hash Secret', required_if_provider='VNPay', groups='base.group_user', help="The Hash Secret provided by VNPay")
    vnpay_payment_url = fields.Char('VNPay Payment Url', required_if_provider='VNPay', groups='base.group_user', default='http://sandbox.vnpayment.vn/paymentv2/vpcpay.html')

    # Default VNPay fees
    fees_dom_fixed = fields.Float(default=0.0)
    fees_dom_var = fields.Float(default=0.0)
    fees_int_fixed = fields.Float(default=0.0)
    fees_int_var = fields.Float(default=0.0)

    def _get_feature_support(self):
        """Get advanced feature support by acquirer."""
        res = super(PaymentAcquirerVNPay, self)._get_feature_support()
        res['fees'].append('vnpay')
        return res

    def vnpay_compute_fees(self, amount, currency_id, country_id):
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

    def _get_real_ip(self):
        return request.httprequest.environ.get('HTTP_X_REAL_IP', request.httprequest.remote_addr)

    def vnpay_form_generate_values(self, values):
        base_url = self.get_base_url()
        lang = values.get('partner_lang', 'en').lower()
        if lang[:2] == 'vi':
            lang = 'vn'
        else:
            lang = 'en'

        ipaddr = self._get_real_ip()
        amount = values.get('amount')
        fees = values.get('fees')
        vnpay_tx_values = dict(values)
        original_currency = self.env['res.currency'].search([('id', '=', vnpay_tx_values['currency_id'])], limit=1)

        # if the currency is not accepted by VNPay and there is an accepted currency defined for the VNPay acquirer
        if original_currency not in self.supported_currency_ids and self.default_converted_currency_id:
            # convert the amount in the original currency to the pre-configured currency supported by VNPay
            amount = int(original_currency._convert(amount,
                                                    self.default_converted_currency_id,
                                                    self.company_id, fields.Date.today()))
            fees = int(original_currency._convert(fees,
                                                  self.default_converted_currency_id,
                                                  self.company_id, fields.Date.today()))

        order_info = 'viindoo'
        vnp_amount = int((amount + fees) * 100)
        vnp_create_date = int(datetime.now().strftime('%Y%m%d%H%M%S'))
        vnp_order_type = 'other'
        vnp_return_url = urls.url_join(base_url, VnpayController._return_url)
        vnp_command = 'pay'
        vnp_curr_code = 'VND'
        vnp_version = '2.1.0'
        msg = 'vnp_Amount=%s&vnp_Command=%s&vnp_CreateDate=%s&vnp_CurrCode=%s&vnp_IpAddr=%s&vnp_Locale=%s&vnp_OrderInfo=%s&vnp_OrderType=%s&vnp_ReturnUrl=%s&vnp_TmnCode=%s&vnp_TxnRef=%s&vnp_Version=%s' % (
            vnp_amount, vnp_command, vnp_create_date, vnp_curr_code, ipaddr, lang, order_info,
            vnp_order_type, quote(vnp_return_url, safe=''), self.vnpay_tmn_code, quote(values.get('reference'), safe=''), vnp_version)

        vnpay_tx_values.update({
            'vnp_Amount': vnp_amount,
            'vnp_Command': vnp_command,
            'vnp_CreateDate': vnp_create_date,
            'vnp_CurrCode': vnp_curr_code,
            'vnp_IpAddr': ipaddr,
            'vnp_Locale': lang,
            'vnp_OrderInfo': order_info,
            'vnp_OrderType': vnp_order_type,
            'vnp_ReturnUrl': vnp_return_url,
            'vnp_TmnCode': self.vnpay_tmn_code,
            'vnp_TxnRef': values.get('reference'),
            'vnp_Version': vnp_version,
            'vnp_SecureHash': hmac.new(str(self.vnpay_hash_secret).encode(),
                                           str(msg).encode(),
                                           hashlib.sha512).hexdigest(),
            })
        return vnpay_tx_values

    def vnpay_get_form_action_url(self):
        return VNPAY_PAYMENT_PROCESS_ROUTE

    @api.model
    def _fill_vnpay_supported_currencies(self):
        """
        To be called by post_init_hook to fill supprted currencies for VNPay Acquirer
        """
        supported_currencies = self.env['res.currency'].with_context(active_test=False).search([('name', 'in', VNPAY_SUPPORTED_CURRENCIES)])
        currency_map_vals_list = []
        for acquirer in self.search([('provider', '=', 'vnpay')]):
            currency_map_vals_list += [{'acquirer_id': acquirer.id, 'currency_id': currency.id} for currency in supported_currencies
                                        if currency not in acquirer.supported_currency_map_ids.currency_id]

        if currency_map_vals_list:
            return self.env['payment.acquirer.supported.currency.map'].create(currency_map_vals_list)
        return self.env['payment.acquirer.supported.currency.map']
