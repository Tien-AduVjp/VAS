import logging
import werkzeug
import requests
import json
import hmac
import hashlib
import pprint

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

MOMO_PAYMENT_PROCESS_ROUTE = '/payment/momo/process'


class MoMoController(http.Controller):
    _notify_url = '/payment/momo/notify'
    _return_url = '/payment/momo/return'

    def momo_get_tx(self, reference=''):
        tx = False
        reference = reference.replace('.', '/')
        if reference != '':
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
        if not tx:
            raise ValidationError(_("MoMo: Could not find payment transaction matching reference #%s") % reference)
        return tx

    def momo_validate_data(self, **post):
        """Once data is validated, process it."""
        res = False
        try:
            tx = self.momo_get_tx(post['orderId'])
            msg = 'partnerCode=%s&accessKey=%s&requestId=%s&amount=%s&orderId=%s&orderInfo=%s&orderType=%s&transId=%s&message=%s&localMessage=%s&responseTime=%s&errorCode=%s&payType=%s&extraData=%s' %(
                tx.acquirer_id.momo_partner_code, tx.acquirer_id.momo_access_key, post['requestId'], post['amount'],
                post['orderId'], post['orderInfo'], post['orderType'], post['transId'], post['message'], post['localMessage'],
                post['responseTime'], post['errorCode'], post['payType'], post['extraData'])
            mac = hmac.new(
                    str(tx.acquirer_id.momo_secret_key).encode(),
                    str(msg).encode(),
                    hashlib.sha256
                    ).hexdigest()
            if post['signature'] == mac:
                _logger.info('MoMo: validated data')
                res = request.env['payment.transaction'].sudo().form_feedback(post, 'momo')
                if not res and tx:
                    tx._set_transaction_error(_('MoMo: Validation error occured. Please contact your administrator.'))
            else:
                _logger.warning('MoMo: Error when payment validated: mac not equal')
                tx._set_transaction_error(_('MoMo: Error when payment validated. Please contact your administrator.'))
        except:
            _logger.warning('MoMo: Unrecognized error. Please contact your administrator.')
            tx._set_transaction_error(_('MoMo: Unrecognized error. Please contact your administrator.'))

        return res

    @http.route(MOMO_PAYMENT_PROCESS_ROUTE, type='http', auth='public', methods=['POST'], csrf=False)
    def momo_payment_process(self, **post):
        try:
            tx = self.momo_get_tx(post.get('orderId', ''))
            environment = 'prod' if tx.acquirer_id.state == 'enabled' else 'test'
            momo_url = tx.acquirer_id._get_momo_urls(environment)['momo_gw_url']
            _logger.info('Creating order:')
            urequest = requests.post(momo_url, json=post)
            urequest.raise_for_status()
            resp = json.loads(urequest.text)
            if resp['errorCode'] == 0:
                tx.update({'momo_request_id': post.get('requestId', '')})
                _logger.info('Waitting for payment:')
                return werkzeug.utils.redirect(resp['payUrl'])
            else:
                _logger.error('MoMo: %s' % resp["message"])
        except:
            return werkzeug.utils.redirect('/payment/process')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/payment/momo/return', type='http', auth='public', csrf=False)
    def momo_return(self, **post):
        """Get payment results from MoMo via returnUrl"""
        if self.momo_get_tx(post.get('orderId', '')):
            return werkzeug.utils.redirect('/payment/process')

    @http.route('/payment/momo/notify', type='http', auth='none', methods=['POST'], csrf=False)
    def momo_notify(self, **post):
        """Get payment results from MoMo via IPN (notifyUrl)"""
        _logger.info('MoMo: Beginning MoMo IPN form_feedback with post data %s', pprint.pformat(post))  # debug
        try:
            self.momo_validate_data(**post)
        except ValidationError:
            _logger.exception('MoMo: Unable to validate the MoMo payment')
