import datetime
from urllib.parse import urljoin


from odoo import models, fields, _
from odoo.exceptions import ValidationError

import requests, json

SANDBOX_SINVOICE_API_URL = 'https://demo-sinvoice.viettel.vn:8443'
SINVOICE_API_URL = 'https://api-sinvoice.viettel.vn:443'
SINVOICE_API_URL_V2 = 'https://api-vinvoice.viettel.vn:443/services/einvoiceapplication/api/'
SINVOICE_STATUS_PATH = 'InvoiceAPI/InvoiceUtilsWS/getProvidesStatusUsingInvoice'
SINVOICE_CREATE_PATH = 'InvoiceAPI/InvoiceWS/createInvoice/'
SINVOICE_UPDATE_PAYMENT_STATUS_PATH = 'InvoiceAPI/InvoiceWS/updatePaymentStatus'
SINVOICE_CANCEL_PAYMENT_STATUS_PATH = 'InvoiceAPI/InvoiceWS/cancelPaymentStatus'
SINVOICE_PRESENTATION_FILE_PATH = 'InvoiceAPI/InvoiceUtilsWS/getInvoiceRepresentationFile'
SINVOICE_EXCHANGE_FILE_PATH = 'InvoiceAPI/InvoiceWS/createExchangeInvoiceFile'
SINVOICE_CANCEL_PATH = 'InvoiceAPI/InvoiceWS/cancelTransactionInvoice'
SINVOICE_SEARCH_INVOICE_BY_TRANSACTION_UUID = 'InvoiceAPI/InvoiceWS/searchInvoiceByTransactionUuid'
SINVOICE_LOGIN_PATH = '/auth/login'


class EinvoiceService(models.Model):
    _inherit = 'einvoice.service'

    provider = fields.Selection(selection_add=[('sinvoice', 'Viettel S-Invoice')],
                                         ondelete={'sinvoice': 'set default'})
    sinvoice_synch_payment_status = fields.Boolean(string='Payment Status Synchronization', default=True,
                                                   help="If checked, having invoice paid in Odoo will also get the sinvoice paid. Having a paid invoice"
                                                        " reopened in Odoo will also get the sinvoice reopened accordingly.")
    sinvoice_conversion_user_id = fields.Many2one('res.users', string='SInvoice Force Conversion User',
                                                  help="If specified, during conversion, Odoo will use this user as the conversion user"
                                                       " instead the one who actually converts the invoice.")

    sinvoice_max_len_bank_name = fields.Integer(string="Length limit bank name",
                                                help="Set if you want to receive length warning of the bank name",
                                                default=100)
    sinvoice_max_len_bank_account = fields.Integer(string="Length limit bank account",
                                                   help="Set if you want to receive length warning of the bank account",
                                                   default=20)

    def get_sinvoice_login_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), SINVOICE_LOGIN_PATH)

    def get_sinvoice_create_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), '%s%s' % (SINVOICE_CREATE_PATH, self.company_id.vat))

    def get_sinvoice_update_payment_status_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), SINVOICE_UPDATE_PAYMENT_STATUS_PATH)

    def get_sinvoice_cancel_payment_status_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), SINVOICE_CANCEL_PAYMENT_STATUS_PATH)

    def get_sinvoice_cancel_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), SINVOICE_CANCEL_PATH)

    def get_sinvoice_exchange_file_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), SINVOICE_EXCHANGE_FILE_PATH)

    def get_sinvoice_presentation_file_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), SINVOICE_PRESENTATION_FILE_PATH)

    def get_sinvoice_status_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), SINVOICE_STATUS_PATH)

    def get_sinvoice_search_by_transaction_uuid_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), SINVOICE_SEARCH_INVOICE_BY_TRANSACTION_UUID)

    def _get_sinvoice_token(self):
        """
        Get API token of S-invoice to access S-invoice system in given duration.
        API server return refresh_token information but we don't have any guidance on how to use it recently.
        # TODO: Check API document how to use refresh_token.
        """
        if self.access_token and self.token_validity and self.token_validity > fields.Datetime.now():
            return self.access_token
        api_url = self.get_sinvoice_login_url()
        data = {
                "username": self.username if self.mode == 'production' else self.sandbox_username,
                "password": self.password if self.mode == 'production' else self.sandbox_password,
                }
        try:
            result = requests.post(api_url,
                                   json=data,
                                   headers={"Content-type": "application/json"},
                                   timeout=30000)
            result.raise_for_status()
            output = json.loads(result.text)
            if not output.get('access_token', False):
                raise ValidationError(_('Log in S-Invoice system unsuccessfully. You should check the account configuration in setting'))
            self.sudo().write({
                'access_token': output['access_token'],
                'refresh_token': output['refresh_token'],
                'token_validity': fields.Datetime.now() + datetime.timedelta(0, output['expires_in'] - 1)
                })
            return output['access_token']
        except Exception as e:
            raise ValidationError(_("Something went wrong when log in S-Invoice system. Here is the debugging information:\n%s") % str(e))
