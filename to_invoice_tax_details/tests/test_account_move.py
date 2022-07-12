from odoo.tests import tagged
from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install', '-at_install')
class TestInInvoiceWithTaxDetails(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.invoice = cls.init_invoice('in_invoice', products=cls.product_a+cls.product_b)

    def setUp(self):
        super(TestInInvoiceWithTaxDetails, self).setUp()
        self.config = self.env['res.config.settings'].create({})

    def test_10_invoice_line_price_tax(self):
        self.config.show_line_subtotals_tax_selection = 'tax_details'
        for line in self.invoice.invoice_line_ids:
            price_sub_total = line.price_unit * line.quantity
            price_tax = price_sub_total * sum(line.tax_ids.mapped('amount')) / 100
            price_total = price_sub_total + price_tax

            self.assertEqual(price_tax, line.price_tax)
            self.assertEqual(price_sub_total, line.price_subtotal)
            self.assertEqual(price_total, line.price_total)

    def test_20_form_test_access_groups(self):
        group_show_line_tax_details = self.env.ref('to_invoice_tax_details.group_show_line_tax_details')
        group_account_invoice = self.env.ref('account.group_account_invoice')
        self.show_line_tax_user = self.env['res.users'].create({
            'name': 'Show line tax',
            'login': 'test login 1',
            'groups_id': [group_show_line_tax_details.id, group_account_invoice.id]
        })
        self.can_not_show_line_tax_user = self.env['res.users'].create({
            'name': 'Can not show',
            'login': 'test login 2',
            'groups_id': [group_account_invoice.id]
        })
        self.config.show_line_subtotals_tax_selection = 'tax_details'

        invoice_form = Form(self.invoice.with_user(self.show_line_tax_user))
        with invoice_form.invoice_line_ids.edit(0) as line:
            self.assertFalse(line._get_modifier('price_tax', 'invisible'))

        invoice_form = Form(self.invoice.with_user(self.can_not_show_line_tax_user))
        with invoice_form.invoice_line_ids.edit(0) as line:
            self.assertTrue(line._get_modifier('price_tax', 'invisible'))
