import hmac
import hashlib

from werkzeug import urls
from lxml import objectify

from odoo import fields
from odoo.tools import mute_logger
from odoo.tests import tagged
from odoo.exceptions import ValidationError

from odoo.addons.payment_momo.models.payment_transaction import PaymentTransactionMoMo
from odoo.addons.payment_momo.controllers.main import MoMoController
from odoo.addons.payment_momo.models.payment_acquirer import MOMO_SUPPORTED_CURRENCIES
from .momo_common import MoMoCommon


@tagged('post_install', '-at_install', 'external', '-standard')
class MoMoTest(MoMoCommon):

    def test_10_form_render(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url').replace('http', 'https')
        # be sure not to do stupid things
        self.assertEqual(self.momo.state, 'test', 'test without test environment')

        # ----------------------------------------
        # Test: button direct rendering
        # ----------------------------------------

        # render the button
        res = self.momo.render(
            'test-ref0', 140000, self.currency_vnd.id,
            values=self.buyer_values)
        
        order_id = 'test-ref0'
        amount = 140000.0
        fees = 0.0
        
        extra_data = str({"serverinfo":"odoo", "itemid":order_id, "itemprice":amount, "fee_shipping":fees, "itemquantity":1})
        
        order_info = '%s (%s) pays order #%s' % (
                self.buyer_values.get('billing_partner_name'),
                self.buyer_values.get('billing_partner_email'),
                order_id
                )
        return_url = urls.url_join(base_url, MoMoController._return_url)
        notify_url = urls.url_join(base_url, MoMoController._notify_url)
        # MM+time create order (unix timestamp)+orderId
        request_id = 'MM%s_%s' % (int(fields.Datetime.now().timestamp()), order_id)

        # partnerCode=$partnerCode&accessKey=$accessKey&requestId=$requestId
        # &amount=$amount&orderId=$orderId&orderInfo=$orderInfo&returnUrl=$returnUrl
        # &notifyUrl=$notifyUrl&extraData=$extraData
        msg = 'partnerCode=%s&accessKey=%s&requestId=%s&amount=%s&orderId=%s&orderInfo=%s&returnUrl=%s&notifyUrl=%s&extraData=%s' % (
            self.momo.momo_partner_code, self.momo.momo_access_key, request_id, int(amount + fees),
            order_id, order_info, return_url, notify_url, extra_data)
        
        form_values = {
            'partnerCode': self.momo.momo_partner_code,
            'accessKey': self.momo.momo_access_key,
            'requestId': request_id,
            'amount': str(int(amount + fees)),
            'orderId': 'test-ref0',
            'orderInfo': order_info,
            'returnUrl': return_url,
            'notifyUrl': notify_url,
            'requestType': 'captureMoMoWallet',
            'signature': hmac.new(
                            str(self.momo.momo_secret_key).encode(),
                            str(msg).encode(),
                            hashlib.sha256
                            ).hexdigest(),
            'extraData': extra_data,
        }

        # check form result
        tree = objectify.fromstring(res)

        data_set = tree.xpath("//input[@name='data_set']")
        self.assertEqual(len(data_set), 1, 'MoMo: Found %d "data_set" input instead of 1' % len(data_set))
        self.assertEqual(data_set[0].get('data-action-url'), '/payment/momo/process', 'MoMo: wrong form POST url')
        for form_input in tree.input:
            if form_input.get('name') in ['submit', 'data_set']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'MoMo: wrong value for input %s: received %s instead of %s' % (form_input.get('name'), form_input.get('value'), form_values[form_input.get('name')])
            )
            
    @mute_logger('odoo.addons.payment_momo.models', 'ValidationError')
    def test_20_momo_form_management(self):
        # be sure not to do stupid things
        self.assertEqual(self.momo.state, 'test', 'test without test environment')

        amount = 130000
        # typical data posted by momo after client has successfully paid
        momo_post_data = self._momo_post_data(amount)

        # should raise error about unknown tx
        with self.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(momo_post_data, 'momo')

        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_vnd)
        tx = self.env['payment.transaction'].create(vals)

        # validate it
        tx.form_feedback(momo_post_data, 'momo')
        # check; tx.state is always a error, because _momo_get_transaction_status
        self.assertEqual(tx.state, 'error', 'MoMo: wrong state')
        self.assertEqual(tx.acquirer_reference, 'test', 'MoMo: wrong txn_id')
        
        # check; tx.state is always a error, because _momo_get_transaction_status
        # skip _momo_get_transaction_status
        self.patch(type(self.env['payment.transaction']), '_momo_get_transaction_status', lambda self: True)
        
        # validate it
        tx.form_feedback(momo_post_data, 'momo')
        # check
        self.assertEqual(tx.state, 'done', 'MoMo: wrong state after receiving a valid pending notification')

    @mute_logger('odoo.addons.payment_momo.models', 'ValidationError')
    def test_30_momo_bad_configuration(self):
        # should raise error if `default_converted_currency_id` not in MOMO_SUPPORTED_CURRENCIES
        if self.momo.default_converted_currency_id.name not in MOMO_SUPPORTED_CURRENCIES:
            self.assertEqual(True, False, 'Default Converted Currency does not support by MoMo.')

    @mute_logger('odoo.addons.payment_momo.models', 'ValidationError')
    def test_40_momo_currency_usd(self):
        # typical data posted by momo after client has successfully paid
        amount = 130.15
        
        # convert the amount in the original currency to the pre-configured currency supported by VNPay
        company = self.env.company
        amount_currency = int(self.currency_usd._convert(amount,
                                                    self.momo.default_converted_currency_id,
                                                    company, fields.Date.today()))
        momo_post_data = self._momo_post_data(amount_currency)

        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_usd, amount_currency)
        tx = self.env['payment.transaction'].create(vals)
        
        # check; tx.state is always a error, because _momo_get_transaction_status
        # skip _momo_get_transaction_status
        self.patch(type(self.env['payment.transaction']), '_momo_get_transaction_status', lambda self: True)
        
        # validate it
        tx.form_feedback(momo_post_data, 'momo')
        
        # check
        self.assertEqual(tx.state, 'done', 'MoMo: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'MoMo: wrong txn_id after receiving a valid pending notification')

    @mute_logger('odoo.addons.payment_momo.models', 'ValidationError')
    def test_50_momo_currency_euro(self):
        # typical data posted by momo after client has successfully paid
        amount = 130.15
        
        # convert the amount in the original currency to the pre-configured currency supported by VNPay
        company = self.env.company
        amount_currency = int(self.currency_euro._convert(amount,
                                                    self.momo.default_converted_currency_id,
                                                    company, fields.Date.today()))
        momo_post_data = self._momo_post_data(amount_currency)

        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_euro, amount_currency)
        tx = self.env['payment.transaction'].create(vals)
        
        # check; tx.state is always a error, because _momo_get_transaction_status
        # skip _momo_get_transaction_status
        self.patch(type(self.env['payment.transaction']), '_momo_get_transaction_status', lambda self: True)
        
        # validate it
        tx.form_feedback(momo_post_data, 'momo')
        
        # check
        self.assertEqual(tx.state, 'done', 'MoMo: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'MoMo: wrong txn_id after receiving a valid pending notification')

    def _prepare_payment_transaction_vals(self, amount, currency, amount_currency=False):
        vals = {
            'amount': amount,
            'acquirer_id': self.momo.id,
            'currency_id': currency.id,
            'reference': 'test-ref0',
            'partner_name': self.buyer_values.get('partner_name'),
            'partner_country_id': self.country_vn.id
            }
        
        if amount_currency and currency.name not in MOMO_SUPPORTED_CURRENCIES:
            vals.update({
                'converted_currency_id': self.momo.default_converted_currency_id.id,
                'converted_amount': amount_currency,
                })
        
        return vals

    def _momo_post_data(self, amount_currency):
        # typical data posted by momo after client has successfully paid
        msg = 'partnerCode=%s&accessKey=%s&requestId=%s&amount=%s&orderId=%s&orderInfo=%s&orderType=%s&transId=%s&message=%s&localMessage=%s&responseTime=%s&errorCode=%s&payType=%s&extraData=%s' % (
                self.momo.momo_partner_code, self.momo.momo_access_key, 'MM.test-ref0', amount_currency,
                'test-ref0', 'orderInfo', 'momo_wallet', '1234124124', 'success', u'thành công',
                '2020-03-28 09:00:00', '0', 'qr', 'extraData')
        mac = hmac.new(
                    str(self.momo.momo_secret_key).encode(),
                    str(msg).encode(),
                    hashlib.sha256
                    ).hexdigest()
        
        return {
            'partnerCode': u'%s' % self.momo.momo_partner_code,
            'accessKey': u'%s' % self.momo.momo_access_key,
            'requestId': u'MM.test-ref0',
            'amount': u'%s' % amount_currency,
            'orderId': 'test-ref0',
            'orderInfo': u'orderInfo',
            'orderType': u'momo_wallet',
            'transId': '1234124124',
            'errorCode': u'0',
            'message': u'success',
            'localMessage': u'thành công',
            'payType': u'qr',
            'responseTime': u'2020-03-28 09:00:00',
            'extraData': u'extraData',
            'signature': mac,
        }
