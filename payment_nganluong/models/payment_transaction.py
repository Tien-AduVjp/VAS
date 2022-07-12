import logging
import requests

from odoo import models, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from odoo.tools.misc import formatLang

from ..controllers.main import md5

_logger = logging.getLogger(__name__)

NL_ERROR_CODE = {
    '00': _("Successful"),
    '01': _("Wrong query method. NganLuong requires a valid POST method."),
    '03': _("Wrong query data (either key or value) submitted to NganLuong."),
    '06': _("Merchant does not exist or not active."),
    '13': _("Wrong order code submitted to NganLuong"),
    '29': _("Wrong token submitted to NganLuong"),
    '81': _("The order has not been paid"),
    '99': _("Unknown error"),
    }

NL_ORDER_PAYMENT_FIELDS_MAP = {
    'receiver_email': 'acquirer_id.nganluong_receiver_email',
    'order_code': 'reference',
    'total_amount': 'amount'
    }


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    nganluong_txn_type = fields.Selection([
        ('0', 'Unknown Payment Type'),
        ('1', 'Direct Transfer'),
        ('2', 'Detained 02 days'),
        ('3', 'Detained 03 days'),
        ('4', 'Detained 04 days'),
        ('5', 'Detained 05 days'),
        ('6', 'Detained 06 days'),
        ('7', 'Detained 07 days'),
        ('8', 'Detained 08 days'),
        ('9', 'Detained 09 days'),
        ('10', 'Detained 10 days'),
        ], string='NganLuong Payment Type')
    nganluong_token = fields.Char(string='NganLuong Token')
    nganluong_payment_id = fields.Char(string='NganLuong Payment ID')

    def _nganluong_form_get_tx_from_data(self, data):
        reference = data.get('transaction_info')
        if not reference:
            error_msg = _('NganLuong: received data with missing reference (%s)') % reference
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = _('NganLuong: received data for reference %s') % reference
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    def _nganluong_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if self.reference and data.get('transaction_info') != self.reference:
            invalid_parameters.append(('transaction_info', data.get('transaction_info'), self.reference))
        # check what is buyed
        # we do check if the transaction currency is VND only as NL always returns amount in VND in its own currency rate
        if self.currency_id == self.env.ref('base.VND'):
            if float_compare(float(data.get('price', '0.0')), (self.amount + self.fees), 2) != 0:
                invalid_parameters.append(('price', data.get('price'), '%.2f' % (self.amount + self.fees)))

        return invalid_parameters

    def _nganluong_form_validate(self, data):
        former_tx_state = self.state
        res = {
            'acquirer_reference': data.get('order_code'),
            'nganluong_txn_type': data.get('payment_type'),
            'nganluong_token':  data.get('token_nl'),
            'nganluong_payment_id': data.get('payment_id'),
            'nganluong_txn_type': data.get('payment_type')
        }

        payment_type = data.get('payment_type')

        detained_states = ['2', '3', '4', '5', '6', '7', '8', '9', '10']

        if (self.acquirer_id.nganluong_accept_detained_payment and payment_type in detained_states) or data.get('payment_type') == '1':
            date = fields.Datetime.now()
            res.update(date=date)
            self._set_transaction_done()
            if self.state == 'done' and self.state != former_tx_state:
                _logger.info('Validated NganLuong payment for tx %s: set as done' % (self.reference))
                return self.write(res)
            return True
        elif payment_type in detained_states:
            res.update(state_message=_("NganLuong Payment has been made successful but detained by NganLuong!"))
            self._set_transaction_pending()
            if self.state == 'pending' and self.state != former_tx_state:
                _logger.info('Received notification for NganLuong payment %s: set as pending' % (self.reference))
                return self.write(res)
            return True
        else:
            error = _('Received unrecognized status for NganLuong payment %s: %s, set as error') % (self.reference, data.get('payment_type'))
            res.update(state_message=error)
            self._set_transaction_cancel()
            if self.state == 'cancel' and self.state != former_tx_state:
                _logger.info(error)
                return self.write(res)
            return True

    def _nganluong_query_order(self, order_code):
        """
        Query ngayluong for payment infor by given order_code
        """
        self.ensure_one()
        url = self.acquirer_id._get_nganluong_order_check_url()
        req = requests.post(url, {
            'merchant_id': self.acquirer_id.nganluong_merchant_site_code,
            'order_code':order_code,
            'checksum': md5('%s|%s' % (order_code, self.acquirer_id.nganluong_merchant_password))
            })
        req.raise_for_status()
        return req.json()

    def _nganluong_validate_payment(self, order_code):
        self.ensure_one()
        try:
            order_info = self._nganluong_query_order(order_code)
            if order_info.get('error_code') != '00':
                raise ValidationError(NL_ERROR_CODE[order_info.get('error_code')])

            if order_info['data'].get('receiver_email') != self.acquirer_id.nganluong_receiver_email:
                raise ValidationError(_("NganLuong merchant does not match!"))

            if order_info['data'].get('order_code') != self.reference.split('-')[0]:
                raise ValidationError(_("NganLuong order code does not match!"))

            expected_amount = 0
            if self.converted_currency_id and self.converted_amount:
                expected_amount = self.converted_amount + self.converted_fee
            else:
                expected_amount = self.amount + self.fees
            if float_compare(order_info['data'].get('total_amount') / 1.0, expected_amount, precision_rounding=self.currency_id.rounding) != 0:
                raise ValidationError(_("NganLuong total amount data does not match!"))

            if  order_info['data'].get('transaction_status') != '00':
                raise ValidationError(_("The payment has not been made at NganLuong"))

        except requests.HTTPError as e:
            raise ValidationError(e)

    def _get_payment_transaction_received_message(self):
        self.ensure_one()
        amount = formatLang(self.env, self.amount, currency_obj=self.currency_id)
        message_vals = [self.reference, self.acquirer_id.name, amount]
        if self.acquirer_id.provider == 'nganluong' and self.state == 'pending' and self.nganluong_txn_type and self.nganluong_txn_type != '1':
            message = _('The transaction %s with %s for %s is pending and detained.')
            return message % tuple(message_vals)
        else:
            return super(PaymentTransaction, self)._get_payment_transaction_received_message()

    def cron_nganluong_check_pending_transactions(self):
        transactions = self.env['payment.transaction'].sudo().search([('state', '=', 'pending'), ('acquirer_id.provider', '=', 'nganluong')])
        for tx in transactions:
            try:
                data = tx._nganluong_query_order(tx.acquirer_reference)
                # TODO: not sure if this is correct. Need to talk with NL support team to find how to know when a detained payment will be done
                if data['error_code'] == '00' and data['data']['transaction_status'] == '00' and data['data']['payment_type'] == '1':
                    tx.write({'state': 'done'})
            except requests.HTTPError as e:
                continue
