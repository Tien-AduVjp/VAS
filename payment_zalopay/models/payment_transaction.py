import hmac
import hashlib
import json
import logging
import requests

from datetime import datetime, date

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from dateutil import relativedelta

_logger = logging.getLogger(__name__)

ZALOPAY_SUPPORTED_CURRENCIES = [
    'VND',  # Vietnam Dong [1]
    # [1] This currency does not support decimals. If you pass a decimal amount, an error occurs.
    ]


class PaymentTransactionZaloPay(models.Model):
    _inherit = 'payment.transaction'
    
    zalopay_apptransid = fields.Char('ZaloPay apptransid')
    
    def _get_reference(self, post):
        # apptransid: yymmdd_ordercode
        return json.loads(post.get('data')).get('apptransid').split('_')[1].replace('.', '/')
    
    def _zalopay_get_transaction_by_apptransid(self):
        self.ensure_one()
        environment = 'prod' if self.acquirer_id.state == 'enabled' else 'test'
        zalopay_url = self.acquirer_id._get_zalopay_urls(environment)['zalopay_get_status_by_apptransid']
        msg = '%s|%s|%s' % (self.acquirer_id.zalopay_appid, self.zalopay_apptransid, self.acquirer_id.zalopay_key1)

        mac = hmac.new(
            str(self.acquirer_id.zalopay_key1).encode(),
            str(msg).encode(),
            hashlib.sha256
            ).hexdigest()
        
        data = requests.get(zalopay_url, params={
            'appid': self.acquirer_id.zalopay_appid,
            'apptransid': self.zalopay_apptransid,
            'mac': mac
            }).json()

        if data.get('returncode') == 1:

            res = {
                'acquirer_reference': self.reference.split('-')[0],
            }
            date = fields.Datetime.now()
            res.update(date=date)
            self._set_transaction_done()
            if self.state == 'done':
                _logger.info('ZaloPay: Validated payment for tx %s: set as done', self.reference)
                return self.write(res)
        return True
    
    @api.model
    def _zalopay_form_get_tx_from_data(self, post):
        reference = self._get_reference(post)
        if not reference:
            error_msg = _('ZaloPay: received data with missing reference %s%s') % ('#', reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'ZaloPay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]
    
    def _zalopay_form_get_invalid_parameters(self, data):
        """
        This method modifies the amount (amount is amount + fees)
        to its original values they were before being converted to a ZaloPay accepted currency
        Without this, amount will be considered as invalid. For example,
        
        Invoice is US$1 and this amount was converted to 23000 VND for ZaloPay payment processing.
        When ZaloPay notifies Odoo, it returns amount as 23000 VND correspondingly.
        After that, Odoo would compare amount with US$1 correspondingly, then this will simply failed.
        """
        invalid_parameters = []

        expected_amount = 0
        if self.converted_currency_id and self.converted_amount:
            expected_amount = self.converted_amount + self.converted_fee
        else:
            expected_amount = self.amount + self.fees
        
        amount = json.loads(data.get('data', {})).get('amount', '0')
        
        if int(amount) != int(expected_amount):
            invalid_parameters.append(('price', amount, '%.2f' % expected_amount))

        return invalid_parameters
    
    def _zalopay_form_validate(self, post):
        """This method uses key2 to authenticate data posted by ZaloPayServer.
              1. If checksum == mac with key2 => payment success.
              2. Otherwise => payment failed
        """
        # Handle when successful payment
        reference = self._get_reference(post)
        former_tx_state = self.state
        res = {
            'acquirer_reference': reference.split('-')[0],
            }
        date = fields.Datetime.now()
        res.update(date=date)
        self._set_transaction_done()
        
        if self.state == 'done' and self.state != former_tx_state:
            _logger.info('ZaloPay: Validated payment for tx %s: set as done' % reference)
            return self.write(res)
        return True
    
    def cron_zalopay_check_transactions_if_not_callback(self):
        if not self:
            retry_limit_date = datetime.now() - relativedelta.relativedelta(days=2)
            # we retrieve all the payment tx that need to be processed
            self = self.search([('state', '=', 'draft'),
                                ('acquirer_id.provider', '=', 'zalopay'),
                                ('create_date', '>=', retry_limit_date)])
        for tx in self:
            try:
                tx._zalopay_get_transaction_by_apptransid()
            except:
                continue
