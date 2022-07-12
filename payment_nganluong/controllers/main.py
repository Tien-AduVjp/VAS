import logging
import pprint
import werkzeug
import hashlib

from odoo import _, http
from odoo.http import request
from odoo.exceptions import ValidationError
from odoo.addons.portal.controllers.portal import _build_url_w_params

_logger = logging.getLogger(__name__)

NGANLUONG_STANDARD_PAYMENT_PROCESS_ROUTE = '/payment/nganluong/standard'
NGANLUONG_SECURE_CODE_FIELDS = [
    'merchant_site_code',
    'return_url',
    'receiver',
    'transaction_info',
    'order_code',
    'price',
    'currency',
    'quantity',
    'tax',
    'discount',
    'fee_cal',
    'fee_shipping',
    'order_description',
    'buyer_info',
    'affiliate_code'
    ]

NGANLUONG_VERIFY_FIELDS = [
    'transaction_info',
    'order_code',
    'price',
    'payment_id',
    'payment_type',
    'error_text',
    'merchant_site_code',
    'secure_pass'
    ]


def md5(org_str):
    return hashlib.md5(org_str.encode()).hexdigest()


class NganLuongController(http.Controller):
    _return_url = '/payment/nganluong/return'
    _cancel_url = '/payment/nganluong/cancel'
    _notify_url = '/payment/nganluong/notify'

    @http.route('/payment/nganluong/webservice', auth="public", website=True, methods=['POST'], csrf=False)
    def nganluong_webservice(self, **post):
        """
        Nhan thong tin tra ve tu ngan luong
        """
        stop = True
        pass

    def _nganluong_md5_secure_code(self, acquirer, post):
        """
        Generate md5 secure code for NganLuong
        """
        join_code_str = ''
        for field in NGANLUONG_SECURE_CODE_FIELDS:
            if field in ['tax', 'discount', 'fee_cal', 'fee_shipping'] and not post[field]:
                post[field] = 0
            join_code_str += str(post[field]) + ' '
        join_code_str += acquirer.nganluong_merchant_password or ''
        return md5(join_code_str)

    @http.route(NGANLUONG_STANDARD_PAYMENT_PROCESS_ROUTE, auth="public", website=True, methods=['POST'], csrf=False)
    def nganluong_standard_payment_process(self, **post):
        """
        As Odoo always apply POST method while NganLuong requires GET method, we redirect request to this and change the method to GET
        """
        acq = request.env['payment.acquirer'].browse(int(post.get('acquirer_id'))).sudo()
        url = acq._get_nganluong_urls()
        post.update({
            'secure_code': self._nganluong_md5_secure_code(acq, post),
            })
        return request.redirect(_build_url_w_params(url, post))

    def nganluong_validate_returned_data(self, **post):
        tx = request.env['payment.transaction'].sudo().search([('reference', '=', post.get('transaction_info'))])
        if not tx:
            raise ValidationError(_("Could not find payment transaction matching reference %s NganLuong") % post.get('transaction_info'))

        nganluong_merchant_site_code = tx.acquirer_id.nganluong_merchant_site_code
        nganluong_merchant_password = tx.acquirer_id.nganluong_merchant_password

        verify_secure_code = ''
        for field in NGANLUONG_VERIFY_FIELDS:
            if field not in ['merchant_site_code', 'secure_pass']:
                verify_secure_code += ' ' + post.get(field)
            elif field == 'merchant_site_code':
                verify_secure_code += ' ' + nganluong_merchant_site_code
            else:
                verify_secure_code += ' ' + nganluong_merchant_password
        verify_secure_code = md5(verify_secure_code)
        if verify_secure_code != post.get('secure_code'):
            raise ValidationError(_("NganLuong: invalid data"))
        res = False
        if post['error_text'] == '':
            _logger.info('NganLuong: validated data')
            res = request.env['payment.transaction'].sudo().form_feedback(post, 'nganluong')
            if not res and tx:
                tx._set_transaction_error(_('Validation error occured. Please contact your administrator.'))
        elif post['error_text'] != '':
            _logger.warning('NganLuong: answered INVALID/FAIL on data verification')
            if tx:
                tx._set_transaction_error('Invalid response from NganLuong. Please contact your administrator.')
        tx._nganluong_validate_payment(post.get('order_code'))
        return res

    @http.route('/payment/nganluong/return', type='http', auth="public", methods=['GET', 'POST'], csrf=False)
    def nganluong_return(self, **post):
        """ NganLuong Return"""
        _logger.info('Beginning NganLuong form_feedback with post data %s', pprint.pformat(post))  # debug
        try:
            self.nganluong_validate_returned_data(**post)
        except ValidationError:
            _logger.exception('Unable to validate the NganLuong payment')
            return 0
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/payment/nganluong/cancel', type='http', auth="public", csrf=False)
    def nganluong_cancel(self, **post):
        """ When the user cancels its NganLuong payment: GET on this route """
        _logger.info('Beginning NganLuong cancel with post data %s', pprint.pformat(post))  # debug
        return werkzeug.utils.redirect('/payment/process')

    @http.route('/payment/nganluong/notify', type='http', auth="none", methods=['GET', 'POST'], csrf=False)
    def nganluong_notify(self, **post):
        """ NganLuong Notify """
        _logger.info('Beginning NganLuong form_feedback with post data %s', pprint.pformat(post))
        try:
            self.nganluong_validate_returned_data(**post)
        except ValidationError:
            _logger.exception('Unable to validate the NganLuong payment')
            return 0
        return ''
