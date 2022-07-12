from odoo.tests import tagged, Form

from odoo.addons.l10n_vn_edi.tests.test_base import TestBaseEinvoiceCommon
from odoo.addons.to_invoice_line_summary.tests.test_base import TestInvoiceLineSummaryBase


@tagged('post_install', 'external', '-standard')
class TestEinvoiceSummary(TestBaseEinvoiceCommon, TestInvoiceLineSummaryBase):

    def test_prepare_einvoice_line_summary_name(self):
        invoice_form = Form(self.invoice)
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.product_id = self.product_a_2
        invoice_form.save()
        self.invoice.action_compute_invoice_line_summary()
        self.assertEqual(len(self.invoice.invoice_line_summary_ids), 3)
        self.assertEqual(self.invoice.invoice_line_summary_ids[0]._prepare_einvoice_line_summary_name(),
                         'product_a_vi_VN (product_a)')
        self.company_data['default_journal_sale'].write({'einvoice_item_name': 'invoice_line_product'})
        self.assertEqual(self.invoice.invoice_line_summary_ids[0]._prepare_einvoice_line_summary_name(),
                         'product_a_vi_VN (product_a)')
        self.invoice.write({'invoice_line_summary_mode': 'product_template_unit_price_tax_discount'})
        self.invoice.action_compute_invoice_line_summary()
        self.assertEqual(len(self.invoice.invoice_line_summary_ids), 2)
        self.assertEqual(self.invoice.invoice_line_summary_ids[0]._prepare_einvoice_line_summary_name(),
                         'product_a_vi_VN (product_a)')
        self.company_data['default_journal_sale'].write({'einvoice_item_name': 'invoice_line_name'})
        self.assertEqual(self.invoice.invoice_line_summary_ids[0]._prepare_einvoice_line_summary_name(),
                         'product_a_vi_VN (product_a)')
