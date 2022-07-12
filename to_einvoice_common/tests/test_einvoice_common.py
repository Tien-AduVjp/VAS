from odoo import fields
from odoo.addons.to_einvoice_common.tests.test_base import TestBaseEinvoiceCommon
from odoo.exceptions import ValidationError
from odoo.tests import tagged, Form


@tagged('external', '-standard')
class TestEinvoiceCommon(TestBaseEinvoiceCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

    def test_prepare_invoice_tax_data(self):
        self.invoice = self.init_invoice('out_invoice', invoice_date=fields.Date.today())
        with self.assertRaises(ValidationError, msg="Multiple taxes on a single invoice line"):
            self.invoice._prepare_invoice_tax_data()
        invoice_form = Form(self.invoice)
        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.tax_ids.clear()
            line_form.tax_ids.add(self.tax_sale_b)
        invoice_form.save()
        result = self.invoice._prepare_invoice_tax_data()
        self.assertEqual(result, [
            {'id': self.tax_sale_a.id, 'name': self.tax_sale_a.tax_group_id.name, 'tax_group_id': self.tax_sale_a.tax_group_id.id,
             'percent': 15.0, 'amount_type': 'percent', 'amount': 1200.0, 'amount_tax': 180.0},
        ])
