import logging
import werkzeug
import requests
import json
import hmac
import hashlib

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

ZALOPAY_PAYMENT_PROCESS_ROUTE = '/payment/zalopay/process'


class ZaloPayController(http.Controller):
    _callback_url = '/payment/zalopay/callback'
    _redirect_url = '/payment/zalopay/redirect'

    def generate_hmac_sha256(self, secret, msg):
        return hmac.new(
                    str(secret).encode(),
                    str(msg).encode(),
                    hashlib.sha256
                    ).hexdigest()

    def zalopay_get_tx(self, reference=''):
        tx = False
        if reference != '':
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', reference.replace('.', '/'))])
        if not tx:
            raise ValidationError(_("ZaloPay: Could not find payment transaction matching reference #%s") % reference)
        return tx

    def zalopay_validate_data(self, post):
        result = {}

        try:
            tx = self.zalopay_get_tx(json.loads(post.get('data')).get('apptransid').split('_')[1])
            if post.get('mac') == self.generate_hmac_sha256(tx.acquirer_id.zalopay_key2, post.get('data')):
                result['returncode'] = 1
                result['returnmessage'] = 'success'
                _logger.info('ZaloPay: validated data')
                res = request.env['payment.transaction'].sudo().form_feedback(post, 'zalopay')
                if not res and tx:
                    tx._set_transaction_error(_('ZaloPay: Validation error occured. Please contact your administrator.'))
            else:
                result['returncode'] = -1
                result['returnmessage'] = 'mac not equal'
                _logger.info('ZaloPay: Error when payment validated: mac not equal')
                tx._set_transaction_error(_('ZaloPay: Error when payment validated. Please contact your administrator.'))
        except:
            result['returncode'] = 0  # ZaloPayServer will callback up to 3 times
            result['returnmessage'] = 'exception error'

        # Notify the result to ZaloPay server
        return json.dumps(result)

    @http.route(ZALOPAY_PAYMENT_PROCESS_ROUTE, type='http', auth='public', methods=['POST'], csrf=False)
    def zalopay_payment_process(self, **post):
        """This method processes the data and creates an order for zalopay, 
        then redirects the user to the received url for payment by the user, 
        or catch an error if an error occurred when creating the order
        """
        try:
            tx = self.zalopay_get_tx(post.get('apptransid').split('_')[1])
            environment = 'prod' if tx.acquirer_id.state == 'enabled' else 'test'
            zalopay_url = tx.acquirer_id._get_zalopay_urls(environment)['zalopay_checkout_url_large_payload']
            _logger.info('Creating order:')
            urequest = requests.post(zalopay_url, post)
            urequest.raise_for_status()
            resp = json.loads(urequest.text)
            if resp["returncode"] == 1:
                _logger.info('Waitting for payment:')
                # create a apptransid to check, because when payment is successful, but ZaloPay may be faulty
                tx.update({'zalopay_apptransid': post.get('apptransid')})
                return werkzeug.utils.redirect(resp["orderurl"])

            _logger.error('ZaloPay: %s' % resp["returnmessage"])
        except:
            return werkzeug.utils.redirect('/payment/process')

        return werkzeug.utils.redirect('/payment/process')

    @http.route('/payment/zalopay/redirect', type='http', auth="public", csrf=False)
    def zalopay_redirect(self, **post):
        """This method will be run when ZaloPayServer redirects:
        - payment success
        - payment failed
        - payment canceled.
        """
        try:
            reference = post.get('apptransid').split('_')[1]
            tx = self.zalopay_get_tx(reference)
            if post.get('status') == '1':  # status 1 => success; otherwise
                # appid+"|"+apptransid+"|"+pmcid+"|"+bankcode+"|"+amount+"|"+discountamount+"|"+status
                msg = "%s|%s|%s|%s|%s|%s|%s" % (
                    post.get('appid'),
                    post.get('apptransid'),
                    post.get('pmcid'),
                    post.get('bankcode'),
                    post.get('amount'),
                    post.get('discountamount'),
                    post.get('status'),
                    )

                if post.get('checksum') == self.generate_hmac_sha256(tx.acquirer_id.zalopay_key2, msg):
                    _logger.info('ZaloPay: Validated payment for tx %s: set as done' % reference)
            elif post.get('status') == '-49':  # payment cancelled
                _logger.warning(_('ZaloPay: Received unrecognized status for payment #%s: %s, set as cancel') % (reference, post.get('status')))
                tx._set_transaction_cancel()
            else:
                _logger.warning('ZaloPay: Received unrecognized status for payment #%s: %s, set as pending' % (reference, post.get('status')))
                tx._set_transaction_error(_('ZaloPay: Error when payment validated. Please contact your administrator.'))

        except ValidationError:
            _logger.exception('ZaloPay: Unable to validate the ZaloPay payment')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/payment/zalopay/callback', type='json', methods=['POST'], auth='none', csrf=False)
    def zalopay_callback(self):
        """This method is called when the ZaloPayServer sub the user's pay"""
        res = False
        try:
            res = self.zalopay_validate_data(json.loads(request.httprequest.data))
        except ValidationError:
            _logger.exception('ZaloPay: Unable to validate the ZaloPay payment')
        return res
