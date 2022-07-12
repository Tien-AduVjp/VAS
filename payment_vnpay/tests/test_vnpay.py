import hashlib
import hmac
import requests

from lxml import objectify
from werkzeug import urls
from urllib.parse import quote
from unittest.mock import patch

from odoo import fields
from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo.exceptions import ValidationError

from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.payment_vnpay.controllers.main import VnpayController
from odoo.addons.payment_vnpay.models.payment_acquirer import PaymentAcquirerVNPay, VNPAY_SUPPORTED_CURRENCIES

from .vnpay_common import VNPayCommon


@tagged('post_install', '-at_install', 'external', '-standard')
class VNPayTest(VNPayCommon):

    @mute_logger('odoo.addons.payment_vnpay.models', 'ValidationError')
    def test_10_vnpay_form_management(self):
        # be sure not to do stupid things
        self.assertEqual(self.vnpay.state, 'test', 'test without test environment')

        # typical data posted by vnpay after client has successfully paid
        amount = 105000
        seq = 0

        vnpay_post_data = self._vnpay_post_data(amount, seq)

        # should raise error about unknown tx
        with self.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(vnpay_post_data, 'vnpay')

        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_vnd, seq)
        tx = self.env['payment.transaction'].create(vals)

        # validate it
        tx.form_feedback(vnpay_post_data, 'vnpay')
        # check
        self.assertEqual(tx.state, 'done', 'VNPay: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'VNPay: wrong txn_id after receiving a valid pending notification')

        # update tx
        tx.write({
            'state': 'draft',
            'acquirer_reference': False})

        # update notification from paypal
        vnpay_post_data['payment_status'] = 'Completed'
        # validate it
        tx.form_feedback(vnpay_post_data, 'vnpay')
        # check
        self.assertEqual(tx.state, 'done', 'VNPay: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'VNPay: wrong txn_id after receiving a valid pending notification')

    @mute_logger('odoo.addons.payment_vnpay.models', 'ValidationError')
    def test_20_vnpay_bad_configuration(self):
        # should raise error if `default_converted_currency_id` not in VNPAY_SUPPORTED_CURRENCIES
        if self.vnpay.default_converted_currency_id.name not in VNPAY_SUPPORTED_CURRENCIES:
            self.assertEqual(True, False, 'Default Converted Currency does not support by VNPay.')

    @mute_logger('odoo.addons.payment_vnpay.models', 'ValidationError')
    def test_30_vnpay_currency_euro(self):
        # typical data posted by vnpay after client has successfully paid

        amount = 105.10
        seq = 1

        # convert the amount in the original currency to the pre-configured currency supported by VNPay
        company = self.env.company
        amount_currency = int(self.currency_euro._convert(amount,
                                                    self.vnpay.default_converted_currency_id,
                                                    company, fields.Date.today()))

        vnpay_post_data = self._vnpay_post_data(amount_currency, seq)

        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_euro, seq, amount_currency)
        tx = self.env['payment.transaction'].create(vals)

        # validate it
        tx.form_feedback(vnpay_post_data, 'vnpay')
        # check
        self.assertEqual(tx.state, 'done', 'VNPay: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'VNPay: wrong txn_id after receiving a valid pending notification')

    @mute_logger('odoo.addons.payment_vnpay.models', 'ValidationError')
    def test_40_vnpay_currency_usd(self):
        # typical data posted by vnpay after client has successfully paid

        amount = 205.10
        seq = 2

        # convert the amount in the original currency to the pre-configured currency supported by VNPay
        company = self.env.company
        amount_currency = int(self.currency_usd._convert(amount,
                                                    self.vnpay.default_converted_currency_id,
                                                    company, fields.Date.today()))

        vnpay_post_data = self._vnpay_post_data(amount_currency, seq)

        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_usd, seq, amount_currency)
        tx = self.env['payment.transaction'].create(vals)

        # validate it
        tx.form_feedback(vnpay_post_data, 'vnpay')
        # check
        self.assertEqual(tx.state, 'done', 'VNPay: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'VNPay: wrong txn_id after receiving a valid pending notification')

    def test_50_vnpay_form_render(self):
        #Test: button direct rendering

        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        ipaddr = '127.0.0.1'

        amount = 150000
        reference = 'test_ref0'

        lang = self.buyer_values.get('partner_lang', 'en').lower()
        if lang[:2] == 'vi':
            lang = 'vn'
        else:
            lang = 'en'

        order_info = 'viindoo'

        vnp_amount = int(amount * 100)
        vnp_order_type = 'other'
        vnp_return_url = urls.url_join(base_url, VnpayController._return_url)
        vnp_command = 'pay'
        vnp_curr_code = 'VND'
        vnp_version = '2.1.0'

        with patch('odoo.addons.payment_vnpay.models.payment_acquirer.PaymentAcquirerVNPay._get_real_ip') as mocked:
            mocked.return_value = '127.0.0.1'
            # render the button
            res = self.vnpay.render(reference, amount, self.currency_vnd.id, values=self.buyer_values)

        # check form result
        tree = objectify.fromstring(res)

        vnp_create_date = False
        for form_input in tree.input:
            if form_input.get('name') == 'vnp_CreateDate':
                vnp_create_date = form_input.get('value')

        msg = 'vnp_Amount=%s&vnp_Command=%s&vnp_CreateDate=%s&vnp_CurrCode=%s&vnp_IpAddr=%s&vnp_Locale=%s&vnp_OrderInfo=%s&vnp_OrderType=%s&vnp_ReturnUrl=%s&vnp_TmnCode=%s&vnp_TxnRef=%s&vnp_Version=%s' % (
            vnp_amount, vnp_command, vnp_create_date, vnp_curr_code, ipaddr, lang, order_info,
            vnp_order_type, quote(vnp_return_url, safe=''), self.vnpay.vnpay_tmn_code, quote(reference, safe=''), vnp_version)

        form_values = {
            'vnp_Amount': str(vnp_amount),
            'vnp_Command': vnp_command,
            'vnp_CreateDate': vnp_create_date,
            'vnp_CurrCode': vnp_curr_code,
            'vnp_IpAddr': ipaddr,
            'vnp_Locale': lang,
            'vnp_OrderInfo': order_info,
            'vnp_OrderType': vnp_order_type,
            'vnp_ReturnUrl': vnp_return_url,
            'vnp_TmnCode': self.vnpay.vnpay_tmn_code,
            'vnp_TxnRef': reference,
            'vnp_Version': vnp_version,
            'vnp_SecureHash': hmac.new(str(self.vnpay.vnpay_hash_secret).encode(),
                                           str(msg).encode(),
                                           hashlib.sha512).hexdigest(),
            }

        data_set = tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set), 1, 'VNPay: Found %d "data_set" input instead of 1' % len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'), '/payment/vnpay/process', 'VNPay: wrong form POST url')
        for form_input in tree.input:
            if form_input.get('name') in ['submit', 'data_set']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'VNPay: wrong value for input %s: received %s instead of %s' % (form_input.get('name'), form_input.get('value'), form_values[form_input.get('name')])
            )

    def test_60_vnpay_test_to_detect_api_has_been_changed(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        ipaddr = '127.0.0.1'

        amount = 150000
        reference = 'test_ref0'

        lang = self.buyer_values.get('partner_lang', 'en').lower()
        if lang[:2] == 'vi':
            lang = 'vn'
        else:
            lang = 'en'

        order_info = 'viindoo'

        vnp_amount = int(amount * 100)
        vnp_order_type = 'other'
        vnp_return_url = urls.url_join(base_url, VnpayController._return_url)
        vnp_command = 'pay'
        vnp_curr_code = 'VND'
        vnp_version = '2.1.0'

        with patch('odoo.addons.payment_vnpay.models.payment_acquirer.PaymentAcquirerVNPay._get_real_ip') as mocked:
            mocked.return_value = '127.0.0.1'

            # render the button
            res = self.vnpay.render(reference, amount, self.currency_vnd.id, values=self.buyer_values)

        # check form result
        tree = objectify.fromstring(res)

        vnp_create_date = False
        for form_input in tree.input:
            if form_input.get('name') == 'vnp_CreateDate':
                vnp_create_date = form_input.get('value')

        msg = 'vnp_Amount=%s&vnp_Command=%s&vnp_CreateDate=%s&vnp_CurrCode=%s&vnp_IpAddr=%s&vnp_Locale=%s&vnp_OrderInfo=%s&vnp_OrderType=%s&vnp_ReturnUrl=%s&vnp_TmnCode=%s&vnp_TxnRef=%s&vnp_Version=%s' % (
            vnp_amount, vnp_command, vnp_create_date, vnp_curr_code, ipaddr, lang, order_info,
            vnp_order_type, quote(vnp_return_url, safe=''), self.vnpay.vnpay_tmn_code, quote(reference, safe=''), vnp_version)

        form_values = {
            'vnp_Amount': str(vnp_amount),
            'vnp_Command': vnp_command,
            'vnp_CreateDate': vnp_create_date,
            'vnp_CurrCode': vnp_curr_code,
            'vnp_IpAddr': ipaddr,
            'vnp_Locale': lang,
            'vnp_OrderInfo': order_info,
            'vnp_OrderType': vnp_order_type,
            'vnp_ReturnUrl': vnp_return_url,
            'vnp_TmnCode': self.vnpay.vnpay_tmn_code,
            'vnp_TxnRef': reference,
            'vnp_Version': vnp_version,
            'vnp_SecureHash': hmac.new(str(self.vnpay.vnpay_hash_secret).encode(),
                                           str(msg).encode(),
                                           hashlib.sha512).hexdigest(),
            }

        res = requests.get(_build_url_w_params(self.vnpay.vnpay_payment_url, form_values))
        self.assertFalse('<title>Error</title>' in res.text)

    def _prepare_payment_transaction_vals(self, amount, currency, seq=0, amount_currency=False):
        vals = {
            'amount': amount,
            'acquirer_id': self.vnpay.id,
            'acquirer_reference': 'test',
            'currency_id': currency.id,
            'reference': 'test-ref%s' % seq,
            'vnpay_card_type': 'ATM',
            'partner_name': 'Norbert Buyer',
            'partner_country_id': self.country_vn.id,
            }

        if amount_currency and currency.name not in VNPAY_SUPPORTED_CURRENCIES:
            vals.update({
                'converted_currency_id': self.vnpay.default_converted_currency_id.id,
                'converted_amount': amount_currency,
                })

        return vals

    def _vnpay_post_data(self, amount_currency, seq=0):
        return {
            'vnp_Amount': u'%s' % (amount_currency * 100),
            'vnp_TxnRef': u'test-ref%s' %seq,
            'vnp_CardType': u'ATM',
            'vnp_ResponseCode': u'00',
        }
