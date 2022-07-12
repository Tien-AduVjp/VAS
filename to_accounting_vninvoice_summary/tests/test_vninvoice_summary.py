from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError
from odoo.addons.to_accounting_vninvoice.tests.test_base import TestVNinvoiceBaseCommon
from odoo.tests import tagged


@tagged('external', '-standard')
class TestEinvoiceSummary(TestVNinvoiceBaseCommon):

    def setUp(self):
        super(TestEinvoiceSummary, self).setUp()
        self.invoice.write({'invoice_display_mode': 'invoice_line_summary_lines'})

    def test_cannot_issue_invoice(self):
        self.check_issue_einvoice_raise_excep()
        with self.assertRaises(UserError, msg="Later e-invoice existing"):
            self.issue_vninvoice()
            self.create_invoice(invoice_date=self.invoice_date - relativedelta(days=1)).issue_einvoices()
    
    def test_00_prepare_einvoice_lines_data(self):
        # test with included price tax
        self.tax_sale_b.write({'price_include': True})
        invoice = self.create_invoice()
        invoice.action_compute_invoice_line_summary()
        result = invoice.invoice_line_ids._prepare_einvoice_lines_data()
        self.assertEqual(result, [
            {'index': 1, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
             'productId': 'default_code_product_a', 'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0,
             'vatPercent': 10, 'vatPercentDisplay': 'Thuế GTGT phải nộp 10%', 'vatAmount': 100.0,
             'note': '[default_code_product_a] product_a; description; sale vi_VN (product_a; description; sale)',
             'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 1100.0},
            {'index': 2, 'productName': 'product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
             'productId': 'default_code_product_b',
             'unitPrice': 181.82, 'quantity': 1.0, 'amount': 182.0, 'vatPercent': 10,
             'vatPercentDisplay': 'Thuế GTGT phải nộp 10% (Copy)', 'vatAmount': 18.0,
             'note': '[default_code_product_b] product_b (product_b)', 'discountAmountBeforeTax': 0.0,
             'discountPercentBeforeTax': 0, 'paymentAmount': 200.0},
        ])
        
    def test_prepare_vninvoice_data(self):
        self.invoice.action_compute_invoice_line_summary()
        self.assertEqual(self.invoice._prepare_vninvoice_data(), [{
            'invoiceDate': '2021-09-01T00:00:00.000000',
            'Note': '',
            'templateNo': '01GTKT0/001',
            'serialNo': 'AA/20E',
            'exchangeRate': 1.0,
            'paymentMethod': 'Tiền mặt hoặc chuyển khoản',
            'paymentDate': '2021-09-01T00:00:00.000000',
            'totalAmount': 2200.0,
            'totalVatAmount': 120.0,
            'totalPaymentAmount': 2320.0,
            'totalDiscountAmountBeforeTax': 0.0,
            'totalDiscountPercentAfterTax': 0,
            'totalDiscountAmountAfterTax': 0.0,
            'buyerEmail': 'khaihoan@example.viindoo.com',
            'buyerFullName': 'partner_a',
            'buyerLegalName': '',
            'buyerTaxCode': '123456789',
            'buyerAddressLine': '31 Bạch Đằng, Hải Phòng, United States',
            'buyerDistrictName': '',
            'buyerCityName': 'Hải Phòng',
            'buyerCountryCode': 'US',
            'buyerPhoneNumber': '0978654321',
            'buyerFaxNumber': '',
            'buyerBankName': '',
            'buyerBankAccount': '',
            'idTransaction': 'access_token',
            'id': 'access_token',
            'userNameCreator': 'Because I am accountman!',
            'idBuyer': str(self.partner_a.id),
            'buyerGroupCode': '',
            'buyerCode': str(self.partner_a.id),
            'idBuyerGroup': '',
            'buyerGroupName': '',
            'currency': 'VND',
            'invoiceDetails': [
                {'index': 1, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
                 'productId': 'default_code_product_a', 'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0,
                 'vatPercent': 10, 'vatPercentDisplay': 'Thuế GTGT phải nộp 10%', 'vatAmount': 100.0, 'note': '',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 1100.0},
                {'index': 2, 'productName': 'product_a_vi_VN (product_a)', 'unitName': 'Đơn vị\n(Units)',
                 'productId': 'default_code_product_a', 'unitPrice': 1000.0, 'quantity': 1.0, 'amount': 1000.0,
                 'vatPercent': -1, 'vatPercentDisplay': 'Không thuộc ĐT chịu thuế GTGT', 'vatAmount': 0.0, 'note': '',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 1000.0},
                {'index': 3, 'productName': 'product_b (product_b)', 'unitName': 'Tá\n(Dozens)',
                 'productId': 'default_code_product_b', 'unitPrice': 200.0, 'quantity': 1.0, 'amount': 200.0,
                 'vatPercent': 10, 'vatPercentDisplay': 'Thuế GTGT phải nộp 10% (Copy)', 'vatAmount': 20.0, 'note': '',
                 'discountAmountBeforeTax': 0.0, 'discountPercentBeforeTax': 0, 'paymentAmount': 220.0}
            ],
            'invoiceTaxBreakdowns': [
                {'vatPercent': 10, 'name': 'Thuế GTGT 10%', 'vatAmount': 120.0},
                {'vatPercent': -1, 'name': 'VAT Exemption', 'vatAmount': 0}
            ]
        }])
