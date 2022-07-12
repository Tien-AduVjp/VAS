from unittest.mock import patch
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import fields
from .test_base import TestVNinvoiceBaseCommon


from odoo.tests import tagged, Form
from odoo.exceptions import UserError, ValidationError


@tagged('post_install', '-at_install')
class TestVNinvoice(TestVNinvoiceBaseCommon):

    def test_01_check_data_after_setup_vninvoice(self):
        self.assertRecordValues(self.company, [
            {'account_vninvoice_template_id': self.template.id, 'account_vninvoice_type_id': self.template.type_id.id}])
        self.assertTrue(self.company_data['default_journal_sale'].einvoice_enabled)

    def test_02_vninvoice_api_url(self):
        self.company._generate_vninvoice_config_params()
        self.assertEqual(self.company._get_vninvoice_api_url(), 'https://demo.vninvoice.vn')
        self.company.write({'vninvoice_mode': 'production'})
        self.assertEqual(self.company._get_vninvoice_api_url(), 'https://domain-khachhang.vn')
        self.company.write({'vninvoice_api_url': 'https://domain-khachhang.vn//'})
        self.assertEqual(self.company.get_vninvoice_create_batch_url(),
                         'https://domain-khachhang.vn/api/01gtkt/create-batch')

    def test_03_cannot_issue_invoice(self):
        self.check_issue_einvoice_raise_excep()
        with self.assertRaises(UserError, msg="Line with no uom"):
            with self.env.cr.savepoint():
                self.invoice.invoice_line_ids[0].product_uom_id = False
                with self.patch_date_today(date(2021, 9, 1)):
                    self.invoice.issue_einvoices()
        with self.assertRaises(UserError, msg="Later e-invoice existing"):
            with self.patch_date_today(date(2021, 9, 1)):
                self.issue_vninvoice()
            self.create_invoice(invoice_date=self.invoice_date - relativedelta(days=1)).issue_einvoices()

    def test_04_issue_invoice(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
        self.assertRecordValues(self.invoice, [{
            'legal_number': '00001',
            'einvoice_state': 'issued',
            'vninvoice_transactionid': 'access_token',
            'vninvoice_recordid': 'vninvoiceID',
        }])
        self.create_payment(amount=self.invoice.amount_total, invoice_ids=[(6, 0, self.invoice.ids)])
        self.assertEqual(self.invoice.einvoice_state, 'paid')

    def test_05_issue_paid_invoice(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice(paid=True)
        self.assertRecordValues(self.invoice, [{
            'legal_number': '00001',
            'einvoice_state': 'paid',
            'vninvoice_transactionid': 'access_token',
            'vninvoice_recordid': 'vninvoiceID',
        }])

    @patch('odoo.addons.to_accounting_vninvoice.models.account_move.requests.get')
    @patch('odoo.addons.to_accounting_vninvoice.models.account_move.requests.post')
    def test_06_download_files_not_signed(self, mock_post, mock_get):
        mock_post.side_effect = self.mock_request_response
        mock_get.side_effect = self.mock_request_response
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
        self.assertRecordValues(self.invoice, [{
            'legal_number': '00001',
            'einvoice_state': 'issued',
            'vninvoice_transactionid': 'access_token',
            'vninvoice_recordid': 'vninvoiceID',
        }])
        self.invoice.get_einvoice_representation_files()
        self.assertRecordValues(self.invoice, [{
            'vninvoice_representation_pdf': self.VNinvoice_representation_no_signed_pdf.encode(),
            'vninvoice_representation_filename_pdf': 'VNinvoice-00001.pdf',
            'vninvoice_representation_xml': False,
            'vninvoice_representation_filename_xml': False,
        }])
        with self.assertRaises(UserError):
            self.invoice.get_einvoice_converted_files()

    def test_07_check_invoice_signed(self):
        self.check_invoice_signed()
        self.assertEqual(self.invoice.check_vninvoice_approved_and_signed, False)
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
        self.assertEqual(self.invoice.check_vninvoice_approved_and_signed, False)
        self.sign_status = True
        self.check_invoice_signed()
        self.assertEqual(self.invoice.check_vninvoice_approved_and_signed, True)

    def test_08_sign_invoice(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
        self.assertEqual(self.invoice.check_vninvoice_approved_and_signed, False)
        self.sign_invoice()
        self.assertEqual(self.invoice.check_vninvoice_approved_and_signed, True)
        self.check_invoice_signed()
        self.assertEqual(self.invoice.check_vninvoice_approved_and_signed, True)

    def test_09_download_invoice_signed(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
        self.sign_invoice()
        self.download_vninvoice()
        self.assertRecordValues(self.invoice, [{
            'vninvoice_representation_pdf': self.VNinvoice_representation_signed_pdf.encode(),
            'vninvoice_representation_filename_pdf': 'VNinvoice-00001.pdf',
            'vninvoice_representation_xml': self.VNinvoice_representation_signed_xml.encode(),
            'vninvoice_representation_filename_xml': 'VNinvoice-00001.xml',
            'vninvoice_converted_file': self.VNinvoice_converted.encode(),
            'vninvoice_converted_filename': 'VNinvoice-00001-converted.pdf',
        }])

    @patch('odoo.addons.to_accounting_vninvoice.models.res_company.requests.post')
    @patch('odoo.addons.to_accounting_vninvoice.models.account_move.requests.get')
    @patch('odoo.addons.to_accounting_vninvoice.models.account_move.requests.post')
    def test_10_download_invoice_with_cron(self, mock_post, mock_get, mock_post_token):
        mock_post.side_effect = self.mock_request_response
        mock_get.side_effect = self.mock_request_response
        mock_post_token.side_effect = self.mock_request_response
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
        self.invoice._cron_ensure_einvoice_download_file()
        self.assertRecordValues(self.invoice, [{
            'vninvoice_representation_pdf': self.VNinvoice_representation_no_signed_pdf.encode(),
            'vninvoice_representation_filename_pdf': 'VNinvoice-00001.pdf',
            'vninvoice_representation_xml': False,
            'vninvoice_representation_filename_xml': False,
            'vninvoice_converted_file': False,
            'vninvoice_converted_filename': False,
        }])
        self.sign_invoice()
        self.invoice._cron_ensure_einvoice_download_file()
        self.assertRecordValues(self.invoice, [{
            'vninvoice_representation_pdf': self.VNinvoice_representation_signed_pdf.encode(),
            'vninvoice_representation_filename_pdf': 'VNinvoice-00001.pdf',
            'vninvoice_representation_xml': self.VNinvoice_representation_signed_xml.encode(),
            'vninvoice_representation_filename_xml': 'VNinvoice-00001.xml',
            'vninvoice_converted_file': self.VNinvoice_converted.encode(),
            'vninvoice_converted_filename': 'VNinvoice-00001-converted.pdf',
        }])

    @patch('odoo.addons.to_accounting_vninvoice.models.res_company.requests.post')
    @patch('odoo.addons.to_accounting_vninvoice.models.account_move.requests.get')
    @patch('odoo.addons.to_accounting_vninvoice.models.account_move.requests.post')
    def test_11_cancel_vninvoice(self, mock_post, mock_get, mock_post_token):
        mock_post.side_effect = self.mock_request_response
        mock_get.side_effect = self.mock_request_response
        mock_post_token.side_effect = self.mock_request_response
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice(paid=True)
        self.sign_invoice()
        # self.invoice.button_draft()
        # self.invoice.button_cancel()
        wizard_form = Form(self.env['account.invoice.einvoice.cancel'].with_context(default_invoice_id=self.invoice.id))
        with self.assertRaises(AssertionError, msg="required cancellation_record"):
            wizard_form.additional_reference_desc = 'khaihoan_cancel'
            wizard_form.additional_reference_date = fields.Datetime.now()
            wizard_form.save()
        with self.assertRaises(AssertionError, msg="required reason"):
            wizard_form.additional_reference_desc = 'khaihoan_cancel'
            wizard_form.additional_reference_date = fields.Datetime.now()
            wizard_form.cancellation_record = self.VNinvoice_representation_signed_pdf
            wizard_form.save()
        with self.assertRaises(ValidationError, msg="Cancelling date in the future"):
            wizard_form.additional_reference_desc = 'khaihoan_cancel'
            wizard_form.additional_reference_date = fields.Datetime.now() + relativedelta(
                months=1)
            wizard_form.cancellation_record = self.VNinvoice_representation_signed_pdf
            wizard_form.reason = 'zuiqua'
            wizard_form.save()
        with self.assertRaises(ValidationError, msg="Cancelling date in the pass"):
            wizard_form.additional_reference_desc = 'khaihoan_cancel'
            wizard_form.additional_reference_date = fields.Datetime.now() - relativedelta(
                months=1)
            wizard_form.cancellation_record = self.VNinvoice_representation_signed_pdf
            wizard_form.cancellation_record_name = 'VNinvoice_representation_signed.pdf'
            wizard_form.reason = 'zuiqua'
            wizard_form.save()
        with self.assertRaises(ValidationError, msg="cancel with cancellation_record be not pdf file"):
            wizard_form.additional_reference_desc = 'khaihoan_cancel'
            wizard_form.additional_reference_date = fields.Datetime.now()
            wizard_form.cancellation_record = self.VNinvoice_representation_signed_xml
            wizard_form.cancellation_record_name = 'VNinvoice_representation_signed.xml'
            wizard_form.reason = 'zuiqua'
            wizard_form.save().action_cancel_einvoice()
        wizard_form.additional_reference_desc = 'khaihoan_cancel'
        wizard_form.additional_reference_date = fields.Datetime.now()
        wizard_form.cancellation_record = self.VNinvoice_representation_signed_pdf
        wizard_form.cancellation_record_name = 'VNinvoice_representation_signed.pdf'
        wizard_form.reason = 'zuiqua'
        wizard = wizard_form.save()
        wizard.action_cancel_einvoice()
        self.assertRecordValues(self.invoice, [{
            'einvoice_state': 'cancelled',
            'cancellation_record': self.VNinvoice_representation_signed_pdf.encode(),
            'cancellation_record_name': 'VNinvoice_representation_signed.pdf',
            'vninvoice_representation_pdf': self.VNinvoice_representation_cancelled_pdf.encode(),
            'vninvoice_representation_filename_pdf': 'VNinvoice-00001.pdf',
            'vninvoice_representation_xml': self.VNinvoice_representation_cancelled_xml.encode(),
            'vninvoice_representation_filename_xml': 'VNinvoice-00001.xml',
            'vninvoice_converted_file': self.VNinvoice_converted_cancelled.encode(),
            'vninvoice_converted_filename': 'VNinvoice-00001-converted.pdf',
        }])

    def test_12_edit_template_type_serial_linked_to_invoices(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
        with self.assertRaises(UserError):
            self.serial.write({'name': 'khaihoan'})
        with self.assertRaises(UserError):
            self.template.write({'name': 'khaihoan'})
        with self.assertRaises(UserError):
            self.template.type_id.write({'name': 'khaihoan'})

    def test_14_cannnot_edit_legal_number(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
        invoice_form = Form(self.invoice)
        with self.assertRaises(AssertionError):
            invoice_form.legal_number = '00001'

    # --------------------------------------------------
    # TEST METHODS
    # --------------------------------------------------

    def test_15_prepare_vninvoice_tax_breakdowns(self):
        result = self.invoice._prepare_vninvoice_tax_breakdowns()
        self.assertEqual(result, [
            {'name': 'Thuế GTGT 10%', 'vatAmount': 120.0, 'vatPercent': 10},
            {'name': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0, 'vatPercent': -1}
        ])

    def test_16_prepare_einvoice_lines_data(self):
        result = self.invoice.invoice_line_ids._prepare_einvoice_lines_data()
        self.assertEqual(result, [
            {'index': 1, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
             'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0,
             'vatPercent': 10, 'vatPercentDisplay': 'Thuế GTGT phải nộp 10%', 'vatAmount': 100.0,
             'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 1100.0,
             'productId': 'default_code_product_a'},
            {'index': 2, 'productName': 'product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
             'unitPrice': 200.0, 'quantity': 1.0, 'amount': 200.0, 'vatPercent': 10,
             'vatPercentDisplay': 'Thuế GTGT phải nộp 10% (Copy)', 'vatAmount': 20.0,
             'note': '[default_code_product_b] product_b (product_b)', 'discountAmountBeforeTax': 0.0,
             'discountPercentBeforeTax': 0, 'paymentAmount': 220.0, 'productId': 'default_code_product_b',},
            {'index': 3, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
             'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0, 'vatPercent': -1,
             'vatPercentDisplay': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0.0,
             'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'discountAmountBeforeTax': 0.0,
             'discountPercentBeforeTax': 0, 'paymentAmount': 1000.0, 'productId': 'default_code_product_a',}
        ])
        # change sequence
        self.invoice.invoice_line_ids[0].write({'sequence': 999})
        result = self.invoice.invoice_line_ids._prepare_einvoice_lines_data()
        self.assertEqual(result, [
            {'index': 1, 'productName': 'product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
             'productId': 'default_code_product_b',
             'unitPrice': 200.0, 'quantity': 1.0, 'amount': 200.0, 'vatPercent': 10,
             'vatPercentDisplay': 'Thuế GTGT phải nộp 10% (Copy)', 'vatAmount': 20.0,
             'note': '[default_code_product_b] product_b (product_b)', 'discountAmountBeforeTax': 0.0,
             'discountPercentBeforeTax': 0, 'paymentAmount': 220.0},
            {'index': 2, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
             'productId': 'default_code_product_a',
             'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0, 'vatPercent': -1,
             'vatPercentDisplay': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0.0,
             'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'discountAmountBeforeTax': 0.0,
             'discountPercentBeforeTax': 0, 'paymentAmount': 1000.0},
            {'index': 3, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
             'productId': 'default_code_product_a',
             'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0, 'vatPercent': 10,
             'vatPercentDisplay': 'Thuế GTGT phải nộp 10%', 'vatAmount': 100.0,
             'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'discountAmountBeforeTax': 0.0,
             'discountPercentBeforeTax': 0, 'paymentAmount': 1100.0},
        ])
    
    def test_16_prepare_einvoice_lines_data_2(self):
        # test with included price tax
        self.tax_sale_b.write({'price_include': True})
        invoice = self.create_invoice()
        result = invoice.invoice_line_ids._prepare_einvoice_lines_data()
        self.assertEqual(result, [
            {'index': 1, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
             'productId': 'default_code_product_a', 'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0,
             'vatPercent': 10, 'vatPercentDisplay': 'Thuế GTGT phải nộp 10%', 'vatAmount': 100.0,
             'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 1100.0},
            {'index': 2, 'productName': 'product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
             'unitPrice': 181.82, 'quantity': 1.0, 'amount': 182.0, 'vatPercent': 10,
             'vatPercentDisplay': 'Thuế GTGT phải nộp 10% (Copy)', 'vatAmount': 18.0,
             'note': '[default_code_product_b] product_b (product_b)', 'discountAmountBeforeTax': 0.0,
             'discountPercentBeforeTax': 0, 'paymentAmount': 200.0, 'productId': 'default_code_product_b'},
        ])
        
    def test_17_onchange_label_on_invoice_lines(self):
        self.assertEqual(self.invoice.invoice_line_ids[0]._prepare_einvoice_line_name('invoice_line_name'),
                         'product_a_vi_VN (product_a)')
        self.assertEqual(self.invoice.invoice_line_ids[0]._prepare_einvoice_line_name('invoice_line_product'),
                         'product_a_vi_VN (product_a)')
        self.invoice.button_draft()
        self.invoice.invoice_line_ids[0].write({'product_id': False})
        self.assertEqual(self.invoice.invoice_line_ids[0]._prepare_einvoice_line_name('invoice_line_product'),
                         '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)')

    def test_18_prepare_vninvoice_data_foreign_partner(self):
        result = self.invoice._prepare_vninvoice_data()
        self.assertDictEqual(result[0], {
            'invoiceDate': '2021-09-01',
            'userNameCreator': 'Because I am accountman!',
            'invoiceDetails': [
                {'index': 1, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
                 'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0, 'vatPercent': 10,
                 'vatPercentDisplay': 'Thuế GTGT phải nộp 10%', 'vatAmount': 100.0,
                 'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 1100.0,
                 'productId': 'default_code_product_a'},
                {'index': 2, 'productName': 'product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
                 'unitPrice': 200.0, 'quantity': 1.0, 'amount': 200.0, 'vatPercent': 10,
                 'vatPercentDisplay': 'Thuế GTGT phải nộp 10% (Copy)', 'vatAmount': 20.0,
                 'note': '[default_code_product_b] product_b (product_b)', 'discountAmountBeforeTax': 0.0,
                 'discountPercentBeforeTax': 0, 'paymentAmount': 220.0,
                 'productId': 'default_code_product_b'},
                {'index': 3, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
                 'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0, 'vatPercent': -1,
                 'vatPercentDisplay': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0.0,
                 'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 1000.0,
                 'productId': 'default_code_product_a'}],
            'invoiceTaxBreakdowns': [
                {'vatPercent': 10, 'name': 'Thuế GTGT 10%', 'vatAmount': 120.0},
                {'vatPercent': -1, 'name': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0}
            ],
            'Note': '',
            'paymentMethod': 'Tiền mặt hoặc chuyển khoản',
            'totalAmount': 2200.0,
            'totalVatAmount': 120.0,
            'totalPaymentAmount': 2320.0,
            'exchangeRate': 1.0,
            'paymentDate': '2021-09-01T00:00:00.000000',
            'buyerEmail': 'khaihoan@example.viindoo.com',
            'buyerFullName': 'partner_a',
            'buyerLegalName': '',
            'buyerTaxCode': '',
            'buyerAddressLine': '31 Bạch Đằng, Hải Phòng, United States, Bạch Đằng, 31',
            'buyerDistrictName': '',
            'buyerCityName': 'Hải Phòng',
            'buyerCountryCode': 'US',
            'buyerPhoneNumber': '0978654321',
            'buyerFaxNumber': '',
            'buyerBankName': '',
            'buyerBankAccount': '',
            'idBuyer': str(self.partner_a.id),
            'buyerGroupCode': '',
            'buyerCode': str(self.partner_a.id),
            'idBuyerGroup': '',
            'buyerGroupName': '',
            'currency': 'VND',
            'templateNo': '01GTKT0/001',
            'serialNo': 'AA/20E',
            'id': 'access_token',
            'idTransaction': 'access_token',
        })

    def test_18_prepare_vninvoice_data_vn_partner(self):
        self.partner_a.write({
            'street': '31 Bạch Đằng',
            'country_id': self.env.ref('base.vn'),
            'city': 'Hải Phòng',
        })
        result = self.invoice._prepare_vninvoice_data()
        self.assertDictEqual(result[0], {
            'invoiceDate': '2021-09-01',
            'userNameCreator': 'Because I am accountman!',
            'invoiceDetails': [
                {'index': 1, 'productName': 'product_a_vi_VN', 'unitName': 'Đơn vị',
                 'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0, 'vatPercent': 10,
                 'vatPercentDisplay': 'Thuế GTGT phải nộp 10%', 'vatAmount': 100.0,
                 'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 1100.0,
                 'productId': 'default_code_product_a'},
                {'index': 2, 'productName': 'product_b', 'unitName': 'Tá',
                 'unitPrice': 200.0, 'quantity': 1.0, 'amount': 200.0, 'vatPercent': 10,
                 'vatPercentDisplay': 'Thuế GTGT phải nộp 10% (Copy)', 'vatAmount': 20.0,
                 'note': '[default_code_product_b] product_b (product_b)', 'discountAmountBeforeTax': 0.0,
                 'discountPercentBeforeTax': 0, 'paymentAmount': 220.0,
                 'productId': 'default_code_product_b'},
                {'index': 3, 'productName': 'product_a_vi_VN', 'unitName': 'Đơn vị',
                 'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0, 'vatPercent': -1,
                 'vatPercentDisplay': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0.0,
                 'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 1000.0,
                 'productId': 'default_code_product_a'}],
            'invoiceTaxBreakdowns': [
                {'vatPercent': 10, 'name': 'Thuế GTGT 10%', 'vatAmount': 120.0},
                {'vatPercent': -1, 'name': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0}
            ],
            'Note': '',
            'paymentMethod': 'Tiền mặt hoặc chuyển khoản',
            'totalAmount': 2200.0,
            'totalVatAmount': 120.0,
            'totalPaymentAmount': 2320.0,
            'exchangeRate': 1.0,
            'paymentDate': '2021-09-01T00:00:00.000000',
            'buyerEmail': 'khaihoan@example.viindoo.com',
            'buyerFullName': 'partner_a',
            'buyerLegalName': '',
            'buyerTaxCode': '123456789',
            'buyerAddressLine': '31 Bạch Đằng, Hải Phòng, Vietnam, Bạch Đằng, 31',
            'buyerDistrictName': '',
            'buyerCityName': 'Hải Phòng',
            'buyerCountryCode': 'VN',
            'buyerPhoneNumber': '0978654321',
            'buyerFaxNumber': '',
            'buyerBankName': '',
            'buyerBankAccount': '',
            'idBuyer': str(self.partner_a.id),
            'buyerGroupCode': '',
            'buyerCode': str(self.partner_a.id),
            'idBuyerGroup': '',
            'buyerGroupName': '',
            'currency': 'VND',
            'templateNo': '01GTKT0/001',
            'serialNo': 'AA/20E',
            'id': 'access_token',
            'idTransaction': 'access_token',
        })

    def test_18_prepare_vninvoice_data_reversal_move(self):
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
        )._prepare_vninvoice_data()
        self.assertDictEqual(result, {
            'invoiceDate': '2021-09-01', 'userNameCreator': 'Because I am accountman!',
            'invoiceDetails': [
                {'index': 1, 'productName': '[Điều chỉnh giảm] product_a_vi_VN [Deduction Adjustment] (product_a)',
                 'unitName': 'Đơn vị\n(Units)', 'unitPrice': 0.0,
                 'quantity': 0.0, 'amount': 0.0, 'vatPercent': 10,
                 'vatPercentDisplay': 'Thuế GTGT phải nộp 10%',
                 'vatAmount': 0.0,
                 'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0,
                 'paymentAmount': 0.0, 'productId': 'default_code_product_a'},
                {'index': 2, 'productName': '[Điều chỉnh giảm] product_b [Deduction Adjustment] (product_b)',
                 'unitName': 'Tá\n(Dozens)', 'unitPrice': 0.0, 'quantity': 0.0,
                 'amount': 0.0, 'vatPercent': 10,
                 'vatPercentDisplay': 'Thuế GTGT phải nộp 10% (Copy)',
                 'vatAmount': 0.0,
                 'note': '[default_code_product_b] product_b (product_b)',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0,
                 'paymentAmount': 0.0, 'productId': 'default_code_product_b'},
                {'index': 3, 'productName': '[Điều chỉnh giảm] product_a_vi_VN [Deduction Adjustment] (product_a)',
                 'unitName': 'Đơn vị\n(Units)', 'unitPrice': 0.0,
                 'quantity': 0.0, 'amount': 0.0, 'vatPercent': -1,
                 'vatPercentDisplay': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0.0,
                 'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0,
                 'paymentAmount': 0.0, 'productId': 'default_code_product_a'}],
            'invoiceTaxBreakdowns': [
                {'vatPercent': 10, 'name': 'Thuế GTGT 10%', 'vatAmount': 0.0},
                {'vatPercent': -1, 'name': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0},
                {'vatPercent': -1, 'name': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0}],
            'Note': '',
            'paymentMethod': 'Tiền mặt hoặc chuyển khoản',
            'totalAmount': 0.0,
            'totalVatAmount': 0.0,
            'totalPaymentAmount': 0.0,
            'exchangeRate': 1.0,
            'paymentDate': '2021-09-01T00:00:00.000000',
            'buyerEmail': 'khaihoan@example.viindoo.com',
            'buyerFullName': 'partner_a',
            'buyerLegalName': '',
            'buyerTaxCode': '',
            'buyerAddressLine': '31 Bạch Đằng, Hải Phòng, United States, Bạch Đằng, 31',
            'buyerDistrictName': '',
            'buyerCityName': 'Hải Phòng',
            'buyerCountryCode': 'US',
            'buyerPhoneNumber': '0978654321',
            'buyerFaxNumber': '',
            'buyerBankName': '',
            'buyerBankAccount': '',
            'idBuyer': str(self.partner_a.id),
            'buyerGroupCode': '',
            'buyerCode': str(self.partner_a.id),
            'idBuyerGroup': '',
            'buyerGroupName': '',
            'currency': 'VND',
            'templateNo': '01GTKT0/001',
            'serialNo': 'AA/20E',
            'id': 'access_token_2',
            'idTransaction': 'access_token_2',
            'idReference': False,
            'recordNo': 'abc',
            'recordDate': '2021-09-01',
            'fileOfRecord': '',
            'fileNameOfRecord': '',
            'reason': 'Reversal of: INV/2021/0001'})

    def test_cannot_issue_refund_if_invoice_not_issued(self):
        wizard =  self.env['account.move.reversal'].create([{
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
                'adjustment_record': self.VNinvoice_representation_no_signed_pdf,
            }).action_adjust_einvoice()

    def test_cannot_issue_refund_if_invoice_not_signed(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
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
                'adjustment_record': self.VNinvoice_representation_no_signed_pdf,
                'adjustment_record_name': 'adjustment_record_name.pdf'
            }).action_adjust_einvoice()

    def test_issue_refund(self):
        with self.patch_date_today(date(2021, 9, 1)):
            self.issue_vninvoice()
        self.sign_invoice()
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
                'adjustment_record': self.VNinvoice_representation_no_signed_pdf,
                'adjustment_record_name': 'adjustment_record_name.pdf'
            }).action_adjust_einvoice()
        self.assertEqual(refund.einvoice_state, 'paid')
        self.assertEqual(self.invoice.einvoice_state, 'adjusted')

    def test_cron_auto_issue(self):
        invoice2 = self.invoice.copy()
        with self.patch_date_context_today(date(2021, 9, 1)):
            invoice2.post()
        with self.patch_date_today(date(2021, 9, 1)):
            self.env['account.move']._cron_issue_einvoices()
        self.assertRecordValues(self.invoice | invoice2, [{
            'einvoice_state': 'not_issued',
        }, {
            'einvoice_state': 'not_issued',
        }])
        self.company_data['default_journal_sale'].write({'einvoice_auto_issue': True})
        with self.patch_date_today(date(2021, 9, 1)):
            self.env['account.move']._cron_issue_einvoices()
        self.assertRecordValues(self.invoice | invoice2, [{
            'einvoice_state': 'issued',
        }, {
            'einvoice_state': 'issued',
        }])
