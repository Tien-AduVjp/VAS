import json
import hmac
import hashlib

from lxml import objectify

from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.addons.payment_zalopay.models.payment_acquirer import PaymentAcquirerZaloPay, ZALOPAY_SUPPORTED_CURRENCIES

from .zalopay_common import ZaloPayCommon


@tagged('post_install', '-at_install', 'external', '-standard')
class ZaloPayTest(ZaloPayCommon):

    @mute_logger('odoo.addons.payment_zalopay.models', 'ValidationError')
    def test_10_zalopay_form_management(self):
        # be sure not to do stupid things
        self.assertEqual(self.zalopay.state, 'test', 'test without test environment')

        # typical data posted by zalopay after client has successfully paid
        amount = 105000
        ref = 'test-ref0'

        zalopay_post_data = self._zalopay_post_data(amount, ref)

        # should raise error about unknown tx
        with self.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(zalopay_post_data, 'zalopay')

        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_vnd, ref)
        tx = self.env['payment.transaction'].create(vals)

        # validate it
        tx.form_feedback(zalopay_post_data, 'zalopay')
        # check
        self.assertEqual(tx.state, 'done', 'ZaloPay: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'ZaloPay: wrong txn_id after receiving a valid pending notification')

        # update tx
        tx.write({
            'state': 'draft',
            'acquirer_reference': False})

        # update notification from paypal
        zalopay_post_data['payment_status'] = 'Completed'
        # validate it
        tx.form_feedback(zalopay_post_data, 'zalopay')
        # check
        self.assertEqual(tx.state, 'done', 'ZaloPay: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'ZaloPay: wrong txn_id after receiving a valid pending notification')

    def test_20_zalopay_form_render(self):
        self.assertEqual(self.zalopay.state, 'test', 'test without test environment')

        appuser = '%s/%s/%s/%s/%s' % (
                self.buyer_values.get('billing_partner_id'),
                self.buyer_values.get('billing_partner_email'),
                'Norbert',
                self.buyer_values.get('billing_partner_phone'),
                self.buyer_values.get('billing_partner_email'))
        amount = 65000
        ref = 'test-ref1'
        fees = 0
        date_now = fields.Date.to_string(fields.Date.today())
        date_now = date_now[2:4] + date_now[5:7] + date_now[8:]
        apptime = int(fields.Datetime.now().timestamp() * 1000)
        apptransid = '%s_%s' %(date_now, ref)
        embeddata = json.dumps({"serverinfo":"odoo"})
        item = json.dumps([{"itemid":ref, "itemprice":amount, "fee_shipping":fees, "itemquantity":1}])
        # appid +”|”+ apptransid +”|”+ appuser +”|”+ amount +"|" + apptime +”|”+ embeddata +"|" +item
        msg = '%s|%s|%s|%s|%s|%s|%s' % (self.zalopay_appid, apptransid, appuser, amount + fees, apptime, embeddata, item)
        mac = hmac.new(
            str(self.zalopay_key1).encode(),
            str(msg).encode(),
            hashlib.sha256
        ).hexdigest()

        #render(self, reference, amount, currency_id, partner_id=False, values=None):
        # render the button
        res = self.zalopay.render(
            ref, amount, self.currency_vnd.id,
            values=self.buyer_values)

        form_values = {
            'appid': str(self.zalopay_appid),
            'appuser': str(appuser),
            'apptime': str(apptime),
            'amount': str(amount + fees),
            'apptransid': str(apptransid),
            'embeddata': str(embeddata),
            'item': str(item),
            'description': '%s %s (%s) pays order #%s' % (
                self.buyer_values.get('billing_partner_first_name'),
                self.buyer_values.get('billing_partner_last_name'),
                self.buyer_values.get('billing_partner_email'),
                ref
                 ),
            'mac': str(mac),
            'bankcode': 'zalopayapp',
        }

        # check form result
        tree = objectify.fromstring(res)

        for form_input in tree.input:
            if form_input.get('name') in ['submit', 'data_set']:
                continue
            self.assertEqual(
                form_input.get('value'),
                form_values[form_input.get('name')],
                'ZaloPay: wrong value for input %s: received %s instead of %s' %(form_input.get('name'), form_input.get('value'), form_values[form_input.get('name')])
                )

    def test_30_zalopay_form_validate(self):
        amount = 65000
        ref = 'test-ref2'
        data = self._zalopay_post_data(amount, ref)
        # should raise error about unknown tx
        with self.assertRaises(ValidationError):
            self.env['payment.transaction'].form_feedback(data, 'zalopay')
        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_vnd, ref)
        tx = self.env['payment.transaction'].create(vals)

        # validate it
        tx.form_feedback(data, 'zalopay')
        # check
        self.assertEqual(tx.state, 'done', 'ZaloPay: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'ZaloPay: wrong txn_id after receiving a valid pending notification')

    @mute_logger('odoo.addons.payment_zalopay.models', 'ValidationError')
    def test_40_zalopay_bad_configuration(self):
        # should raise error if `default_converted_currency_id` not in ZALOPAY_SUPPORTED_CURRENCIES
        if self.zalopay.default_converted_currency_id.name not in ZALOPAY_SUPPORTED_CURRENCIES:
            self.assertEqual(True, False, 'Default Converted Currency does not support by ZaloPay.')

    @mute_logger('odoo.addons.payment_zalopay.models', 'ValidationError')
    def test_50_zalopay_currency_euro(self):
        # typical data posted by ZaloPay after client has successfully paid

        amount = 105.10
        ref = 'test-ref3'

        # convert the amount in the original currency to the pre-configured currency supported by ZaloPay
        company = self.env.company
        amount_currency = int(self.currency_euro._convert(amount,
                                                    self.zalopay.default_converted_currency_id,
                                                    company, fields.Date.today()))

        zalopay_post_data = self._zalopay_post_data(amount_currency, ref)

        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_euro, ref, amount_currency)
        tx = self.env['payment.transaction'].create(vals)

        # validate it
        tx.form_feedback(zalopay_post_data, 'zalopay')
        # check
        self.assertEqual(tx.state, 'done', 'ZaloPay: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'ZaloPay: wrong txn_id after receiving a valid pending notification')

    @mute_logger('odoo.addons.payment_zalopay.models', 'ValidationError')
    def test_60_zalopay_currency_usd(self):
        # typical data posted by ZaloPay after client has successfully paid

        amount = 205.10
        ref = 'test-ref4'

        # convert the amount in the original currency to the pre-configured currency supported by VNPay
        company = self.env.company
        amount_currency = int(self.currency_usd._convert(amount+1,
                                                    self.zalopay.default_converted_currency_id,
                                                    company, fields.Date.today()))

        zalopay_post_data = self._zalopay_post_data(amount_currency, ref)

        # create tx
        vals = self._prepare_payment_transaction_vals(amount, self.currency_usd, ref, amount_currency)
        tx = self.env['payment.transaction'].create(vals)

        # validate it
        tx.form_feedback(zalopay_post_data, 'zalopay')
        # check
        self.assertEqual(tx.state, 'done', 'ZaloPay: wrong state after receiving a valid pending notification')
        self.assertEqual(tx.acquirer_reference, 'test', 'ZaloPay: wrong txn_id after receiving a valid pending notification')

    def _prepare_payment_transaction_vals(self, amount, currency, ref='test-ref0', amount_currency=False):
        vals = {
            'amount': amount,
            'acquirer_id': self.zalopay.id,
            'currency_id': self.currency_vnd.id,
            'reference': ref,
            'partner_name': 'Norbert Buyer',
            'partner_country_id': self.country_vn.id
            }

        if amount_currency and currency.name not in ZALOPAY_SUPPORTED_CURRENCIES:
            vals.update({
                'converted_currency_id': self.zalopay.default_converted_currency_id.id,
                'converted_amount': amount_currency,
                })

        return vals

    def _zalopay_post_data(self, amount_currency, ref='test-ref0'):
        return {
            "data":'{"apptransid":"200325_%s", "amount":"%s"}' % (ref, amount_currency),
        }
