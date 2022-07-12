from odoo.addons.to_einvoice_common.tests.test_base import TestBaseEinvoiceCommon
from odoo.tests import tagged


@tagged('external', '-standard')
class TestL10nVnEinvoiceSale(TestBaseEinvoiceCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super(TestL10nVnEinvoiceSale, cls).setUpClass(chart_template_ref)
        cls.company.write({'einvoice_provider': 'vninvoice'})
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner_a.id,
        })
        cls.sol_product_order = cls.env['sale.order.line'].create({
            'name': cls.product_a.name,
            'product_id': cls.product_a.id,
            'product_uom_qty': 2,
            'qty_to_invoice': 1,
            'product_uom': cls.product_a.uom_id.id,
            'price_unit': cls.product_a.list_price,
            'order_id': cls.sale_order.id,
            'tax_id': False,
        })
        cls.sale_order.action_confirm()

    def test_create_invoice_line_with_vietnamese(self):
        invoice = self.sale_order._create_invoices()
        self.assertEqual(invoice.invoice_line_ids.name, 'description\nsale vi_VN (product_a)')
