import hmac
import hashlib
import json
import logging
import requests

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransactionMoMo(models.Model):
    _inherit = 'payment.transaction'
    
    momo_payment_type = fields.Char('MoMo Payment type')
    momo_request_id = fields.Char('MoMo Request ID')
    
    def _momo_get_transaction_status(self):
        """Check the status of the payment transaction"""
        self.ensure_one()
        reference = self.reference.replace('/', '.')
        environment = 'prod' if self.acquirer_id.state == 'enabled' else 'test'
        momo_url = self.acquirer_id._get_momo_urls(environment)['momo_gw_url']
        # partnerCode=%s&accessKey=%s&requestId=%s&orderId=%s&requestType=%s
        msg = 'partnerCode=%s&accessKey=%s&requestId=%s&orderId=%s&requestType=%s' % (
            self.acquirer_id.momo_partner_code, self.acquirer_id.momo_access_key,
            self.momo_request_id, reference, 'transactionStatus')
        data = {
            'partnerCode': self.acquirer_id.momo_partner_code,
            'accessKey': self.acquirer_id.momo_access_key,
            'requestId': self.momo_request_id,
            'orderId': reference,
            'requestType': 'transactionStatus',
            'signature': hmac.new(
                            str(self.acquirer_id.momo_secret_key).encode(),
                            str(msg).encode(),
                            hashlib.sha256
                            ).hexdigest(),
            }
        urequest = requests.post(momo_url, json=data)
        urequest.raise_for_status()
        resp = json.loads(urequest.text)
        # payment type: web or qr; by default is '' if no payment
        if resp['errorCode'] == 0 and resp['payType'] != '':
            return True
        else:
            return False

    @api.model
    def _momo_form_get_tx_from_data(self, data):
        reference, request_id, trans_id = data.get('orderId', '').replace('.', '/'), data.get('requestId', ''), data.get('transId', '')
        if not reference or not request_id or not trans_id:
            error_msg = _('MoMo: received data with missing reference (%s) or request_id (%s) or trans_id (%s)') % (reference, request_id, trans_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'MoMo: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _momo_form_get_invalid_parameters(self, data):
        """
        This method modifies the amount (amount is amount + fees)
        to its original values they were before being converted to a MoMo accepted currency
        Without this, amount will be considered as invalid. For example,
        
        Invoice is US$1 and this amount was converted to 23000 VND for Momo payment processing.
        When Momo notifies Odoo, it returns vnp_amount and vnp_curr_code as 23000 VND and VND correspondingly.
        After that, Odoo would compare amount with US$1 correspondingly, then this will simply failed.
        """
        invalid_parameters = []
        # check what is buyed
        # we do check if the transaction currency is VND only as MoMo always returns amount in VND in its own currency rate
        expected_amount = 0
        if self.converted_currency_id and self.converted_amount:
            expected_amount = self.converted_amount + self.converted_fee
        else:
            expected_amount = self.amount + self.fees
        
        if int(data.get('amount', '0')) != int(expected_amount):
            invalid_parameters.append(('price', data.get('amount', '0'), '%.2f' % expected_amount))
        return invalid_parameters

    def _momo_form_validate(self, data):
        former_tx_state = self.state
        res = {
            'acquirer_reference': data.get('orderId', '').split('-')[0],
            'momo_payment_type': data.get('payType', '')
        }
        if data['errorCode'] == '0' and self._momo_get_transaction_status():
            date = fields.Datetime.now()
            res.update(date=date)
            self._set_transaction_done()
            if self.state == 'done' and self.state != former_tx_state:
                _logger.info('MoMo: Validated MoMo payment for tx %s: set as done' % (self.reference))
                return self.write(res)
            return True
        elif data['errorCode'] == '49':
            error = _('MoMo: Received unrecognized status for payment #%s: %s, set as cancel') % (self.reference, data['errorCode'])
            res.update(state_message=error)
            self._set_transaction_cancel()
            if self.state == 'cancel' and self.state != former_tx_state:
                _logger.info(error)
                return self.write(res)
            return True
        else:
            error = _('MoMo: Received unrecognized status for MoMo payment %s: %s, set as error') % (self.reference, data['errorCode'])
            res.update(state_message=error)
            self._set_transaction_error(error)
            if self.state == 'error' and self.state != former_tx_state:
                _logger.info(error)
                return self.write(res)
            return True
