import requests, json
from urllib.parse import urljoin, urlparse

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

SANDBOX_VNINVOICE_API_URL = 'https://demo.vninvoice.vn'
VNINVOICE_API_URL = 'https://domain-khachhang.vn'
VNINVOICE_LOGIN = '/login'
VNINVOICE_LOGIN_V2 = '/api/system/account/login'
VNINVOICE_COMPANY_INFO = '/company/info'
VNINVOICE_CREATE_BATCH = '/api/01gtkt/create-batch'
VNINVOICE_APPROVE_AND_SIGN = '/api/01gtkt/approve-and-sign/{}'
VNINVOICE_DELETE = '/api/01gtkt/delete/{}'
VNINVOICE_CANCEL = '/api/01gtkt/cancel/{}'
VNINVOICE_UNOFFICIAL = '/api/01gtkt/unofficial?Ids={}'
VNINVOICE_UNOFFICIAL_V2 = '/api/01gtkt/unofficial/{}'
VNINVOICE_OFFICIAL = '/{}/01gtkt/download/official'
VNINVOICE_OFFICIAL_V2 = '/api/01gtkt/official/{}'
VNINVOICE_DOWNLOAD_XML = '/{manoibo}/01gtkt/download/xml/{iderp}'
VNINVOICE_DOWNLOAD_XML_V2 = '/api/01gtk/api/01gtkt/download-xml/{iderp}'
VNINVOICE_INVOICE_INFO = '/api/01gtkt?FromDate={fromdate}&ToDate={todate}'
VNINVOICE_INVOICE_INFO_V2 = '/api/01gtkt/info'
VNINVOICE_INVOICE_ADJUSTMENT = '/api/01gtkt/auto-adjustment-detail'
VNINVOICE_INVOICE_ADJUSTMENT_V2 = '/api/01gtkt/adjustment-detail'
VNINVOICE_INVOICE_ERROR_NOTIFICATION = '/api/01gtkt/invoice-error/create'
VNINVOICE_INVOICE_SIGN_ERROR_NOTIFICATION = '/api/01gtkt/signserver/invoice01-error'
VNINVOICE_INVOICE_DELETE_ERROR_NOTIFICATION = '/api/01gtkt/invoice-error/delete'

class ResCompany(models.Model):
    _inherit = 'res.company'

    einvoice_provider = fields.Selection(selection_add=[('vninvoice', 'VN-Invoice')])
    vninvoice_mode = fields.Selection([('sandbox', 'Sandbox'), ('production', 'Production')], default='sandbox', copy=False, required=True,
                                        string='VN-invoice Mode', help="Choose Sandbox mode for testing before switch it to Production")
    vninvoice_start_date = fields.Date(string='VN-Invoice Start Date', help="The date from which your company announced the start of using VN-Invoice.")
    vninvoice_api_url = fields.Char(string='VNInvoice API URL', compute='_compute_vninvoice_api_url', inverse='_set_vninvoice_api_url')
    sandbox_vninvoice_api_url = fields.Char(string='VNInvoice Sandbox API URL', compute='_compute_sandbox_vninvoice_api_url',
                                           inverse='_set_sandbox_vninvoice_api_url')
    account_vninvoice_serial_id = fields.Many2one('account.vninvoice.serial', string='VNInvoice Invoice Serial',
                                                 ondelete='restrict',
                                                 help="The prefix (e.g. AA/16E, AA/17E, etc) of the"
                                                      " invoice number that must be registered with VN-Invoice priorily. See the Circular No. 39/2014/TT-BTC"
                                                      " dated March 31, 2014 by The Ministry of Finance of Vietnam.")
    account_vninvoice_template_id = fields.Many2one('account.vninvoice.template', string='VN-Invoice Template',
                                                   ondelete='restrict',
                                                   help="The template that you have registered with"
                                                        " VN-Invoice for rendering your invoices of this template")
    account_vninvoice_type_id = fields.Many2one('account.vninvoice.type', string='VN-Invoice Type', ondelete='restrict',
                                               help="The invoice type provided by VN-Invoice.")
    vninvoice_api_username = fields.Char('VN-Invoice username', copy=False)
    vninvoice_api_password = fields.Char('VN-Invoice password', copy=False)

    def _get_vninvoice_api_url(self):
        """
        Return VN-invoice API URL according to the VN-invoice Mode which is either sandbox or production
        """
        self.ensure_one()
        return self.vninvoice_api_url if self.vninvoice_mode == 'production' else self.sandbox_vninvoice_api_url

    def _get_vninvoice_domain_name(self):
        """
        return domain name according to the VN-invoice Mode which is either sandbox or production
        """
        self.ensure_one()
        return urlparse(self._get_vninvoice_api_url()).netloc

    def get_vninvoice_login_url(self):
        self.ensure_one()
        if self.einvoice_api_version == 'v1':
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_LOGIN)
        else:
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_LOGIN_V2)

    def get_vninvoice_company_info_url(self):
        self.ensure_one()
        return urljoin(self._get_vninvoice_api_url(), VNINVOICE_COMPANY_INFO)
    
    def get_vninvoice_create_batch_url(self):
        self.ensure_one()
        return urljoin(self._get_vninvoice_api_url(), VNINVOICE_CREATE_BATCH)

    def get_vninvoice_approve_and_sign_url(self):
        self.ensure_one()
        return urljoin(self._get_vninvoice_api_url(), VNINVOICE_APPROVE_AND_SIGN)

    def get_vninvoice_delete_url(self):
        self.ensure_one()
        return  urljoin(self._get_vninvoice_api_url(), VNINVOICE_DELETE)
    
    def get_vninvoice_cancel_unsign_url(self):
        self.ensure_one()
        return  urljoin(self._get_vninvoice_api_url(), VNINVOICE_CANCEL)

    def get_vninvoice_unofficial_url(self):
        self.ensure_one()
        if self.einvoice_api_version == 'v1':
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_UNOFFICIAL)
        else:
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_UNOFFICIAL_V2)
    
    def get_vninvoice_official_url(self):
        self.ensure_one()
        if self.einvoice_api_version == 'v1':
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_OFFICIAL.format(self.get_vninvoice_company_code()))
        else:
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_OFFICIAL_V2)
    
    def get_vninvoice_download_xml_url(self):
        self.ensure_one()
        if self.einvoice_api_version == 'v1':
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_DOWNLOAD_XML)
        else:
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_DOWNLOAD_XML_V2)

    
    def get_vninvoice_invoice_info_url(self):
        self.ensure_one()
        if self.einvoice_api_version == 'v1':
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_INVOICE_INFO)
        else:
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_INVOICE_INFO_V2)

    def get_vninvoice_invoice_adjustment(self):
        self.ensure_one()
        if self.einvoice_api_version == 'v1':
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_INVOICE_ADJUSTMENT)
        else:
            return urljoin(self._get_vninvoice_api_url(), VNINVOICE_INVOICE_ADJUSTMENT_V2)

    def get_vninvoice_invoice_error_notification(self):
        self.ensure_one()
        return urljoin(self._get_vninvoice_api_url(), VNINVOICE_INVOICE_ERROR_NOTIFICATION)

    def get_vninvoice_invoice_sign_error_notification(self):
        self.ensure_one()
        return urljoin(self._get_vninvoice_api_url(), VNINVOICE_INVOICE_SIGN_ERROR_NOTIFICATION)

    def get_vninvoice_invoice_delete_error_notification(self):
        self.ensure_one()
        return urljoin(self._get_vninvoice_api_url(), VNINVOICE_INVOICE_DELETE_ERROR_NOTIFICATION)
    # ----------------
    # Get token key of VNinvoice
    # ----------------


    def get_vninvoice_api_token(self):
        """
        Get API token of VN-invoice to access VN-invoice system in given duration
        """
        api_url = self.get_vninvoice_login_url()
        data = {
                "userName": self.vninvoice_api_username,
                "password": self.vninvoice_api_password,
            }

        if self.einvoice_api_version == 'v1':
            data.update({
                "domainName": self._get_vninvoice_domain_name()
            })
        else:
            data.update({
                "taxCode": self.vat
            })
        try:
            result = requests.post(api_url, json=data, headers={"Content-type": "application/json"})
            result.raise_for_status()
            output = json.loads(result.text)
            if self.einvoice_api_version == 'v1':
                if not output['succeeded']:
                    raise ValidationError(_('Log in VN-Invoice system unsuccessfully. Error: %s') % (output['message']))
                else:
                    token = output['data']['token']
            else:
                if not output.get('accessToken', False):
                    raise ValidationError(_('Log in VN-Invoice system unsuccessfully. You should check the account configuration in setting'))
                else:
                    token = output['accessToken']
        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code)
            raise  ValidationError(_("Something went wrong when log in VN-Invoice system. Here is the debugging information:\n%s") % (str(content)))
        return token
    
    # ----------------
    # Get company code of VNinvoice
    # ----------------
    def get_vninvoice_company_code(self):
        """
        Get company Code of VN-invoice to download VN-invoice files (zip, converted file)
        """
        api_url = self.get_vninvoice_company_info_url()
        company_code = ''
        try:
            result = requests.get(api_url, headers={"Authorization": "Bearer {}".format(self.get_vninvoice_api_token())})
            result.raise_for_status()
            output = json.loads(result.text)
            if not output['succeeded']:
                raise  ValidationError(_('Log in VN-Invoice system unsuccessfully. Error: %s') % (output['message']))
            else:
                company_code = output['data']['code']
        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code).get('error', {}).get('details', '')
            raise  ValidationError(_("Something went wrong when log in VN-Invoice system. Here is the debugging information:\n%s") % (str(content)))
        return company_code
    
    # ----------------
    @api.model
    def _generate_vninvoice_config_params(self):
        """To be called from post_init_hook"""
        Config = self.env['ir.config_parameter']
        Config.set_param('vninvoice_api_url', VNINVOICE_API_URL)
        Config.set_param('sandbox_vninvoice_api_url', SANDBOX_VNINVOICE_API_URL)

    # ----------------
    # Production
    # ----------------
    def _compute_vninvoice_api_url(self):
        ConfigParameter = self.env['ir.config_parameter'].sudo()
        vninvoice_api_url = ConfigParameter.get_param('vninvoice_api_url')
        for r in self:
            r.vninvoice_api_url = vninvoice_api_url
            
    def _set_vninvoice_api_url(self):
        vninvoice_api_url = self and self[0].vninvoice_api_url or False
        self.env['ir.config_parameter'].sudo().set_param('vninvoice_api_url', vninvoice_api_url)

    # ----------------
    # Sandbox
    # ----------------
    def _compute_sandbox_vninvoice_api_url(self):
        ConfigParameter = self.env['ir.config_parameter'].sudo()
        sandbox_vninvoice_api_url = ConfigParameter.get_param('sandbox_vninvoice_api_url')
        for r in self:
            r.sandbox_vninvoice_api_url = sandbox_vninvoice_api_url
            
    def _set_sandbox_vninvoice_api_url(self):
        sandbox_vninvoice_api_url = self and self[0].sandbox_vninvoice_api_url or False
        self.env['ir.config_parameter'].sudo().set_param('sandbox_vninvoice_api_url', sandbox_vninvoice_api_url)