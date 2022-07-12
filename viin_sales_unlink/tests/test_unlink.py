from odoo.tests import Form, TransactionCase, tagged
from odoo.exceptions import UserError

@tagged('post_install', '-at_install')
class TestSalesUnlink(TransactionCase):

    def setUp(self):
        super(TestSalesUnlink, self).setUp()

        # Enable feature prevent unlink
        self.env.company.prevent_unlink_sales_having_invoices = True

        #Create data for SO
        product1 = self.env.ref('product.consu_delivery_01')
        product2 = self.env.ref('product.consu_delivery_01')
        (product1 | product2).invoice_policy = 'order'

        partner = self.env.ref('base.res_partner_1')

        # Create data SO
        so = Form(self.env['sale.order'])
        so.partner_id = partner
        with so.order_line.new() as so_line:
            so_line.product_id = product1
            so_line.price_unit = 1000
        with so.order_line.new() as so_line:
            so_line.product_id = product2
            so_line.price_unit = 1500

        self.so = so.save()
        self.so.action_confirm()

        journal_sale = self.env['account.journal'].create({
            'name': 'Sale Journal - Test',
            'code': 'AJ-SALE',
            'type': 'sale',
            'company_id': self.env.company.id,
        })

        context = {
            'active_model': 'sale.order',
            'active_ids': [self.so.id],
            'active_id': self.so.id,
            'default_journal_id': journal_sale.id,
        }
        self.SaleAdvancePaymentInv = self.env['sale.advance.payment.inv'].with_context(context)

    def test_unlink_with_single_invoiced(self):
        payment = self.SaleAdvancePaymentInv.create({
            'advance_payment_method': 'delivered'
        })
        # Create invoice from so
        payment.create_invoices()
        # To avoid any other constraints, set state sale order to draft.
        self.so.state = 'draft'

        # Remove first invoice line
        with Form(self.so.invoice_ids) as invoice:
            invoice.invoice_line_ids.remove(index=0)

        # Can remove first so line but not the others
        self.so.order_line[0].unlink()
        with self.assertRaises(UserError):
            self.so.order_line[0].unlink()
        with self.assertRaises(UserError):
            self.so.unlink()

        # Unlink all invoice line to remove so linking
        with Form(self.so.invoice_ids) as invoice:
            invoice.invoice_line_ids.remove(index=0)

        # Can remove so and so lines when invoice is unlinked
        self.so.order_line.unlink()
        self.so.unlink()

    def test_unlink_with_multi_invoiced(self):
        payment = self.SaleAdvancePaymentInv.create({
            'advance_payment_method': 'delivered'
        })
        # Create the first invoice
        payment.create_invoices()

        # Remove invoice line to create extra invoice
        with Form(self.so.invoice_ids) as invoice:
            invoice.invoice_line_ids.remove(index=0)

        # Create the second invoice
        payment.create_invoices()

        # To avoid any other constraints, set state sale order to draft.
        self.so.state = 'draft'

        # Unlink first invoice
        self.so.invoice_ids[0].unlink()

        # Can't unlink SO because it still linking the second invoice
        self.so.order_line[0].unlink()
        with self.assertRaises(UserError):
            self.so.unlink()

        # Unlink the second invoice
        self.so.invoice_ids.unlink()

        # Can unlink all
        self.so.order_line.unlink()
        self.so.unlink()
