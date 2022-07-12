import base64
import json
from unittest.mock import patch
from unittest.mock import MagicMock
from datetime import date

from odoo.addons.viin_l10n_vn_accounting_vninvoice.models.einvoice_service import \
    VNINVOICE_LOGIN, \
    VNINVOICE_COMPANY_INFO, \
    VNINVOICE_CREATE_BATCH, \
    VNINVOICE_INVOICE_ADJUSTMENT
from odoo import fields
from odoo.modules.module import get_module_resource
from odoo.addons.l10n_vn_edi.tests.test_base import TestBaseEinvoiceCommon
from odoo.tests import Form



class TestVNinvoiceBaseCommon(TestBaseEinvoiceCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref='l10n_vn.vn_template'):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.tax_exemption_template = cls.env.ref('l10n_vn_c200.account_tax_template_sale_vat_exemption')
        cls.tax_exemption = cls.env['account.tax'].search([
            ('tax_group_id', '=', cls.env.ref('l10n_vn_c200.account_tax_template_sale_vat_exemption').id),
            ('type_tax_use', '=', 'sale'),
            ('company_id', '=', cls.company.id)
        ], limit=1)
        if not cls.tax_exemption:
            tax_id = cls.tax_exemption_template._generate_tax(cls.company)['tax_template_to_tax'][
                cls.tax_exemption_template.id]
            cls.tax_exemption = cls.env['account.tax'].browse(tax_id)
        cls.einvoice_service_vninvoice = cls.env['einvoice.service'].sudo().search([('provider', '=', 'vninvoice'),
                                                                   ('api_version', '=', 'v1')], limit=1)
        cls.einvoice_service_vninvoice.sudo().write({
            'company_id': cls.company.id,
            'sandbox_api_url': 'https://demo23bdo.vninvoice.vn',
            'api_url': 'https://domain-khachhang.vn',
            'sandbox_username': '0101333767-123',
            'sandbox_password': '0101333767-123',
            'start_date': date(2021, 8, 1)
            })
        serial_vninvoice = cls.env['account.einvoice.serial'].search([('name', '=', 'VN/21E')], limit=1)
        if not serial_vninvoice:
            serial_vninvoice = cls.env['account.einvoice.serial'].create([{
                'name': 'VN/21E',
                'einvoice_service_id': cls.einvoice_service_vninvoice.id,
                'template_id': cls.template.id
            }])
        cls.serial_vninvoice = serial_vninvoice

        # setup config
        cls.default_values.update({
            'einvoice_service_id': cls.einvoice_service_vninvoice.id,
        })
        ResCofig = cls.config.create(cls.default_values)
        ResCofig.flush()
        ResCofig.execute()

        # setup download file data
        with open(get_module_resource('viin_l10n_vn_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_representation_no_signed.pdf'),
                  'rb') as f:
            cls.VNinvoice_representation_no_signed_pdf = base64.b64encode(f.read()).decode()
        with open(get_module_resource('viin_l10n_vn_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_representation_signed.pdf'),
                  'rb') as f:
            cls.VNinvoice_representation_signed_pdf = base64.b64encode(f.read()).decode()
        with open(get_module_resource('viin_l10n_vn_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_representation_signed.xml'),
                  'rb') as f:
            cls.VNinvoice_representation_signed_xml = base64.b64encode(f.read()).decode()
        with open(get_module_resource('viin_l10n_vn_accounting_vninvoice', 'tests', 'download_files', 'VNinvoice_converted.pdf'),
                  'rb') as f:
            cls.VNinvoice_converted = base64.b64encode(f.read()).decode()
        with open(get_module_resource('viin_l10n_vn_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_representation_cancelled.pdf'),
                  'rb') as f:
            cls.VNinvoice_representation_cancelled_pdf = base64.b64encode(f.read()).decode()
        with open(get_module_resource('viin_l10n_vn_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_representation_cancelled.xml'),
                  'rb') as f:
            cls.VNinvoice_representation_cancelled_xml = base64.b64encode(f.read()).decode()
        with open(get_module_resource('viin_l10n_vn_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_converted_cancelled.pdf'),
                  'rb') as f:
            cls.VNinvoice_converted_cancelled = base64.b64encode(f.read()).decode()

        invoice = cls.init_invoice('out_invoice', invoice_date=cls.invoice_date,
                                   products=[cls.product_a, cls.product_b, cls.product_a])
        invoice.write({'access_token': 'access_token'})
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(2) as line_form:
            line_form.tax_ids.clear()
            line_form.tax_ids.add(cls.tax_exemption)
        invoice = invoice_form.save()
        cls.env['account.move.line'].create({
            'name': 'line note',
            'display_type': 'line_note',
            'move_id': invoice.id,
        })
        invoice.journal_id.account_einvoice_serial_id = cls.serial_vninvoice
        invoice.action_post()
        cls.invoice = invoice

    def setUp(self):
        super(TestVNinvoiceBaseCommon, self).setUp()
        self.sign_status = False
        self.cancel_invoice = False

    def mock_request_response(self, url, *args, **kwargs):
        """
        This function is called whenever the mock is called.
        it patches requests calling APIs and bases on url param of them to return corresponding datas.
        :param url (str): API URL
        :param args:
        :param kwargs:
        :return:
        """
        mock = MagicMock()
        return_value = {
            'succeeded': True,
            'code': 0,
            'message': 'Thành công',
        }
        if VNINVOICE_LOGIN in url:
            return_value.update({
                'data': {
                    'token': '123456',
                    'expireOn': '2021-08-27T10:32:31.021481Z',
                    'validFor': 30.0
                }
            })
        elif VNINVOICE_COMPANY_INFO in url:
            return_value.update({
                'data': {
                    'code': 'company_code',
                    'taxCode': '0304998358-040',
                    'address': '30 Bạch Đằng, Hải Phòng',
                    'city': 'Hải Phòng',
                    'district': 'Ngô Quyền',
                    'email': 'zuiqua@example.viindoo.com',
                    'fullName': 'Công ty cổ phần công nghệ Viindoo',
                    'dayOfUse': '2021-08-20T00:00:00',
                    'path': '6906d8b4-d8c5-43c4-a142-e77ce8e9bac3',
                    'idParent': '981aef5e-bb21-469e-8423-9c6bd156e1a7',
                    'idTaxDepartment': 2,
                    'domainName': 'demo23bdo.vninvoice.vn',
                    'id': '711e944d-c713-43d5-b027-08d62389be99',
                    'status': 'Active',
                    'createAt': '2018-09-27T06:42:06.818478',
                    'createBy': 'fa9c867e-7418-460e-ba2c-e38ac8eecaf4',
                    'updateAt': '2021-03-08T10:52:21.354476'
                }})
        elif VNINVOICE_CREATE_BATCH in url:
            return_value.update({
                'data': [{
                    'id': 'vninvoiceID',
                    'idErp': 'access_token',
                    'idTransaction': 'access_token',
                    'invoiceNo': '00001',
                    'invoiceStatus': 1,
                    'signStatus': 2
                }]
            })
        elif '/api/01gtkt?FromDate=' in url:
            if not self.sign_status:
                return_value = [{
                    'id': 'vninvoiceID',
                    'idErp': 'access_token',
                    'idTransaction': 'access_token',
                    'invoiceNo': '00001',
                    'invoiceStatus': 1,
                    'signStatus': 2,
                    'idFileOfRecord': 'access_token'
                }]
            elif not self.sign_status and self.cancel_invoice:
                return_value = [{
                    'id': 'vninvoiceID',
                    'idErp': 'access_token',
                    'idTransaction': 'access_token',
                    'invoiceNo': '00001',
                    'invoiceStatus': 9,
                    'signStatus': 2,
                    'idFileOfRecord': 'access_token'
                }]
            elif self.sign_status and not self.cancel_invoice:
                return_value = [{
                    'id': 'vninvoiceID',
                    'idErp': 'access_token',
                    'idTransaction': 'access_token',
                    'invoiceNo': '00001',
                    'invoiceStatus': 1,
                    'signStatus': 5,
                    'idFileOfRecord': 'access_token'
                }]
            else:
                return_value = [{
                    'id': 'vninvoiceID',
                    'idErp': 'access_token',
                    'idTransaction': 'access_token',
                    'invoiceNo': '00001',
                    'invoiceStatus': 2,
                    'signStatus': 5,
                    'idFileOfRecord': 'access_token'
                }]
        elif '/api/01gtkt/approve-and-sign/' in url:
            return_value.update({
                'data': [{
                    'id': 'vninvoiceID',
                    'idErp': 'access_token',
                    'idTransaction': 'access_token',
                    'invoiceNo': '00001',
                    'invoiceStatus': 1,
                    'signStatus': 5
                }]
            })
        elif '/api/01gtkt/unofficial?Ids=' in url:
            if not self.sign_status:
                return_value.update({
                    'data': {
                        'id': 'access_token',
                        'data': self.VNinvoice_representation_no_signed_pdf,
                    }
                })
            elif self.sign_status and not self.cancel_invoice:
                return_value.update({
                    'data': {
                        'id': 'access_token',
                        'data': self.VNinvoice_representation_signed_pdf,
                    }
                })
            else:
                return_value.update({
                    'data': {
                        'id': 'access_token',
                        'data': self.VNinvoice_representation_cancelled_pdf,
                    }
                })
        elif '/01gtkt/download/xml/' in url:
            if not self.sign_status:
                mock.status_code = 500
                mock.reason = "download xml of not signed invoice"
            elif self.sign_status and not self.cancel_invoice:
                return_value.update({
                    'data': {
                        'base64': self.VNinvoice_representation_signed_xml,
                        'fileName': 'VNinvoice_representation_signed.xml',
                    }
                })
            else:
                return_value.update({
                    'data': {
                        'base64': self.VNinvoice_representation_cancelled_xml,
                        'fileName': 'VNinvoice_representation_cancelled.xml',
                    }
                })
        elif '01gtkt/download/official' in url:
            if not self.sign_status:
                mock.status_code = 500
                mock.reason = "download xml of not signed invoice"
            elif self.sign_status and not self.cancel_invoice:
                return_value.update({
                    'data': {
                        'base64': self.VNinvoice_converted,
                        'fileName': 'VNinvoice_converted.pdf',
                    }
                })
            else:
                return_value.update({
                    'data': {
                        'base64': self.VNinvoice_converted_cancelled,
                        'fileName': 'VNinvoice_converted_cancelled.pdf',
                    }
                })
        elif '/api/01gtkt/delete/' in url:
            self.cancel_invoice = True
            if not self.sign_status:
                return_value.update({
                    'data': [{
                        'id': 'vninvoiceID',
                        'idErp': 'access_token',
                        'idTransaction': 'access_token',
                        'invoiceNo': '00001',
                        'invoiceStatus': 9,
                        'signStatus': 5
                    }]
                })
            else:
                return_value.update({
                    'data': [{
                        'id': 'vninvoiceID',
                        'idErp': 'access_token',
                        'idTransaction': 'access_token',
                        'invoiceNo': '00001',
                        'invoiceStatus': 2,
                        'signStatus': 5
                    }]
                })
        elif VNINVOICE_INVOICE_ADJUSTMENT in url:
            return_value.update({
                'data': {
                    'id': 'vninvoiceID',
                    'idErp': 'access_token',
                    'idTransaction': 'access_token',
                    'invoiceNo': '00001',
                    'invoiceStatus': 1,
                    'signStatus': 2
                }
            })
        else:
            mock.status_code = 500
            mock.reason = "url not exit"
        data_json = json.dumps(return_value)
        mock.text = data_json
        return mock


    def run(self, result=None):
        with patch('odoo.addons.viin_l10n_vn_accounting_vninvoice.models.account_move.requests.post',
                  self.mock_request_response), \
            patch('odoo.addons.viin_l10n_vn_accounting_vninvoice.models.account_move.requests.patch',
                  self.mock_request_response):
            super(TestVNinvoiceBaseCommon, self).run(result)

    def download_vninvoice(self):
        self.invoice.get_einvoice_representation_files()
        if self.invoice.check_einvoice_approved_and_signed:
            self.invoice.get_einvoice_converted_files()

    def issue_vninvoice(self, paid=False):
        if paid:
            self.create_payment(self.invoice)
        self.invoice.issue_einvoices()


    def sign_invoice(self):
        self.invoice.action_approve_and_sign()
        self.sign_status = True

    def check_invoice_signed(self):
        self.invoice.with_context(active_ids=self.invoice.ids)._action_check_vninvoices_signed()
