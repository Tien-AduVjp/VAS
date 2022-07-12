import logging

from werkzeug import urls

from odoo import api, fields, models

from ..controllers.main import NganLuongController, NGANLUONG_STANDARD_PAYMENT_PROCESS_ROUTE
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)

NGANLUONG_SUPPORTED_CURRENCIES = [
    'USD',  # United States dollar
    'VND',  # VietNam dong
    ]


class AcquirerNganLuong(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('nganluong', 'NganLuong')], ondelete={'nganluong': 'set default'})
    nganluong_merchant_site_code = fields.Char('NganLuong Merchant ID', groups='base.group_user',
                                                  help="The Merchant Site Code provided by NganLuong")
    nganluong_merchant_password = fields.Char('NganLuong Merchant Password', groups='base.group_user', help="Provided by Ngan Luong")
    nganluong_receiver_email = fields.Char(string="NganLuong Receiver Email", groups='base.group_user')
    nganluong_accept_detained_payment = fields.Boolean(string='Accept Detained Payments',
                                                       help="If checked, the payment transactions detained by NganLuong will always be accepted as valid."
                                                       " Otherwise, Odoo will mark the transaction as pending. In such case, a scheduled action will regularly"
                                                       " query NganLuong and turn the transaction into done when it found the transaction is released by NganLuong")
    fees_dom_fixed = fields.Float(default=0.0)
    fees_dom_var = fields.Float(default=0.0)
    fees_int_fixed = fields.Float(default=0.0)
    fees_int_var = fields.Float(default=0.0)

    def _get_nganluong_urls(self):
        if self.state == 'enabled':
            return 'https://www.nganluong.vn/checkout.php'
        else:
            return 'https://sandbox.nganluong.vn:8088/nl35/checkout.php'

    def _get_nganluong_order_check_url(self):
        if self.state == 'enabled':
            return 'https://www.nganluong.vn/service/order/checkV2'
        else:
            return 'https://sandbox.nganluong.vn:8088/nl35/service/order/checkV2'

    def _get_feature_support(self):
        res = super(AcquirerNganLuong, self)._get_feature_support()
        res['fees'].append('nganluong')
        return res

    def nganluong_compute_fees(self, amount, currency_id, country_id):
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

    def nganluong_form_generate_values(self, values):
        base_url = self.get_base_url()
        lang = values.get('partner_lang', 'en').lower()
        if lang[:2] == 'vi':
            lang = 'vi'
        else:
            lang = 'en'

        currency = values.get('currency').name.lower()
        original_currency = self.env['res.currency'].search([('id', '=', values['currency_id'])], limit=1)
        amount = values.get('amount', 0)
        fees = values.get('fees', 0)

        # if the currency is not accepted by NganLuong and there is an accepted currency defined for the NganLuong acquirer
        if original_currency and original_currency.name not in NGANLUONG_SUPPORTED_CURRENCIES and self.default_converted_currency_id:
            # convert the amount in the original currency to the pre-configured currency supported by NganLuong
            amount = values.get('converted_amount', 0)
            fees = values.get('converted_fee', 0)
            currency = self.default_converted_currency_id.name.lower()

        values.update({
            'merchant_site_code': str(self.nganluong_merchant_site_code),
            'return_url': urls.url_join(base_url, NganLuongController._return_url),
            'receiver': self.nganluong_receiver_email,
            'transaction_info': values.get('reference'),
            'order_code': values.get('reference').split('-')[0],
            'price': amount,
            'currency': currency,
            'quantity': 1,
            'fee_shipping': fees,
            'order_description': 'odoo',
            'buyer_info': '%s *|* %s *|* %s *|* %s' % (
                values.get('billing_partner_name'),
                values.get('billing_partner_email'),
                values.get('billing_partner_phone'),
                '%s, %s, %s, %s' % (
                    values.get('partner_address'),
                    values.get('partner_city'),
                    values.get('partner_state').name,
                    values.get('partner_country').name
                    )
                ),
            'affiliate_code': 'odoo',
            'acquirer_id': self.id,
            'lang': lang,
            'cancel_url': urls.url_join(base_url, NganLuongController._cancel_url),
            'notify_url': urls.url_join(base_url, NganLuongController._notify_url),
            })
        return values

    def nganluong_get_form_action_url(self):
        return NGANLUONG_STANDARD_PAYMENT_PROCESS_ROUTE

    @api.model
    def _fill_nganluong_supported_currencies(self):
        """
        To be called by post_init_hook to fill supported currencies for Nganluong Acquirer
        """
        currency_map_vals_list = []

        supported_currencies = self.env['res.currency'].with_context(active_test=False).search([('name', 'in', NGANLUONG_SUPPORTED_CURRENCIES)])
        for acquirer in self.search([('provider', '=', 'nganluong')]):
            currency_map_vals_list += [{'acquirer_id': acquirer.id, 'currency_id': currency.id} for currency in supported_currencies
                                        if currency not in acquirer.supported_currency_map_ids.currency_id]
        if currency_map_vals_list:
            return self.env['payment.acquirer.supported.currency.map'].create(currency_map_vals_list)
        return self.env['payment.acquirer.supported.currency.map']
