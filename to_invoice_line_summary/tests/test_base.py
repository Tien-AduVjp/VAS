from odoo import fields
from odoo.tests.common import Form
from odoo.tests import tagged
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install', '-at_install')
class TestInvoiceLineSummaryBase(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.product_attribute = cls.env.ref('product.product_attribute_2')
        cls.product_attribute_value_1 = cls.env.ref('product.product_attribute_value_3')
        cls.product_attribute_value_2 = cls.env.ref('product.product_attribute_value_4')
        cls.product_template_a = cls.product_a.product_tmpl_id
        cls.product_template_attribute_line_a = cls.env['product.template.attribute.line'].create({
            'product_tmpl_id': cls.product_template_a.id,
            'attribute_id': cls.product_attribute.id,
            'value_ids': [(6, 0, (cls.product_attribute_value_1 + cls.product_attribute_value_2).ids)]
        })
        cls.product_a = cls.product_template_a.product_variant_ids[0]
        cls.product_a_2 = cls.product_template_a.product_variant_ids[1]

    @classmethod
    def create_invoice(cls, invoice_line_summary_group_mode='product_unit_price_tax_discount', products=[], discount=0):
        move_form = Form(cls.env['account.move'].with_context(default_move_type='out_invoice'))
        move_form.invoice_date = fields.Date.to_date('2021-01-01')
        move_form.partner_id = cls.partner_a
        move_form.invoice_line_summary_group_mode = invoice_line_summary_group_mode
        for product in products:
            with move_form.invoice_line_ids.new() as line_form:
                line_form.product_id = product
                line_form.discount = discount
        return move_form.save()
