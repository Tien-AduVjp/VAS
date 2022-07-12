from odoo import fields
from odoo.addons.l10n_vn_edi.tests.test_base import TestBaseEinvoiceCommon
from odoo.addons.account_edi.tests.common import AccountEdiTestCommon
from odoo.exceptions import ValidationError, AccessError, UserError
from odoo.tests import tagged, Form


@tagged('post_install', '-at_install')
class TestL10nVnEdi(AccountEdiTestCommon, TestBaseEinvoiceCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None, edi_format_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref, edi_format_ref='l10n_vn_edi.edi_vn_xml')
        cls.internal_user = cls.env['res.users'].create({
            'name': 'user_internal',
            'login': 'user_internal@example.com',
            'email': 'user_internal@example.com',
            'groups_id': [(6, 0, cls.env.ref('base.group_user').ids)],
        })
        cls.user_accountant = cls.env['res.users'].create({
            'name': 'user_accountant',
            'login': 'user_accountant@example.com',
            'email': 'user_accountant@example.com',
            'groups_id': [(6, 0, cls.env.ref('account.group_account_invoice').ids)],
        })
        cls.tax_10 = cls.env['account.tax'].create({
            'name': 'tax_10',
            'amount_type': 'percent',
            'amount': 10,
            'type_tax_use': 'purchase',
            'include_base_amount': True,
            'sequence': 10,
        })
        cls.invoice = cls.init_invoice('out_invoice', invoice_date=cls.invoice_date,
                                       products=cls.product_a + cls.product_b)
        cls.env['account.move.line'].create({
            'name': 'line note',
            'display_type': 'line_note',
            'move_id': cls.invoice.id,
        })
        cls.expected_values = """
            <inv:invoice
                xmlns:inv="http://laphoadon.gdt.gov.vn/2014/09/invoicexml/v1"
                xmlns:ns1="http://www.w3.org/2000/09/xmldsig#">
                <inv:invoiceData id="data">
                    <inv:invoiceNumber>INV/2021/09/0001</inv:invoiceNumber>
                    <inv:invoiceName>INV/2021/09/0001</inv:invoiceName>
                    <inv:invoiceIssuedDate>2021-09-01T00:00:00.000000</inv:invoiceIssuedDate>
                    <inv:currencyCode>USD</inv:currencyCode>
                    <inv:exchangeRate>1.0</inv:exchangeRate>
                    <inv:adjustmentType>1</inv:adjustmentType>
                    <inv:sellerLegalName>company_1_data</inv:sellerLegalName>
                    <inv:sellerTaxCode>0201994665</inv:sellerTaxCode>
                    <inv:sellerAddressLine>Kỳ Sơn, Sơn, Kỳ</inv:sellerAddressLine>
                    <inv:sellerEmail>khaihoan@example.viindoo.com</inv:sellerEmail>
                    <inv:sellerPhoneNumber>0918777888</inv:sellerPhoneNumber>
                    <inv:sellerBankAccName></inv:sellerBankAccName>
                    <inv:sellerBankName></inv:sellerBankName>
                    <inv:sellerBankAccount></inv:sellerBankAccount>
                    <inv:sellerContactPersonName></inv:sellerContactPersonName>
                    <inv:sellerSignedPersonName></inv:sellerSignedPersonName>
                    <inv:sellerSubmittedPersonName></inv:sellerSubmittedPersonName>
                    <inv:buyerDisplayName>partner_a</inv:buyerDisplayName>
                    <inv:buyerLegalName>partner_a</inv:buyerLegalName>
                    <inv:buyerTaxCode>123456789</inv:buyerTaxCode>
                    <inv:BuyerCode></inv:BuyerCode>
                    <inv:buyerAddressLine>31 Bạch Đằng, Hải Phòng, United States, Bạch Đằng, 31</inv:buyerAddressLine>
                    <inv:buyerPhoneNumber>0978654321</inv:buyerPhoneNumber>
                    <inv:buyerEmail>khaihoan@example.viindoo.com</inv:buyerEmail>
                    <inv:buyerBankName></inv:buyerBankName>
                    <inv:buyerBankAccount></inv:buyerBankAccount>
                    <inv:payments>
                        <inv:payment>
                            <inv:paymentMethodName>TM/CK</inv:paymentMethodName>
                            <inv:paymentNote></inv:paymentNote>
                        </inv:payment>
                    </inv:payments>
                    <inv:items>
                        <inv:invoice>
                            <inv:item>
                                <inv:lineNumber>1</inv:lineNumber>
                                <inv:itemName>[default_code_product_a] product_a_vi_VN; description; sale vi_VN (product_a; description; sale)</inv:itemName>
                                <inv:selection>1</inv:selection>
                                <inv:itemCode>default_code_product_a</inv:itemCode>
                                <inv:unitName>Đơn vị\n(Units)</inv:unitName>
                                <inv:unitPrice>1000.0</inv:unitPrice>
                                <inv:quantity>1.0</inv:quantity>
                                <inv:itemTotalAmountWithoutVat>1000.0</inv:itemTotalAmountWithoutVat>
                                <inv:itemTotalAmountWithVat>1150.0</inv:itemTotalAmountWithVat>
                                <inv:vatPercentage>15.0</inv:vatPercentage>
                                <inv:vatAmount>150.0</inv:vatAmount>
                            </inv:item>
                        </inv:invoice>
                        <inv:invoice>
                            <inv:item>
                                <inv:lineNumber>2</inv:lineNumber>
                                <inv:itemName>[default_code_product_b] product_b (product_b)</inv:itemName>
                                <inv:selection>1</inv:selection>
                                <inv:itemCode>default_code_product_b</inv:itemCode>
                                <inv:unitName>Tá\n(Dozens)</inv:unitName>
                                <inv:unitPrice>200.0</inv:unitPrice>
                                <inv:quantity>1.0</inv:quantity>
                                <inv:itemTotalAmountWithoutVat>200.0</inv:itemTotalAmountWithoutVat>
                                <inv:itemTotalAmountWithVat>230.0</inv:itemTotalAmountWithVat>
                                <inv:vatPercentage>15.0</inv:vatPercentage>
                                <inv:vatAmount>30.0</inv:vatAmount>
                            </inv:item>
                        </inv:invoice>
                        <inv:invoice>
                            <inv:item>
                                <inv:lineNumber>3</inv:lineNumber>
                                <inv:itemName>line note</inv:itemName>
                                <inv:selection>2</inv:selection>
                            </inv:item>
                        </inv:invoice>
                    </inv:items>
                    <inv:invoiceTaxBreakdowns>
                        <inv:invoice>
                            <inv:invoiceTaxBreakdown>
                                <inv:vatPercentage>15.0</inv:vatPercentage>
                                <inv:vatTaxableAmount>1200.0</inv:vatTaxableAmount>
                                <inv:vatTaxAmount>180.0</inv:vatTaxAmount>
                            </inv:invoiceTaxBreakdown>
                        </inv:invoice>
                    </inv:invoiceTaxBreakdowns>
                    <inv:totalAmountWithoutVAT>1200.0</inv:totalAmountWithoutVAT>
                    <inv:totalVATAmount>180.0</inv:totalVATAmount>
                    <inv:totalAmountWithVAT>1380.0</inv:totalAmountWithVAT>
                    <inv:totalAmountWithVATFrn>0</inv:totalAmountWithVATFrn>
                    <inv:totalAmountWithVATInWords>Một nghìn ba trăm tám mươi</inv:totalAmountWithVATInWords>
                </inv:invoiceData>
                <ns1:Signature>
                    <ns1:SignedInfo>
                        <ns1:CanonicalizationMethod Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></ns1:CanonicalizationMethod>
                        <ns1:SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#rsa-sha1"></ns1:SignatureMethod>
                        <ns1:Reference URI="#data">
                            <ns1:Transforms>
                                <ns1:Transform Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature"></ns1:Transform>
                                <ns1:Transform Algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"></ns1:Transform>
                            </ns1:Transforms>
                            <ns1:DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></ns1:DigestMethod>
                            <ns1:DigestValue></ns1:DigestValue>
                        </ns1:Reference>
                    </ns1:SignedInfo>
                    <ns1:SignatureValue></ns1:SignatureValue>
                    <ns1:KeyInfo>
                        <ns1:X509Data>
                            <ns1:X509SubjectName></ns1:X509SubjectName>
                            <ns1:X509Certificate></ns1:X509Certificate>
                        </ns1:X509Data>
                    </ns1:KeyInfo>
                </ns1:Signature>
            </inv:invoice>
        """

    def test_prepare_invoice_tax_data(self):
        invoice = self.invoice
        with self.assertRaises(ValidationError, msg="Multiple taxes on a single invoice line"):
            with self.env.cr.savepoint():
                invoice.invoice_line_ids[0].write(
                    {'tax_ids': [(6, 0, (self.tax_purchase_a + self.tax_purchase_b).ids)]})
                invoice._prepare_invoice_tax_data()
        result = self.invoice._prepare_invoice_tax_data()
        self.assertEqual(result, [
            {'id': self.tax_sale_a.id, 'name': self.tax_sale_a.tax_group_id.name,
             'tax_group_id': self.tax_sale_a.tax_group_id.id,
             'percent': 15.0, 'amount_type': 'percent', 'amount': 1200.0, 'amount_tax': 180.0},
        ])

    def test_action_prepend_vietnamese_description_to_invoice_lines(self):
        self.invoice.invoice_line_ids[0].write({'name': 'description\nsale'})
        self.invoice.action_prepend_vietnamese_description_to_invoice_lines()
        self.assertEqual(self.invoice.invoice_line_ids[0].name, 'description; sale vi_VN (description; sale)')
        self.assertEqual(self.invoice.invoice_line_ids[2].name, 'line note')
        self.invoice.action_post()
        self.invoice.action_prepend_vietnamese_description_to_invoice_lines()
        self.assertEqual(self.invoice.invoice_line_ids[0].name,
                         'description; sale vi_VN (description; sale vi_VN (description; sale))')
        self.assertEqual(self.invoice.invoice_line_ids[2].name, 'line note')

    def test_action_prepend_vietnamese_description_to_invoice_lines_access_rights(self):
        self.invoice.invoice_line_ids[0].write({'name': 'description\nsale'})
        with self.assertRaises(AccessError):
            self.invoice.with_user(self.internal_user).action_prepend_vietnamese_description_to_invoice_lines()
        self.invoice.with_user(self.user_accountant).action_prepend_vietnamese_description_to_invoice_lines()
        self.assertEqual(self.invoice.invoice_line_ids[0].name, 'description; sale vi_VN (description; sale)')
        self.assertEqual(self.invoice.invoice_line_ids[2].name, 'line note')

    ####################################################
    # Test import
    ####################################################
    def test_update_invoice_edi_xml(self):
        invoice = self._create_empty_vendor_bill()
        invoice_count = len(self.env['account.move'].search([]))
        self.update_invoice_from_file('l10n_vn_edi', 'test_file', '85ZMSNLEBA-AA_20E0000406.xml', invoice)

        self.assertEqual(len(self.env['account.move'].search([])), invoice_count)
        self.assertEqual(invoice.amount_total, 880)

    def test_create_invoice_edi_xml(self):
        invoice_count = len(self.env['account.move'].search([]))
        invoice = self.create_invoice_from_file('l10n_vn_edi', 'test_file', '85ZMSNLEBA-AA_20E0000406.xml')
        self.assertEqual(invoice.amount_total, 880)
        self.assertEqual(len(self.env['account.move'].search([])), invoice_count + 1)

    ####################################################
    # Test export
    ####################################################

    def test_edi_xml(self):
        self.assert_generated_file_equal(self.invoice, self.expected_values)

    def test_export_pdf(self):
        self.invoice.action_post()
        pdf_values = self.edi_format._get_embedding_to_invoice_pdf_values(self.invoice)
        self.assertEqual(pdf_values['name'], 'edi_vn.xml')

    def test_issue_unposted_invoice(self):
        with self.assertRaises(UserError):
            self.invoice._issue_einvoice(raise_error=False)

    def test_issue_posted_invoice(self):
        self.invoice._post(soft=False)
        self.invoice._issue_einvoice(raise_error=False)
