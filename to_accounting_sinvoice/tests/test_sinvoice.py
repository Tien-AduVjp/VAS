import base64
import json
import requests
from unittest.mock import patch, MagicMock
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import fields
from odoo.modules.module import get_module_resource
from odoo.addons.to_einvoice_common.tests.test_base import TestBaseEinvoiceCommon
from odoo.addons.to_accounting_sinvoice.models.res_company import \
    SINVOICE_PRESENTATION_FILE_PATH, \
    SINVOICE_EXCHANGE_FILE_PATH, \
    SINVOICE_CANCEL_PATH, \
    SINVOICE_CREATE_PATH, \
    SINVOICE_UPDATE_PAYMENT_STATUS_PATH, \
    SINVOICE_CANCEL_PAYMENT_STATUS_PATH, \
    SINVOICE_SEARCH_INVOICE_BY_TRANSACTION_UUID
from odoo.tests import tagged, Form
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestSinvoice(TestBaseEinvoiceCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref='l10n_vn.vn_template'):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.template = cls.env.ref('to_accounting_sinvoice.sinvoice_template_01GTKT0_001')
        serial = cls.env['account.sinvoice.serial'].search([('name', '=', 'AA/20E')], limit=1)
        if not serial:
            serial = cls.env['account.sinvoice.serial'].create({
                'name': 'AA/20E',
                'template_id': cls.template.id
            })
        cls.serial = serial
        cls.tax_exemption_template = cls.env.ref('l10n_vn_c200.tax_sale_vat_exemption')
        cls.tax_exemption = cls.env['account.tax'].search([
            ('tax_group_id', '=', cls.env.ref('l10n_vn_c200.tax_group_exemption').id),
            ('type_tax_use', '=', 'sale'),
            ('company_id', '=', cls.company.id)
        ], limit=1)
        if not cls.tax_exemption:
            tax_id = cls.tax_exemption_template._generate_tax(cls.company)['tax_template_to_tax'][
                cls.tax_exemption_template.id]
            cls.tax_exemption = cls.env['account.tax'].browse(tax_id)

        cls.default_values.update({
            'einvoice_provider': 'sinvoice',
            'sinvoice_api_username': 'khaihoan',
            'sinvoice_api_password': 'khaihoan',
            'sinvoice_start': fields.Date.to_date('2021-08-01'),
            'account_sinvoice_serial_id': cls.serial.id,
            'sinvoice_synch_payment_status': True,
            'sinvoice_conversion_user_id': False,
        })
        ResCofig = cls.config.create(cls.default_values)
        ResCofig._onchange_account_sinvoice_serial()
        ResCofig._onchange_account_sinvoice_template()
        ResCofig.flush()
        ResCofig.execute()

        # setup download file data
        with open(get_module_resource('to_accounting_sinvoice', 'tests', 'download_files',
                                      'representation_file.pdf'),
                  'rb') as f:
            cls.representation_pdf = base64.b64encode(f.read()).decode()
        with open(get_module_resource('to_accounting_sinvoice', 'tests', 'download_files',
                                      'representation_file.zip'),
                  'rb') as f:
            cls.representation_zip = base64.b64encode(f.read()).decode()
        with open(get_module_resource('to_accounting_sinvoice', 'tests', 'download_files',
                                      'converted_file.pdf'),
                  'rb') as f:
            cls.converted_file = base64.b64encode(f.read()).decode()
        with open(get_module_resource('to_accounting_sinvoice', 'tests', 'download_files', 'representation_file_cancelled.pdf'),
                  'rb') as f:
            cls.representation_file_cancelled_pdf = base64.b64encode(f.read()).decode()
        with open(get_module_resource('to_accounting_sinvoice', 'tests', 'download_files',
                                      'representation_file_cancelled.zip'),
                  'rb') as f:
            cls.representation_file_cancelled_zip = base64.b64encode(f.read()).decode()
        invoice = cls.create_invoice(invoice_date=cls.invoice_date, post=False)
        invoice.write({'access_token': 'access_token'})
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = cls.product_a
            line_form.tax_ids.clear()
            line_form.tax_ids.add(cls.tax_exemption)
        invoice_form.save()
        cls.env['account.move.line'].create({
            'name': 'line note',
            'display_type': 'line_note',
            'move_id': invoice.id,
        })
        invoice.action_post()
        cls.invoice = invoice

    def setUp(self):
        super(TestSinvoice, self).setUp()
        self.cancel_invoice = False

    def mock_request_response(self, url, *args, data=None, **kwargs):
        """
        This function is called whenever the mock is called.
        it patches actions calling APIs and bases on params of them to return corresponding datas.
        :param url (str): API URL
        :param args:
        :param kwargs:
        :return:
        """
        mock = MagicMock()
        data = data if isinstance(data, dict) else json.loads(data)
        return_value = {
            'errorCode': None,
            'description': None,
        }
        if SINVOICE_CREATE_PATH in url:
            return_value.update({
                'result': {
                    'supplierTaxCode': '0201994665',
                    'invoiceNo': 'AA/20E0000001',
                    'transactionID': 'access_token',
                    'reservationCode': 'AXHBNK8I0H',
                }
            })
        elif SINVOICE_UPDATE_PAYMENT_STATUS_PATH in url or SINVOICE_CANCEL_PAYMENT_STATUS_PATH in url:
            return_value.update({
                'result': True,
                'paymentTime': '',
                'paymentMethod': 'TM/CK',
            })
        elif SINVOICE_PRESENTATION_FILE_PATH in url:
            if not self.cancel_invoice:
                if data['fileType'] == 'PDF':
                    return_value.update({
                        'fileName': 'representation_file',
                        'fileToBytes': self.representation_pdf,
                    })
                elif data['fileType'] == 'ZIP':
                    return_value.update({
                        'fileName': 'representation_file',
                        'fileToBytes': self.representation_zip,
                    })
                else:
                    return_value = None
            else:
                if data['fileType'] == 'PDF':
                    return_value.update({
                        'fileName': 'representation_file_cancelled',
                        'fileToBytes': self.representation_file_cancelled_pdf,
                    })
                elif data['fileType'] == 'ZIP':
                    return_value.update({
                        'fileName': 'representation_file_cancelled',
                        'fileToBytes': self.representation_file_cancelled_zip,
                    })
                else:
                    return_value = None
        elif SINVOICE_EXCHANGE_FILE_PATH in url:
            return_value.update({
                'fileName': 'converted_file',
                'fileToBytes': self.converted_file,
            })
        elif SINVOICE_CANCEL_PATH in url:
            self.cancel_invoice = True
        elif SINVOICE_SEARCH_INVOICE_BY_TRANSACTION_UUID in url:
            return_value.update({
                'result': [{'status': 'Hóa đơn xóa bỏ'}],
            })
        else:
            mock.status_code = 500
            mock.reason = "url not exit"
        mock.json.return_value = return_value
        return mock

    def run(self, result=None):
        with patch('odoo.addons.to_accounting_sinvoice.models.account_move.requests.post', self.mock_request_response):
            super(TestSinvoice, self).run(result)

    def download_sinvoice(self):
        self.issue_sinvoice()
        self.invoice.get_einvoice_representation_files()
        self.invoice.get_einvoice_converted_files()

    def issue_sinvoice(self, paid=False):
        if paid:
            self.create_payment(amount=self.invoice.amount_total, invoice_ids=[(6, 0, self.invoice.ids)])
        self.invoice.issue_einvoices()

    def test_01_check_data_after_setup_sinvoice(self):
        self.assertRecordValues(self.company, [
            {'account_sinvoice_template_id': self.template.id, 'account_sinvoice_type_id': self.template.type_id.id}])
        self.assertTrue(self.company_data['default_journal_sale'].einvoice_enabled)

    def test_02_sinvoice_api_url(self):
        self.company._generate_sinvoice_config_params()
        self.assertEqual(self.company._get_sinvoice_api_url(), 'https://demo-sinvoice.viettel.vn:8443')
        self.company.write({'sinvoice_mode': 'production'})
        self.assertEqual(self.company._get_sinvoice_api_url(), 'https://api-sinvoice.viettel.vn:443')
        self.company.write({'sinvoice_api_url': 'https://api-sinvoice.viettel.vn:443//'})
        self.assertEqual(self.company.get_sinvoice_create_url(),
                         'https://api-sinvoice.viettel.vn:443/InvoiceAPI/InvoiceWS/createInvoice/0201994665')

    def test_03_cannot_issue_invoice(self):
        self.check_issue_einvoice_raise_excep()
        with self.assertRaises(UserError, msg="Product name too long"):
            with self.env.cr.savepoint():
                self.company_data['default_journal_sale'].write({'einvoice_item_name_limit': 10})
                with self.patch_date_today(date(2021, 9, 1)):
                    self.invoice.issue_einvoices()
        with self.assertRaises(ValidationError, msg="Bank Name or Bank Account Too long"):
            self.company.write({
                'sinvoice_max_len_bank_name': 13,
                'sinvoice_max_len_bank_account': 8,
            })
            with self.patch_date_today(date(2021, 9, 1)):
                self.invoice.issue_einvoices()

    def test_04_issue_invoice(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_sinvoice()
        self.assertRecordValues(self.invoice, [{
            'legal_number': 'AA/20E0000001',
            'einvoice_state': 'issued',
            'sinvoice_transactionid': 'access_token',
        }])

    def test_05_issue_paid_invoice(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_sinvoice(paid=True)
        self.assertRecordValues(self.invoice, [{
            'legal_number': 'AA/20E0000001',
            'einvoice_state': 'paid',
            'sinvoice_transactionid': 'access_token',
        }])

    def test_06_sinvoice_synch_payment_status(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.invoice.issue_einvoices()
        self.assertRecordValues(self.invoice, [{
            'legal_number': 'AA/20E0000001',
            'einvoice_state': 'issued',
            'sinvoice_transactionid': 'access_token',
        }])
        payment = self.create_payment(amount=self.invoice.amount_total, invoice_ids=[(6, 0, self.invoice.ids)])
        self.assertRecordValues(self.invoice, [{
            'einvoice_state': 'paid',
        }])
        payment.move_line_ids.filtered(lambda r: r.account_id.internal_type == 'receivable').with_context(
            move_id=self.invoice.id).remove_move_reconcile()
        self.assertRecordValues(self.invoice, [{
            'einvoice_state': 'issued',
        }])

    def test_07_download_file(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.download_sinvoice()
        self.assertTrue(self.invoice.sinvoice_representation_pdf)
        self.assertTrue(self.invoice.sinvoice_representation_zip)
        self.assertEqual(self.invoice.sinvoice_representation_filename_pdf, 'representation_file.pdf')
        self.assertEqual(self.invoice.sinvoice_representation_filename_zip, 'representation_file.zip')
        self.assertTrue(self.invoice.sinvoice_converted_file)
        self.assertEqual(self.invoice.sinvoice_converted_filename, 'converted_file.pdf')

    def test_08_download_file_with_cron(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_sinvoice()
        self.invoice._cron_ensure_einvoice_download_file()
        self.assertTrue(self.invoice.sinvoice_representation_pdf)
        self.assertTrue(self.invoice.sinvoice_representation_zip)
        self.assertEqual(self.invoice.sinvoice_representation_filename_pdf, 'representation_file.pdf')
        self.assertEqual(self.invoice.sinvoice_representation_filename_zip, 'representation_file.zip')
        self.assertTrue(self.invoice.sinvoice_converted_file)
        self.assertEqual(self.invoice.sinvoice_converted_filename, 'converted_file.pdf')

    def test_09_cancel_sinvoice(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_sinvoice(paid=True)
        # self.invoice.button_draft()
        # self.invoice.button_cancel()
        with self.assertRaises(ValidationError, msg="Cancelling date in the future"):
            self.env['account.invoice.einvoice.cancel'].create({
                'invoice_id': self.invoice.id,
                'additional_reference_desc': 'khaihoan_cancel',
                'additional_reference_date': fields.Datetime.now() + relativedelta(months=1),
            })
        with self.assertRaises(ValidationError, msg="Cancelling date in the pass"):
            self.env['account.invoice.einvoice.cancel'].create({
                'invoice_id': self.invoice.id,
                'additional_reference_desc': 'khaihoan_cancel',
                'additional_reference_date': fields.Datetime.now() - relativedelta(months=1),
            })
        with self.assertRaises(ValidationError, msg="cancel with cancellation_record be not pdf file"):
            wizard = self.env['account.invoice.einvoice.cancel'].create({
                'invoice_id': self.invoice.id,
                'additional_reference_desc': 'khaihoan_cancel',
                'additional_reference_date': fields.Datetime.now() - relativedelta(months=1),
                'cancellation_record': self.representation_file_cancelled_zip,
            })
            wizard.action_cancel_einvoice()
        wizard = self.env['account.invoice.einvoice.cancel'].create({
            'invoice_id': self.invoice.id,
            'additional_reference_desc': 'khaihoan_cancel',
            'additional_reference_date': fields.Datetime.now(),
            'cancellation_record': self.representation_file_cancelled_pdf,
        })
        wizard.action_cancel_einvoice()
        self.assertEqual(self.invoice.einvoice_state, 'cancelled')
        self.assertEqual(self.invoice.sinvoice_representation_pdf.decode(), self.representation_file_cancelled_pdf)
        self.assertEqual(self.invoice.sinvoice_representation_zip.decode(), self.representation_file_cancelled_zip)
        self.assertEqual(self.invoice.cancellation_record.decode(), self.representation_file_cancelled_pdf)
        self.assertEqual(self.invoice.sinvoice_representation_filename_pdf, 'representation_file_cancelled.pdf')
        self.assertEqual(self.invoice.sinvoice_representation_filename_zip, 'representation_file_cancelled.zip')

    def test_10_edit_template_type_serial_assigned_to_invoices(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_sinvoice()
        with self.assertRaises(UserError):
            self.serial.write({'name': 'khaihoan'})
        with self.assertRaises(UserError):
            self.template.write({'name': 'khaihoan'})
        with self.assertRaises(UserError):
            self.template.type_id.write({'name': 'khaihoan'})


    # def test_12_send_email_with_download_files(self):
    #     with self.patch_date_today(date(2021, 9, 1)):
    #         self.download_sinvoice()
    #     action_mail = self.invoice.action_invoice_sent()
    #     mail_form = Form(
    #         self.env['account.invoice.send'].with_context(**action_mail['context'], active_ids=self.invoice.ids,
    #                                                       force_report_rendering=True))
    #     mail = mail_form.save()
    #     attachments = mail.attachment_ids
    #     self.assertEqual(self.invoice.sinvoice_representation_zip, attachments[0].datas)

    def test_13_cannnot_edit_legal_number(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_sinvoice()
        invoice_form = Form(self.invoice)
        with self.assertRaises(AssertionError):
            invoice_form.legal_number = '00001'

    # --------------------------------------------------
    # TEST METHODS
    # --------------------------------------------------

    def test_14_prepare_sinvoice_tax_breakdowns(self):
        result = self.invoice._prepare_sinvoice_tax_breakdowns()
        self.assertEqual(result, [
            {'taxPercentage': 10.0, 'taxableAmount': 1200.0, 'taxAmount': 120.0},
            {'taxPercentage': -2, 'taxableAmount': 1000.0, 'taxAmount': 0}
        ])

    def test_15_prepare_einvoice_lines_data(self):
        result = self.invoice.invoice_line_ids._prepare_einvoice_lines_data()
        self.assertEqual(result, [
            {'lineNumber': 1, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'unitName': 'Đơn vị\n(Units)', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0, 'quantity': 1.0,
             'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': 10.0, 'taxAmount': 100.0, 'discount': 0,
             'itemDiscount': 0, 'itemTotalAmountWithTax': 1100.0},
            {'lineNumber': 2, 'itemName': '[default_code_product_b] product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
             'itemCode': 'default_code_product_b', 'unitPrice': 200.0, 'quantity': 1.0,
             'itemTotalAmountWithoutTax': 200.0, 'taxPercentage': 10.0, 'taxAmount': 20.0, 'discount': 0,
             'itemDiscount': 0, 'itemTotalAmountWithTax': 220.0},
            {'lineNumber': 3, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'unitName': 'Đơn vị\n(Units)', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0, 'quantity': 1.0,
             'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': -2, 'taxAmount': 0.0, 'discount': 0,
             'itemDiscount': 0, 'itemTotalAmountWithTax': 1000.0},
            {'lineNumber': 4, 'selection': 2, 'itemName': 'line note'},
        ])
        # change sequence
        self.invoice.invoice_line_ids[0].write({'sequence': 999})
        result = self.invoice.invoice_line_ids._prepare_einvoice_lines_data()
        self.assertEqual(result, [
            {'lineNumber': 1, 'itemName': '[default_code_product_b] product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
             'itemCode': 'default_code_product_b', 'unitPrice': 200.0, 'quantity': 1.0,
             'itemTotalAmountWithoutTax': 200.0, 'taxPercentage': 10.0, 'taxAmount': 20.0, 'discount': 0,
             'itemDiscount': 0, 'itemTotalAmountWithTax': 220.0},
            {'lineNumber': 2, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'unitName': 'Đơn vị\n(Units)', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0, 'quantity': 1.0,
             'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': -2, 'taxAmount': 0.0, 'discount': 0,
             'itemDiscount': 0, 'itemTotalAmountWithTax': 1000.0},
            {'lineNumber': 3, 'selection': 2, 'itemName': 'line note'},
            {'lineNumber': 4, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'unitName': 'Đơn vị\n(Units)', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0, 'quantity': 1.0,
             'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': 10.0, 'taxAmount': 100.0, 'discount': 0,
             'itemDiscount': 0, 'itemTotalAmountWithTax': 1100.0},
        ])
    
    def test_16_prepare_einvoice_lines_data_2(self):
        # test with included price tax
        self.tax_sale_b.write({'price_include': True})
        invoice = self.create_invoice()
        result = invoice.invoice_line_ids._prepare_einvoice_lines_data()
        self.assertEqual(result, [
            {'lineNumber': 1, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'unitName': 'Đơn vị\n(Units)', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0, 'quantity': 1.0,
             'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': 10.0, 'taxAmount': 100.0, 'discount': 0,
             'itemDiscount': 0, 'itemTotalAmountWithTax': 1100.0},
            {'lineNumber': 2, 'itemName': '[default_code_product_b] product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
             'itemCode': 'default_code_product_b', 'unitPrice': 181.82, 'quantity': 1.0,
             'itemTotalAmountWithoutTax': 182.0, 'taxPercentage': 10.0, 'taxAmount': 18.0, 'discount': 0,
             'itemDiscount': 0, 'itemTotalAmountWithTax': 200.0},
        ])
        
    def test_16_onchange_label_on_invoice_lines(self):
        self.assertEqual(self.invoice.invoice_line_ids[0]._prepare_einvoice_line_name('invoice_line_name'),
                         '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)')
        self.assertEqual(self.invoice.invoice_line_ids[0]._prepare_einvoice_line_name('invoice_line_product'),
                         'product_a_vi_VN (product_a)')
        self.invoice.button_draft()
        self.invoice.invoice_line_ids[0].write({'product_id': False})
        self.assertEqual(self.invoice.invoice_line_ids[0]._prepare_einvoice_line_name('invoice_line_product'),
                         '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)')

    def test_17_prepare_sinvoice_data_foreign_partner(self):
        result = self.invoice._prepare_sinvoice_data()
        self.assertEqual(result, {
            'generalInvoiceInfo':
                {
                    'transactionUuid': 'access_token',
                    'userName': 'Because I am accountman!',
                    'currencyCode': 'VND',
                    'exchangeRate': 1.0,
                    'invoiceSeries': 'AA/20E',
                    'templateCode': '01GTKT0/001',
                    'invoiceType': '01GTKT',
                    'adjustmentType': '1',
                    'paymentStatus': False,
                    'paymentType': 'TM/CK',
                    'paymentTypeName': 'TM/CK',
                    'cusGetInvoiceRight': True,
                },
            'payments': [{'paymentMethodName': 'TM/CK'}],
            'buyerInfo':
                {
                    'buyerName': '',
                    'buyerLegalName': 'partner_a',
                    'buyerTaxCode': '',
                    'buyerAddressLine': '31 Bạch Đằng, Hải Phòng, United States, Bạch Đằng, 31',
                    'buyerCityName': 'Hải Phòng',
                    'buyerCountryCode': 'US',
                    'buyerPhoneNumber': '0978654321',
                    'buyerEmail': 'khaihoan@example.viindoo.com'
                },
            'sellerInfo':
                {
                    'sellerLegalName': 'company_1_data',
                    'sellerTaxCode': '0201994665',
                    'sellerAddressLine': 'Kỳ Sơn',
                    'sellerPhoneNumber': '0918777888',
                    'sellerEmail': 'khaihoan@example.viindoo.com',
                    'sellerBankName': 'Ngân hàng ACB, Swift/bic: khaihoan',
                    'sellerBankAccount': 'zuiqua',
                    'sellerWebsite': 'http://viindoo.com'
                },
            'itemInfo': [
                {'lineNumber': 1, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'unitName': 'Đơn vị\n(Units)', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0,
                 'quantity': 1.0, 'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': 10.0, 'taxAmount': 100.0,
                 'discount': 0, 'itemDiscount': 0, 'itemTotalAmountWithTax': 1100.0},
                {'lineNumber': 2, 'itemName': '[default_code_product_b] product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
                 'itemCode': 'default_code_product_b', 'unitPrice': 200.0, 'quantity': 1.0,
                 'itemTotalAmountWithoutTax': 200.0, 'taxPercentage': 10.0, 'taxAmount': 20.0, 'discount': 0,
                 'itemDiscount': 0, 'itemTotalAmountWithTax': 220.0},
                {'lineNumber': 3, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'unitName': 'Đơn vị\n(Units)', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0,
                 'quantity': 1.0, 'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': -2, 'taxAmount': 0.0,
                 'discount': 0, 'itemDiscount': 0, 'itemTotalAmountWithTax': 1000.0},
                {'lineNumber': 4, 'selection': 2, 'itemName': 'line note'},],
            'summarizeInfo': {
                'sumOfTotalLineAmountWithoutTax': 2200.0,
                'totalAmountWithoutTax': 2200.0,
                'totalTaxAmount': 120.0,
                'totalAmountWithTax': 2320.0,
                'totalAmountWithTaxInWords': 'Hai nghìn ba trăm hai mươi (Two Thousand, Three Hundred And Twenty Dong)',
                'discountAmount': 0,
                'taxPercentage': 5.454545454545454
            },
            'taxBreakdowns': [
                {'taxPercentage': 10.0, 'taxableAmount': 1200.0, 'taxAmount': 120.0},
                {'taxPercentage': -2, 'taxableAmount': 1000.0, 'taxAmount': 0}]
        })

    def test_17_prepare_sinvoice_data_vn_partner(self):
        self.partner_a.write({
            'street': '31 Bạch Đằng',
            'country_id': self.env.ref('base.vn'),
            'city': 'Hải Phòng',
        })
        result = self.invoice._prepare_sinvoice_data()
        self.assertEqual(result, {
            'generalInvoiceInfo':
                {
                    'transactionUuid': 'access_token',
                    'userName': 'Because I am accountman!',
                    'currencyCode': 'VND',
                    'exchangeRate': 1.0,
                    'invoiceSeries': 'AA/20E',
                    'templateCode': '01GTKT0/001',
                    'invoiceType': '01GTKT',
                    'adjustmentType': '1',
                    'paymentStatus': False,
                    'paymentType': 'TM/CK',
                    'paymentTypeName': 'TM/CK',
                    'cusGetInvoiceRight': True,
                },
            'payments': [{'paymentMethodName': 'TM/CK'}],
            'buyerInfo':
                {
                    'buyerName': '',
                    'buyerLegalName': 'partner_a',
                    'buyerTaxCode': '123456789',
                    'buyerAddressLine': '31 Bạch Đằng, Hải Phòng, Vietnam, Bạch Đằng, 31',
                    'buyerCityName': 'Hải Phòng',
                    'buyerCountryCode': 'VN',
                    'buyerPhoneNumber': '0978654321',
                    'buyerEmail': 'khaihoan@example.viindoo.com'
                },
            'sellerInfo':
                {
                    'sellerLegalName': 'company_1_data',
                    'sellerTaxCode': '0201994665',
                    'sellerAddressLine': 'Kỳ Sơn',
                    'sellerPhoneNumber': '0918777888',
                    'sellerEmail': 'khaihoan@example.viindoo.com',
                    'sellerBankName': 'Ngân hàng ACB, Swift/bic: khaihoan',
                    'sellerBankAccount': 'zuiqua',
                    'sellerWebsite': 'http://viindoo.com'
                },
            'itemInfo': [
                {'lineNumber': 1, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'unitName': 'Đơn vị', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0,
                 'quantity': 1.0, 'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': 10.0, 'taxAmount': 100.0,
                 'discount': 0, 'itemDiscount': 0, 'itemTotalAmountWithTax': 1100.0},
                {'lineNumber': 2, 'itemName': '[default_code_product_b] product_b (product_b)', 'unitName': 'Tá',
                 'itemCode': 'default_code_product_b', 'unitPrice': 200.0, 'quantity': 1.0,
                 'itemTotalAmountWithoutTax': 200.0, 'taxPercentage': 10.0, 'taxAmount': 20.0, 'discount': 0,
                 'itemDiscount': 0, 'itemTotalAmountWithTax': 220.0},
                {'lineNumber': 3, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'unitName': 'Đơn vị', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0,
                 'quantity': 1.0, 'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': -2, 'taxAmount': 0.0,
                 'discount': 0, 'itemDiscount': 0, 'itemTotalAmountWithTax': 1000.0},
                {'lineNumber': 4, 'selection': 2, 'itemName': 'line note'},],
            'summarizeInfo': {
                'sumOfTotalLineAmountWithoutTax': 2200.0,
                'totalAmountWithoutTax': 2200.0,
                'totalTaxAmount': 120.0,
                'totalAmountWithTax': 2320.0,
                'totalAmountWithTaxInWords': 'Hai nghìn ba trăm hai mươi',
                'discountAmount': 0,
                'taxPercentage': 5.454545454545454
            },
            'taxBreakdowns': [
                {'taxPercentage': 10.0, 'taxableAmount': 1200.0, 'taxAmount': 120.0},
                {'taxPercentage': -2, 'taxableAmount': 1000.0, 'taxAmount': 0}]
        })

    def test_17_prepare_sinvoice_data_reversal_move(self):
        self.env['account.move.reversal'].create([{
            'move_id': self.invoice.id,
            'refund_method': 'cancel',
            'date': self.invoice_date
        }]).reverse_moves()
        refund = self.env['account.move'].search([('reversed_entry_id', '=', self.invoice.id)])
        refund.write({'access_token': 'access_token_2'})
        result = refund.with_context(
            additionalReferenceDesc='abc',
            additionalReferenceDate=fields.Datetime.to_datetime('2021-09-01')
        )._prepare_sinvoice_data()
        self.assertDictEqual(result, {
            'generalInvoiceInfo': {
                'transactionUuid': 'access_token_2',
                'userName': 'Because I am accountman!',
                'currencyCode': 'VND',
                'exchangeRate': 1.0,
                'invoiceSeries': 'AA/20E',
                'templateCode': '01GTKT0/001',
                'invoiceType': '01GTKT',
                'adjustmentType': '5',
                'paymentStatus': True,
                'paymentType': 'TM/CK',
                'paymentTypeName': 'TM/CK',
                'cusGetInvoiceRight': True,
                'adjustmentInvoiceType': 1,
                'originalInvoiceId': False,
                'originalInvoiceIssueDate': False,
                'additionalReferenceDesc': 'abc',
                'additionalReferenceDate': '2021-09-01',
            },
            'payments': [{'paymentMethodName': 'TM/CK'}],
            'buyerInfo': {
                'buyerName': '',
                'buyerLegalName': 'partner_a',
                'buyerTaxCode': '',
                'buyerAddressLine': '31 Bạch Đằng, Hải Phòng, United States, Bạch Đằng, 31',
                'buyerCityName': 'Hải Phòng',
                'buyerCountryCode': 'US',
                'buyerPhoneNumber': '0978654321',
                'buyerEmail': 'khaihoan@example.viindoo.com'},
            'sellerInfo': {
                'sellerLegalName': 'company_1_data',
                'sellerTaxCode': '0201994665',
                'sellerAddressLine': 'Kỳ Sơn',
                'sellerPhoneNumber': '0918777888',
                'sellerEmail': 'khaihoan@example.viindoo.com',
                'sellerBankName': 'Ngân hàng ACB, Swift/bic: khaihoan',
                'sellerBankAccount': 'zuiqua',
                'sellerWebsite': 'http://viindoo.com'
            },
            'itemInfo': [
                {'lineNumber': 1, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'unitName': 'Đơn vị\n(Units)', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0,
                 'quantity': 1.0, 'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': 10.0, 'taxAmount': 100.0,
                 'discount': 0, 'itemDiscount': 0, 'itemTotalAmountWithTax': 1100.0, 'adjustmentTaxAmount': 100.0,
                 'isIncreaseItem': False, 'itemTotalAmountAfterDiscount': 1100.0},
                {'lineNumber': 2, 'itemName': '[default_code_product_b] product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
                 'itemCode': 'default_code_product_b', 'unitPrice': 200.0, 'quantity': 1.0,
                 'itemTotalAmountWithoutTax': 200.0, 'taxPercentage': 10.0, 'taxAmount': 20.0, 'discount': 0,
                 'itemDiscount': 0, 'itemTotalAmountWithTax': 220.0, 'adjustmentTaxAmount': 20.0,
                 'isIncreaseItem': False, 'itemTotalAmountAfterDiscount': 220.0},
                {'lineNumber': 3, 'itemName': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'unitName': 'Đơn vị\n(Units)', 'itemCode': 'default_code_product_a', 'unitPrice': 1000.0,
                 'quantity': 1.0, 'itemTotalAmountWithoutTax': 1000.0, 'taxPercentage': -2, 'taxAmount': 0.0,
                 'discount': 0, 'itemDiscount': 0, 'itemTotalAmountWithTax': 1000.0, 'adjustmentTaxAmount': 0.0,
                 'isIncreaseItem': False, 'itemTotalAmountAfterDiscount': 1000.0},
                {'lineNumber': 4, 'selection': 2, 'itemName': 'line note'}
            ],
            'summarizeInfo': {
                'sumOfTotalLineAmountWithoutTax': 2200.0,
                'totalAmountWithoutTax': 2200.0,
                'totalTaxAmount': 120.0,
                'totalAmountWithTax': 2320.0,
                'totalAmountWithTaxInWords': 'Hai nghìn ba trăm hai mươi (Two Thousand, Three Hundred And Twenty Dong)',
                'discountAmount': 0,
                'taxPercentage': 5.454545454545454,
                'isTotalAmountPos': False,
                'isTotalTaxAmountPos': False,
                'isTotalAmtWithoutTaxPos': False,
                'isDiscountAmtPos': False
            },
            'taxBreakdowns': [
                {'taxPercentage': 10.0, 'taxableAmount': 1200.0, 'taxAmount': 120.0},
                {'taxPercentage': -2, 'taxableAmount': 1000.0, 'taxAmount': 0}
            ]
        })

    def test_cannot_issue_refund_if_invoice_not_issued(self):
        wizard = self.env['account.move.reversal'].create([{
            'move_id': self.invoice.id,
            'refund_method': 'cancel',
            'date': self.invoice_date
        }])
        refund = self.invoice._reverse_moves([wizard._prepare_default_reversal(self.invoice)], cancel=True)
        refund.write({'access_token': 'access_token_2'})
        with self.assertRaises(UserError):
            self.env['account.invoice.einvoice.adjustment'].create({
                'invoice_id': refund.id,
                'additional_reference_desc': 'abc',
                'adjustment_record': self.converted_file,
            }).action_adjust_einvoice()

    def test_issue_refund(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_sinvoice()
        wizard = self.env['account.move.reversal'].create([{
            'move_id': self.invoice.id,
            'refund_method': 'cancel',
            'date': self.invoice_date
        }])
        refund = self.invoice._reverse_moves([wizard._prepare_default_reversal(self.invoice)], cancel=True)
        refund.write({'access_token': 'access_token_2'})
        with self.patch_date_today(date(2021, 9, 1)):
            self.env['account.invoice.einvoice.adjustment'].create({
                'invoice_id': refund.id,
                'additional_reference_desc': 'abc',
                'adjustment_record': self.converted_file,
                'adjustment_record_name': 'adjustment_record_name.pdf'
            }).action_adjust_einvoice()
        self.assertEqual(refund.einvoice_state, 'paid')
        self.assertEqual(self.invoice.einvoice_state, 'adjusted')
