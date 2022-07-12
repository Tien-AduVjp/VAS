import requests, json
from urllib.parse import urljoin
from requests.auth import HTTPBasicAuth

from odoo import models, fields, api
from odoo.exceptions import ValidationError

SANDBOX_SINVOICE_API_URL = 'https://demo-sinvoice.viettel.vn:8443'
SINVOICE_API_URL = 'https://api-sinvoice.viettel.vn:443'
SINVOICE_STATUS_PATH = '/InvoiceAPI/InvoiceUtilsWS/getProvidesStatusUsingInvoice'
SINVOICE_CREATE_PATH = '/InvoiceAPI/InvoiceWS/createInvoice/'
SINVOICE_UPDATE_PAYMENT_STATUS_PATH = '/InvoiceAPI/InvoiceWS/updatePaymentStatus'
SINVOICE_CANCEL_PAYMENT_STATUS_PATH = '/InvoiceAPI/InvoiceWS/cancelPaymentStatus'
SINVOICE_PRESENTATION_FILE_PATH = '/InvoiceAPI/InvoiceUtilsWS/getInvoiceRepresentationFile'
SINVOICE_EXCHANGE_FILE_PATH = '/InvoiceAPI/InvoiceWS/createExchangeInvoiceFile'
SINVOICE_CANCEL_PATH = '/InvoiceAPI/InvoiceWS/cancelTransactionInvoice'
SINVOICE_SEARCH_INVOICE_BY_TRANSACTION_UUID = '/InvoiceAPI/InvoiceWS/searchInvoiceByTransactionUuid'


class ResCompany(models.Model):
    _inherit = 'res.company'

    einvoice_provider = fields.Selection(selection_add=[('sinvoice', 'Viettel S-Invoice')])
    sinvoice_mode = fields.Selection([
        ('sandbox', 'Sandbox'), ('production', 'Production')], default='sandbox', copy=False, required=True,
        string='S-Invoice Mode', help="Choose Sandbox mode for testing before switch it to Production")
    sinvoice_start = fields.Date(string='S-Invoice Start Date', help="The date from which your company announced the start of using S-Invoice.")
    sinvoice_api_url = fields.Char(string='SInvoice API URL', compute='_compute_sinvoice_api_url', inverse='_set_sinvoice_api_url')
    sandbox_sinvoice_api_url = fields.Char(string='SInvoice Sandbox API URL', compute='_compute_sandbox_sinvoice_api_url', inverse='_set_sandbox_sinvoice_api_url')

    account_sinvoice_serial_id = fields.Many2one('account.sinvoice.serial', string='SInvoice Invoice Serial', ondelete='restrict',
                                                 help="The prefix (e.g. AA/16E, AA/17E, etc) of the"
                                                 " invoice number that must be registered with S-Invoice priorily. See the Circular No. 39/2014/TT-BTC"
                                                 " dated March 31, 2014 by The Ministry of Finance of Vietnam.")
    account_sinvoice_template_id = fields.Many2one('account.sinvoice.template', string='S-Invoice Template', ondelete='restrict',
                                                   help="The template that you have registered with"
                                                   " S-Invoice for redering your invoices of this template")
    account_sinvoice_type_id = fields.Many2one('account.sinvoice.type', string='S-Invoice Type', ondelete='restrict',
                                               help="The invoice type provided by Viettel S-Invoice.")
    sinvoice_synch_payment_status = fields.Boolean(string='Payment Status Synchronization', default=True,
                                                help="If checked, having invoice paid in Odoo will also get the sinvoice paid. Having a paid invoice"
                                                " reopened in Odoo will also get the sinvoice reopened accordingly.")
    sinvoice_conversion_user_id = fields.Many2one('res.users', string='SInvoice Force Conversion User',
                                                help="If specified, during conversion, Odoo will use this user as the conversion user"
                                                " instead the one who actually converts the invoice.")

    sinvoice_api_username = fields.Char('S-Invoice username', copy=False)
    sinvoice_api_password = fields.Char('S-Invoice password', copy=False)
    sinvoice_max_len_bank_name = fields.Integer(string="Length limit bank name", 
                                                help="Set if you want to receive length warning of the bank name",
                                                default=100)
    sinvoice_max_len_bank_account = fields.Integer(string="Length limit bank account", 
                                                   help="Set if you want to receive length warning of the bank account",
                                                   default=20)
    def get_sinvoice_auth_str(self):
        self.ensure_one()
        return HTTPBasicAuth(self.sinvoice_api_username, self.sinvoice_api_password)

    def _get_sinvoice_api_url(self):
        """
        Return S-Invoice API URL according to the S-Invoice Mode which is either sandbox or production
        """
        self.ensure_one()
        return self.sinvoice_api_url if self.sinvoice_mode == 'production' else self.sandbox_sinvoice_api_url

    def get_sinvoice_create_url(self):
        self.ensure_one()
        return urljoin(self._get_sinvoice_api_url(), '%s%s' % (SINVOICE_CREATE_PATH, self.vat))

    def get_sinvoice_update_payment_status_url(self):
        self.ensure_one()
        return urljoin(self._get_sinvoice_api_url(), SINVOICE_UPDATE_PAYMENT_STATUS_PATH)

    def get_sinvoice_cancel_payment_status_url(self):
        self.ensure_one()
        return urljoin(self._get_sinvoice_api_url(), SINVOICE_CANCEL_PAYMENT_STATUS_PATH)

    def get_sinvoice_cancel_url(self):
        self.ensure_one()
        return urljoin(self._get_sinvoice_api_url(), SINVOICE_CANCEL_PATH)

    def get_sinvoice_exchange_file_url(self):
        self.ensure_one()
        return urljoin(self._get_sinvoice_api_url(), SINVOICE_EXCHANGE_FILE_PATH)

    def get_sinvoice_presentation_file_url(self):
        self.ensure_one()
        return urljoin(self._get_sinvoice_api_url(), SINVOICE_PRESENTATION_FILE_PATH)

    def get_sinvoice_status_url(self):
        self.ensure_one()
        return urljoin(self._get_sinvoice_api_url(), SINVOICE_STATUS_PATH)

    def get_sinvoice_search_by_transaction_uuid_url(self):
        self.ensure_one()
        return urljoin(self._get_sinvoice_api_url(), SINVOICE_SEARCH_INVOICE_BY_TRANSACTION_UUID)

    def get_sinvoice_status(self):
        api_url = self.get_sinvoice_status_url()

        data = {
            'supplierTaxCode': self.vat,
            'templateCode': self.account_sinvoice_type_id.name,
            'serial': self.account_sinvoice_serial_id.name,
        }
        result = requests.post(
            api_url,
            json=data,
            headers={"Content-type": "application/json; charset=utf-8"},
            auth=(self.account_sinvoice_serial_id.name, self.sinvoice_api_password)
            )

        if result.status_code == 200:
            output = json.loads(result.text)
            if not output['errorCode'] and not output['description']:
                raise ValidationError("Số hóa đơn đã sử dụng %s / %s" % (output['numOfpublishInv'], output['totalInv']))
            else:
                raise ValidationError("%s\n%s" % (output['errorCode'], output['description']))
        else:
            raise ValidationError("Lỗi Kết Nối: %s" % (result.status_code))

    @api.model
    def _generate_sinvoice_config_params(self):
        """
        To be called from post_init_hook
        """
        Config = self.env['ir.config_parameter']
        Config.set_param('sinvoice_api_url', SINVOICE_API_URL)
        Config.set_param('sandbox_sinvoice_api_url', SANDBOX_SINVOICE_API_URL)

    @api.model
    def _update_sinvoice_settings(self):
        """
        To be called from post_init_hook
        """
        account_sinvoice_type_id = self.env.ref('to_accounting_sinvoice.sinvoice_type_01GTKT')
        account_sinvoice_template_id = self.env.ref('to_accounting_sinvoice.sinvoice_template_01GTKT0_001')
        self.search([]).write({
            'account_sinvoice_type_id': account_sinvoice_type_id.id,
            'account_sinvoice_template_id': account_sinvoice_template_id.id
            })

    # ----------------
    # Production
    # ----------------
    def _compute_sinvoice_api_url(self):
        ConfigParameter = self.env['ir.config_parameter'].sudo()
        sinvoice_api_url = ConfigParameter.get_param('sinvoice_api_url')
        for r in self:
            r.sinvoice_api_url = sinvoice_api_url

    def _set_sinvoice_api_url(self):
        sinvoice_api_url = self and self[0].sinvoice_api_url or False
        self.env['ir.config_parameter'].sudo().set_param('sinvoice_api_url', sinvoice_api_url)

    # ----------------
    # Sandbox
    # ----------------
    def _compute_sandbox_sinvoice_api_url(self):
        ConfigParameter = self.env['ir.config_parameter'].sudo()
        sandbox_sinvoice_api_url = ConfigParameter.get_param('sandbox_sinvoice_api_url')
        for r in self:
            r.sandbox_sinvoice_api_url = sandbox_sinvoice_api_url

    def _set_sandbox_sinvoice_api_url(self):
        sandbox_sinvoice_api_url = self and self[0].sandbox_sinvoice_api_url or False
        self.env['ir.config_parameter'].sudo().set_param('sandbox_sinvoice_api_url', sandbox_sinvoice_api_url)

