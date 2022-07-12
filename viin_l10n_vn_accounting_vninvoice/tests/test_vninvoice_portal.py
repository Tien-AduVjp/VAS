import base64

from odoo.tests import tagged
from odoo.modules.module import get_module_resource
from odoo.addons.l10n_vn_edi.tests.test_base_portal import TestEInvoicePortalCommon


@tagged('post_install', '-at_install')
class TestVNinvoicePortal(TestEInvoicePortalCommon):

    def setUp(self):
        super(TestVNinvoicePortal, self).setUp()
        with open(get_module_resource('viin_l10n_vn_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_representation_signed.pdf'),
                  'rb') as f:
            self.VNinvoice_representation_signed_pdf = base64.b64encode(f.read()).decode()
        with open(get_module_resource('viin_l10n_vn_accounting_vninvoice', 'tests', 'download_files',
                                      'VNinvoice_representation_signed.xml'),
                  'rb') as f:
            self.VNinvoice_representation_signed_xml = base64.b64encode(f.read()).decode()
        self.invoice.write({
            'legal_number': 'AA/20E000001',
            'einvoice_state': 'issued',
            'einvoice_representation_pdf': self.VNinvoice_representation_signed_pdf,
        })

    def test_download_xml_from_portal(self):
        url_get_xml = self.invoice.get_portal_url(report_type='xml', download=True)
        result = self.url_open(url_get_xml, timeout=None)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content, b'No XML files available yet. Please try again later!')
        self.invoice.write({'check_einvoice_approved_and_signed': True, 'einvoice_official_representation': self.VNinvoice_representation_signed_xml,})
        result = self.url_open(url_get_xml, timeout=None)
        self.assertEqual(base64.b64encode(result.content), self.invoice.einvoice_official_representation)
