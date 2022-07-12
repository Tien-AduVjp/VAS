import base64

from odoo.tests import tagged
from odoo.modules.module import get_module_resource
from odoo.addons.to_einvoice_common.tests.test_base_portal import TestEInvoicePortalCommon


@tagged('post_install', '-at_install')
class TestSinvoicePortal(TestEInvoicePortalCommon):

    def setUp(self):
        super(TestSinvoicePortal, self).setUp()
        with open(get_module_resource('to_accounting_sinvoice', 'tests', 'download_files',
                                      'representation_file.pdf'),
                  'rb') as f:
            representation_pdf = base64.b64encode(f.read()).decode()
        with open(get_module_resource('to_accounting_sinvoice', 'tests', 'download_files',
                                      'representation_file.zip'),
                  'rb') as f:
            representation_zip = base64.b64encode(f.read()).decode()
        self.invoice.write({
            'legal_number': 'AA/20E000001',
            'sinvoice_transactionid': 'zuiqua',
            'sinvoice_representation_zip': representation_zip,
            'sinvoice_representation_pdf': representation_pdf,
        })

    def test_download_xml_from_portal(self):
        url_get_xml = self.invoice.get_portal_url(report_type='xml', download=True)
        result = self.url_open(url_get_xml)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(base64.b64encode(result.content), self.invoice.sinvoice_representation_zip)
