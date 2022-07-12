from odoo.tests.common import Form
from odoo.tests import tagged
from odoo.addons.to_invoice_line_summary.tests.test_base import TestInvoiceLineSummaryBase


@tagged('post_install', '-at_install')
class TestInvoiceLineSummary(TestInvoiceLineSummaryBase):

    def test_summarize_lines_with_product_unit_price_tax_discount(self):
        invoice = self.create_invoice(products=[self.product_a, self.product_a])
        invoice_form = Form(invoice)
        self.assertEqual(len(invoice.invoice_line_summary_ids), 1)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 2.0, 'price_unit': 1000.0, 'price_subtotal': 2000.0,
             'price_total': 2300.0},
        ])
        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.price_unit = 2000.0
        invoice = invoice_form.save()
        self.assertEqual(len(invoice.invoice_line_summary_ids), 2)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 1000.0, 'price_subtotal': 1000.0,
             'price_total': 1150.0},
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 2000.0, 'price_subtotal': 2000.0,
             'price_total': 2300.0}
        ])

        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.product_uom_id = self.env['uom.uom']
            line_form.price_unit = 3000.0
        invoice = invoice_form.save()
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 3000.0, 'price_subtotal': 3000.0,
             'price_total': 3450.0},
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 2000.0, 'price_subtotal': 2000.0,
             'price_total': 2300.0}
        ])
        
    def test_summarize_lines_with_product_unit_price_tax_discount_2(self):
        invoice = self.create_invoice(products=[self.product_a, self.product_a])
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.price_unit = 2000
        invoice = invoice_form.save()
        self.assertEqual(len(invoice.invoice_line_summary_ids), 2)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 1000.0, 'price_subtotal': 1000.0,
             'price_total': 1150.0},
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 2000.0, 'price_subtotal': 2000.0,
             'price_total': 2300.0}
        ])

    def test_summarize_lines_with_product_tax_discount(self):
        invoice = self.create_invoice(invoice_line_summary_mode='product_tax_discount',
                                      products=[self.product_a, self.product_a])
        invoice_form = Form(invoice)
        self.assertEqual(len(invoice.invoice_line_summary_ids), 1)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 2.0, 'price_unit': 1000.0, 'price_subtotal': 2000.0,
             'price_total': 2300.0},
        ])
        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.product_uom_id = self.env['uom.uom']
            line_form.price_unit = 2000.0
        invoice = invoice_form.save()
        self.assertEqual(len(invoice.invoice_line_summary_ids), 1)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 2.0, 'price_unit': 1500.0, 'price_subtotal': 3000.0,
             'price_total': 3450.0},
        ])

    def test_summarize_lines_with_product_tax_discount_2(self):
        invoice = self.create_invoice(invoice_line_summary_mode='product_tax_discount',
                                      products=[self.product_a, self.product_a], discount=10)
        self.assertEqual(len(invoice.invoice_line_summary_ids), 1)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 2.0, 'price_unit': 1000.0, 'discount': 10,
             'price_subtotal': 1800.0, 'price_total': 2070.0},
        ])

    def test_summarize_lines_with_product_template_unit_price_tax_discount(self):
        invoice = self.create_invoice(invoice_line_summary_mode='product_template_unit_price_tax_discount',
                                      products=[self.product_a, self.product_a_2])
        invoice_form = Form(invoice)
        self.assertEqual(len(invoice.invoice_line_summary_ids), 1)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_tmpl_id': self.product_template_a.id, 'quantity': 2.0, 'price_unit': 1000.0,
             'price_subtotal': 2000.0,
             'price_total': 2300.0},
        ])
        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.product_uom_id = self.env['uom.uom']
            line_form.price_unit = 2000.0
        invoice = invoice_form.save()
        self.assertEqual(len(invoice.invoice_line_summary_ids), 2)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_tmpl_id': self.product_template_a.id, 'quantity': 1.0, 'price_unit': 1000.0,
             'price_subtotal': 1000.0,
             'price_total': 1150.0},
            {'product_tmpl_id': self.product_template_a.id, 'quantity': 1.0, 'price_unit': 2000.0,
             'price_subtotal': 2000.0,
             'price_total': 2300.0}
        ])

    def test_summarize_lines_with_product_template_tax_discount(self):
        invoice = self.create_invoice(invoice_line_summary_mode='product_template_tax_discount',
                                      products=[self.product_a, self.product_a_2])
        invoice_form = Form(invoice)
        self.assertEqual(len(invoice.invoice_line_summary_ids), 1)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_tmpl_id': self.product_template_a.id, 'quantity': 2.0, 'price_unit': 1000.0,
             'price_subtotal': 2000.0,
             'price_total': 2300.0},
        ])
        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.price_unit = 2000.0
        invoice = invoice_form.save()
        self.assertEqual(len(invoice.invoice_line_summary_ids), 1)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_tmpl_id': self.product_template_a.id, 'quantity': 2.0, 'price_unit': 1500.0,
             'price_subtotal': 3000.0,
             'price_total': 3450.0},
        ])

    def test_summarize_lines_with_different_discount(self):
        invoice = self.create_invoice(products=[self.product_a, self.product_a])
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.discount = 50.0
        invoice = invoice_form.save()
        self.assertEqual(len(invoice.invoice_line_summary_ids), 2)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 1000.0, 'price_subtotal': 1000.0,
             'discount': 0.0, 'price_total': 1150.0},
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 1000.0, 'price_subtotal': 500.0,
             'discount': 50.0, 'price_total': 575.0}
        ])

    def test_summarize_lines_with_different_taxes(self):
        invoice = self.create_invoice(products=[self.product_a, self.product_a])
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.tax_ids.clear()
        invoice = invoice_form.save()
        self.assertEqual(len(invoice.invoice_line_summary_ids), 2)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 1000.0, 'price_subtotal': 1000.0,
             'invoice_line_tax_ids': [self.tax_sale_a.id], 'price_total': 1150.0},
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 1000.0, 'price_subtotal': 1000.0,
             'invoice_line_tax_ids': [], 'price_total': 1000.0},
        ])

    def test_recompute_summary_lines(self):
        invoice = self.create_invoice(products=[self.product_a, self.product_a])
        invoice_form = Form(invoice)
        self.assertEqual(len(invoice.invoice_line_summary_ids), 1)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 2.0, 'price_unit': 1000.0, 'price_subtotal': 2000.0,
             'price_total': 2300.0},
        ])
        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.product_uom_id = self.env['uom.uom']
            line_form.price_unit = 2000.0
        invoice = invoice_form.save()
        self.assertEqual(len(invoice.invoice_line_summary_ids), 2)
        self.assertRecordValues(invoice.invoice_line_summary_ids, [
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 1000.0, 'price_subtotal': 1000.0,
             'price_total': 1150.0},
            {'product_id': self.product_a.id, 'quantity': 1.0, 'price_unit': 2000.0, 'price_subtotal': 2000.0,
             'price_total': 2300.0}
        ])
