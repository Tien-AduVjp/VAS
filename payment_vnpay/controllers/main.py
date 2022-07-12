import logging
import pprint
import werkzeug
import hashlib
import json
import hmac

from urllib.parse import quote, urlencode

from odoo import http, _
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params

_logger = logging.getLogger(__name__)

VNPAY_ERROR_CODE = {
    '00': 'Confirm Success',
    '01': 'Order not found',
    '02': 'Order already confirmed',
    '04': 'Invalid Amount',
    '97': 'Invalid Signature',
    '99': 'Unknow error',
    }

VNPAY_PAYMENT_PROCESS_ROUTE = '/payment/vnpay/process'


class VnpayController(http.Controller):
    _return_url = '/payment/vnpay/return'
    _notify_url = '/payment/vnpay/notify'
    
    def _check_characters_not_supported_by_VNPay(self, order_infor):
        if order_infor.find('+') != -1:
            return True
        return False
    
    def vnpay_get_tx(self, reference=''):
        tx = False
        if reference != '':
            tx = request.env['payment.transaction'].sudo().search([('reference', '=', reference)])
        if not tx:
            raise ValidationError(_("VNPay: Could not find payment transaction matching reference #%s") % reference)
        return tx

    def vnpay_validate_response(self, tx, **post):
        """This method will validate the data returned VNPay;
        return vnp_secure_hash == hash_value"""
        vnp_secure_hash = False
        # Remove hash params
        if 'vnp_SecureHash' in post.keys():
            vnp_secure_hash = post.get('vnp_SecureHash')
            post.pop('vnp_SecureHash')
        if 'vnp_SecureHashType' in post.keys():
            post.pop('vnp_SecureHashType')

        hash_value = hmac.new(tx.acquirer_id.vnpay_hash_secret.encode(), urlencode(post).encode(), hashlib.sha512).hexdigest()
        return vnp_secure_hash == hash_value

    def vnpay_validate_data(self, **post):
        """Once data is validated, process it."""
        vnp_TxnRef = post.get('vnp_TxnRef', '')
        msg_transaction_error = ''
        error_code = ''
        tx = False
        
        try:
            tx = self.vnpay_get_tx(vnp_TxnRef)
            if self.vnpay_validate_response(tx, **post):
                expected_amount = 0
                if tx.converted_currency_id and tx.converted_amount:
                    expected_amount = tx.converted_amount + tx.converted_fee
                else:
                    expected_amount = tx.amount + tx.fees

                if int(post.get('vnp_Amount', 0)) != (int(expected_amount) * 100):
                    error_code = '04'
                    _logger.warning('VNPay: Invalid amount for reference #%s' % vnp_TxnRef)
                    msg_transaction_error = _('VNPay: Invalid amount. Please contact your administrator.')
                elif tx.state == 'done':
                    error_code = '02'
                    _logger.info('VNPay: Order with reference #%s already confirmed.' % vnp_TxnRef)
                elif post.get('vnp_ResponseCode', '') == '00':
                    error_code = '00'
                    _logger.info('VNPay: validated data for reference #%s' % vnp_TxnRef)
                else:
                    error_code = '99'
                    _logger.warning('VNPay: Unknow error for reference #%s.' % vnp_TxnRef)
                    msg_transaction_error = _('VNPay: Unrecognized error. Please contact your administrator.')
                res = request.env['payment.transaction'].sudo().form_feedback(post, 'vnpay')
                if not res and tx:
                    msg_transaction_error = _('VNPay: Validation error occured. Please contact your administrator.')
            else:
                error_code = '97'
                _logger.warning('VNPay: Error when payment validated: mac not equal for reference #%s' % vnp_TxnRef)
                msg_transaction_error = _('VNPay: Error when payment validated. Please contact your administrator.')
        except:
            # tx._set_transaction_error('VNPay: Unrecognized error. Please contact your administrator.')
            if not tx:
                error_code = '01'
                _logger.warning('VNPay: Could not find payment transaction matching reference #%s.' % vnp_TxnRef)
            else:
                error_code = '99'
                _logger.warning('VNPay: Unknow error for reference #%s.' % vnp_TxnRef)
        
        if msg_transaction_error:
            tx._set_transaction_error(msg_transaction_error)
        
        result = {
            'RspCode': error_code,
            'Message': VNPAY_ERROR_CODE.get(error_code, ''),
            }
        return json.dumps(result)

    @http.route('/payment/vnpay/process', type='http', auth='public', methods=['POST'], csrf=False)
    def vnpay_payment_process(self, **post):
        tx = False
        try:
            tx = self.vnpay_get_tx(post.get('vnp_TxnRef'))
            _logger.info('Waitting for payment:')
        except:
            return werkzeug.utils.redirect('/payment/process')
        
        if self._check_characters_not_supported_by_VNPay(post.get('vnp_OrderInfo')):
            msg = _('VNPay: No support for special characters in name or email.')
            _logger.warning(msg)
            tx._set_transaction_error(msg)
            return werkzeug.utils.redirect('/payment/process')
        
        return werkzeug.utils.redirect(_build_url_w_params(tx.acquirer_id.vnpay_payment_url, post))

    @http.route('/payment/vnpay/return', type='http', auth="public", csrf=False)
    def vnpay_return(self, **post):
        """Get payment results from VNPay via returnUrl"""
        _logger.info('VNPay: Beginning VNPay return form_feedback with post data %s', pprint.pformat(post))  # debug
        try:
            self.vnpay_validate_data(**post)
        except ValidationError:
            _logger.exception('VNPay: Unable to validate the VNPay payment')
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/payment/vnpay/notify', type='http', auth="none", methods=['GET', 'POST'], csrf=False)
    def vnpay_notify(self, **post):
        """
        Get payment results from VNPay via IPN.
        Use GET or POST, depending on the configuration on the merchant page of VNPay."""
        
        _logger.info('VNPay: Beginning VNPay IPN form_feedback with post data %s', pprint.pformat(post))  # debug
        res = False
        try:
            res = self.vnpay_validate_data(**post)
        except ValidationError:
            _logger.exception('VNPay: Unable to validate the VNPay payment')
        return res
    
