from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError
from odoo.addons.viin_l10n_vn_accounting_vninvoice.tests.test_base import TestVNinvoiceBaseCommon
from odoo.addons.to_invoice_line_summary.tests.test_base import TestInvoiceLineSummaryBase

from odoo.tests import tagged


@tagged('post_install', 'external', '-standard')
class TestEinvoiceSummary(TestVNinvoiceBaseCommon, TestInvoiceLineSummaryBase):

    def setUp(self):
        super(TestEinvoiceSummary, self).setUp()
        self.invoice.write({'invoice_display_mode': 'invoice_line_summary_lines'})
        self.product_a_2.default_code = 'default_code_product_a_2'

    def test_cannot_issue_invoice(self):
        self.check_issue_einvoice_raise_excep()
        with self.assertRaises(UserError, msg="Later e-invoice existing"):
            self.issue_vninvoice()
            self.create_invoice(invoice_date=self.invoice_date - relativedelta(days=1)).issue_einvoices()

    def test_00_prepare_einvoice_lines_data(self):
        # test with included price tax
        self.tax_sale_a.write({'price_include': True})
        invoice = self.create_invoice(products=[self.product_a, self.product_a, self.product_a_2])
        result = invoice.invoice_line_summary_ids._prepare_einvoice_summary_lines_data()
        self.assertEqual(result, [
            {'index': 1, 'productId': 'default_code_product_a', 'productName': 'product_a_vi_VN (product_a)',
             'unitName': 'Đơn vị\n(Units)', 'unitPrice': 909.09, 'quantity': 2.0, 'amount': 1818.0, 'vatPercent': 10,
             'vatPercentDisplay': 'Thuế GTGT phải nộp 10%', 'vatAmount': 182.0, 'note': '', 'discountAmountBeforeTax': 0.0,
             'discountPercentBeforeTax': 0, 'paymentAmount': 2000.0},
            {'index': 2, 'productId': 'default_code_product_a_2', 'productName': 'product_a_vi_VN (product_a)',
             'unitName': 'Đơn vị\n(Units)', 'unitPrice': 909.09, 'quantity': 1.0, 'amount': 909.0, 'vatPercent': 10,
             'vatPercentDisplay': 'Thuế GTGT phải nộp 10%', 'vatAmount': 91.0, 'note': '', 'discountAmountBeforeTax': 0.0,
             'discountPercentBeforeTax': 0, 'paymentAmount': 1000.0}]
            )

    def test_prepare_vninvoice_data(self):
        invoice = self.create_invoice(products=[self.product_a, self.product_a_2])
        self.assertEqual(invoice._prepare_vninvoice_data(), [{
            "invoiceDate": "2021-01-01",
            "userNameCreator": "Because I am accountman!",
            "invoiceDetails": [
                {"index": 1, "productName": "[default_code_product_a] product_a_vi_VN (Trắng); description; sale vi_VN (product_a (White); description; sale)",
                 "unitName": "Đơn vị\n(Units)", "unitPrice": 1000.0, "quantity": 1.0, "amount": 1000.0, "vatPercent": 10,
                 "vatPercentDisplay": "Thuế GTGT phải nộp 10%", "vatAmount": 100.0,
                 "note": "[default_code_product_a] product_a_vi_VN (Trắng); description; sale vi_VN (product_a (White); description; sale)",
                 "discountAmountBeforeTax": 0.0, "discountPercentBeforeTax": 0, "paymentAmount": 1100.0, "productId": "default_code_product_a"},
                {"index": 2, "productName": "[default_code_product_a_2] product_a_vi_VN (Đen); description; sale vi_VN (product_a (Black); description; sale)",
                 "unitName": "Đơn vị\n(Units)", "unitPrice": 1000.0, "quantity": 1.0, "amount": 1000.0, "vatPercent": 10,
                 "vatPercentDisplay": "Thuế GTGT phải nộp 10%", "vatAmount": 100.0,
                 "note": "[default_code_product_a_2] product_a_vi_VN (Đen); description; sale vi_VN (product_a (Black); description; sale)",
                 "discountAmountBeforeTax": 0.0, "discountPercentBeforeTax": 0, "paymentAmount": 1100.0, "productId": "default_code_product_a_2"}],
            "invoiceTaxBreakdowns": [{"vatPercent": 10, "name": "Thuế GTGT 10%", "vatAmount": 200.0}],
            "Note": "",
            "paymentMethod": "Tiền mặt hoặc chuyển khoản",
            "totalAmount": 2000.0,
            "totalVatAmount": 200.0,
            "totalPaymentAmount": 2200.0,
            "exchangeRate": 1,
            "paymentDate": "2021-01-01T00:00:00.000000",
            "buyerEmail": "khaihoan@example.viindoo.com",
            "buyerFullName": "partner_a",
            "buyerLegalName": "",
            "buyerTaxCode": "",
            "buyerAddressLine": "31 Bạch Đằng, Hải Phòng, United States",
            "buyerDistrictName": "",
            "buyerCityName": "Hải Phòng",
            "buyerCountryCode": "US",
            "buyerPhoneNumber": "0978654321",
            "buyerFaxNumber": "",
            "buyerBankName": "",
            "buyerBankAccount": "",
            "idBuyer": str(self.partner_a.id),
            "buyerGroupCode": "",
            "buyerCode": str(self.partner_a.id),
            "idBuyerGroup": "",
            "buyerGroupName": "",
            "currency": "VND",
            "templateNo": "01GTKT0/001",
            "serialNo": "VN/21E",
            "id": invoice.access_token,
            "idTransaction": invoice.access_token}
        ])
