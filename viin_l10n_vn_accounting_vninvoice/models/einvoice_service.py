import requests, json
from urllib.parse import urljoin, urlparse

from odoo import models, fields, _
from odoo.exceptions import ValidationError

SANDBOX_VNINVOICE_API_URL = 'https://demo23bdo.vninvoice.vn'
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
VNINVOICE_DOWNLOAD_XML_V2 = '/api/01gtkt/download-xml/{iderp}'
VNINVOICE_INVOICE_INFO = '/api/01gtkt?FromDate={fromdate}&ToDate={todate}'
VNINVOICE_INVOICE_INFO_V2 = '/api/01gtkt/info'
VNINVOICE_INVOICE_ADJUSTMENT = '/api/01gtkt/auto-adjustment-detail'
VNINVOICE_INVOICE_ADJUSTMENT_V2 = '/api/01gtkt/adjustment-detail'
VNINVOICE_INVOICE_ERROR_NOTIFICATION = '/api/01gtkt/invoice-error/create'
VNINVOICE_INVOICE_SIGN_ERROR_NOTIFICATION = '/api/01gtkt/signserver/invoice01-error'
VNINVOICE_INVOICE_DELETE_ERROR_NOTIFICATION = '/api/01gtkt/invoice-error/delete'

class EinvoiceService(models.Model):
    _inherit = 'einvoice.service'

    provider = fields.Selection(selection_add=[('vninvoice', 'VN-Invoice')],
                                         ondelete={'vninvoice': 'set default'})

    def _get_vninvoice_domain_name(self):
        """
        return domain name according to the VN-invoice Mode which is either sandbox or production
        """
        self.ensure_one()
        return urlparse(self._get_einvoice_api_url()).netloc

    def get_vninvoice_login_url(self):
        self.ensure_one()
        if self.api_version == 'v1':
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_LOGIN)
        else:
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_LOGIN_V2)

    def get_vninvoice_company_info_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), VNINVOICE_COMPANY_INFO)

    def get_vninvoice_create_batch_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), VNINVOICE_CREATE_BATCH)

    def get_vninvoice_approve_and_sign_url(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), VNINVOICE_APPROVE_AND_SIGN)

    def get_vninvoice_delete_url(self):
        self.ensure_one()
        return  urljoin(self._get_einvoice_api_url(), VNINVOICE_DELETE)

    def get_vninvoice_cancel_unsign_url(self):
        self.ensure_one()
        return  urljoin(self._get_einvoice_api_url(), VNINVOICE_CANCEL)

    def get_vninvoice_unofficial_url(self):
        self.ensure_one()
        if self.api_version == 'v1':
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_UNOFFICIAL)
        else:
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_UNOFFICIAL_V2)

    def get_vninvoice_official_url(self):
        self.ensure_one()
        if self.api_version == 'v1':
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_OFFICIAL.format(self.get_vninvoice_company_code()))
        else:
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_OFFICIAL_V2)

    def get_vninvoice_download_xml_url(self):
        self.ensure_one()
        if self.api_version == 'v1':
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_DOWNLOAD_XML)
        else:
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_DOWNLOAD_XML_V2)


    def get_vninvoice_invoice_info_url(self):
        self.ensure_one()
        if self.api_version == 'v1':
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_INVOICE_INFO)
        else:
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_INVOICE_INFO_V2)

    def get_vninvoice_invoice_adjustment(self):
        self.ensure_one()
        if self.api_version == 'v1':
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_INVOICE_ADJUSTMENT)
        else:
            return urljoin(self._get_einvoice_api_url(), VNINVOICE_INVOICE_ADJUSTMENT_V2)

    def get_vninvoice_invoice_error_notification(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), VNINVOICE_INVOICE_ERROR_NOTIFICATION)

    def get_vninvoice_invoice_sign_error_notification(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), VNINVOICE_INVOICE_SIGN_ERROR_NOTIFICATION)

    def get_vninvoice_invoice_delete_error_notification(self):
        self.ensure_one()
        return urljoin(self._get_einvoice_api_url(), VNINVOICE_INVOICE_DELETE_ERROR_NOTIFICATION)
    # ----------------
    # Get token key of VNinvoice
    # ----------------


    def get_vninvoice_api_token(self):
        """
        Get API token of VN-invoice to access VN-invoice system in given duration
        """
        api_url = self.get_vninvoice_login_url()
        data = {
                "userName": self.username if self.mode == 'production' else self.sandbox_username,
                "password": self.password if self.mode == 'production' else self.sandbox_password,
                "domainName": self._get_vninvoice_domain_name()
            }
        if self.api_version == 'v1':
            data.update({
                "domainName": self._get_vninvoice_domain_name()
            })
        else:
            data.update({
                "taxCode": self.company_id.vat
            })
        try:
            result = requests.post(api_url, json=data, headers={"Content-type": "application/json"})
            result.raise_for_status()
            output = json.loads(result.text)
            if self.api_version == 'v1':
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
            output = json.loads(result.text)
            if not output['succeeded']:
                raise  ValidationError(_('Log in VN-Invoice system unsuccessfully. Error: %s') % (output['message']))
            else:
                company_code = output['data']['code']
        except requests.HTTPError as e:
            content = json.loads(e.response.content.decode('utf-8') or '{"errorCode": %s}' % e.response.status_code).get('error', {}).get('details', '')
            raise  ValidationError(_("Something went wrong when log in VN-Invoice system. Here is the debugging information:\n%s") % (str(content)))
        return company_code
