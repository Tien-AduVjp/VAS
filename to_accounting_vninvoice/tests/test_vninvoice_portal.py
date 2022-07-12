import base64

from odoo.tests import tagged
from odoo.modules.module import get_module_resource
from odoo.addons.to_einvoice_common.tests.test_base_portal import TestEInvoicePortalCommon


@tagged('post_install', '-at_install')
class TestVNinvoicePortal(TestEInvoicePortalCommon):

    def setUp(self):
        super(TestVNinvoicePortal, self).setUp()
        with open(get_module_resource('to_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_representation_signed.pdf'),
                  'rb') as f:
            VNinvoice_representation_signed_pdf = base64.b64encode(f.read()).decode()
        with open(get_module_resource('to_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_representation_signed.xml'),
                  'rb') as f:
            VNinvoice_representation_signed_xml = base64.b64encode(f.read()).decode()
        self.invoice.write({
            'legal_number': 'AA/20E000001',
            'vninvoice_transactionid': 'zuiqua',
            'vninvoice_representation_xml': VNinvoice_representation_signed_xml,
            'vninvoice_representation_pdf': VNinvoice_representation_signed_pdf,
        })

    def test_download_xml_from_portal(self):
        url_get_xml = self.invoice.get_portal_url(report_type='xml', download=True)
        result = self.url_open(url_get_xml, timeout=None)
        self.assertEquals(result.status_code, 200)
        self.assertEquals(result.content, b'E-invoice is not signed, so you cannot download the XML file')
        self.invoice.write({'check_vninvoice_approved_and_signed': True})
        result = self.url_open(url_get_xml, timeout=None)
        self.assertEquals(base64.b64encode(result.content), self.invoice.vninvoice_representation_xml)
