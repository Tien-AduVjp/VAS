from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class PaymentCommon(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(self, chart_template_ref=None):
        super(PaymentCommon, self).setUpClass(chart_template_ref=chart_template_ref)

    def _create_so(self, partner=False, product=False, price_unit=100000, qty=1):
        so = Form(self.env['sale.order'])
        so.partner_id = partner or self.partner_a
        with so.order_line.new() as so_line:
            so_line.product_id = product or self.product_a
            so_line.product_uom_qty = qty
            so_line.price_unit = price_unit
            # Removes all existing taxes in the SO line to no change price total
            so_line.tax_id.clear()
        so = so.save()
        return so

    def _create_account_payment(self, amount, sales=[]):
        payment_form = Form(self.env['account.payment'])
        payment_form.partner_type = 'customer'
        payment_form.payment_type = 'inbound'
        payment_form.journal_id = self.env.company.bank_journal_ids[:1]
        for so in sales:
            payment_form.sale_order_ids.add(so)
        payment_form.amount = amount
        return payment_form.save()
