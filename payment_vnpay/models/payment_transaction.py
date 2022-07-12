import logging

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

VNPAY_SUPPORTED_CURRENCIES = [
    'VND',  # Vietnam Dong [1]
    # [1] This currency does not support decimals. If you pass a decimal amount, an error occurs.
    ]

class PaymentTransactionVNPay(models.Model):
    _inherit = 'payment.transaction'

    vnpay_card_type = fields.Char('VNPay Card Type')

    @api.model
    def _vnpay_form_get_tx_from_data(self, data):
        reference = data.get('vnp_TxnRef')
        if not reference:
            error_msg = _('VNPay: received data with missing reference (%s)') % reference
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'VNPay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _vnpay_form_get_invalid_parameters(self, data):
        """
        This method modifies the vnp_amount and vnp_curr_code (vnp_amount is amount + fees)
        to its original values they were before being converted to a VNPay accepted currency
        Without this, vnp_amount and vnp_curr_code will be considered as invalid. For example,

        Invoice is US$1 and this amount was converted to 23000 VND for VNPay payment processing.
        When VNPay notifies Odoo, it returns vnp_amount and vnp_curr_code as 23000 VND and VND correspondingly.
        After that, Odoo would compare vnp_amount and vnp_curr_code with US$1 and USD correspondingly, then this will simply failed.
        """
        invalid_parameters = []
        expected_amount = 0
        if self.converted_currency_id and self.converted_amount:
            expected_amount = self.converted_amount + self.converted_fee
        else:
            expected_amount = self.amount + self.fees

        if int(data.get('vnp_Amount', '0')) != int(expected_amount * 100):
                invalid_parameters.append(('price', int(data.get('vnp_Amount')) / 100, '%.2f' % expected_amount))

        return invalid_parameters

    def _vnpay_form_validate(self, data):
        former_tx_state = self.state
        res = {
            'acquirer_reference': data.get('vnp_TxnRef').split('-')[0],
            'vnpay_card_type': data.get('vnp_CardType')
        }
        if data['vnp_ResponseCode'] == '00':
            date = fields.Datetime.now()
            res.update(date=date)
            self._set_transaction_done()
            if self.state == 'done' and self.state != former_tx_state:
                _logger.info('VNPay: Validated VNPay payment for tx %s: set as done' % (self.reference))
                return self.write(res)
            return True
        else:
            error = _('VNPay: Received unrecognized status for VNPay payment %s: %s, set as error') % (self.reference, data['vnp_ResponseCode'])
            res.update(state_message=error)
            self._set_transaction_error(error)
            if self.state == 'error' and self.state != former_tx_state:
                _logger.info(error)
                return self.write(res)
            return True
