from odoo.tests.common import Form

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class PaymentCommon(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(self, chart_template_ref=None):
        super(PaymentCommon, self).setUpClass(chart_template_ref=chart_template_ref)

    def _create_po(self, partner=False, product=False, price_unit=100000, qty=1):
        po = Form(self.env['purchase.order'])
        po.partner_id = partner or self.partner_a
        with po.order_line.new() as po_line:
            po_line.product_id = product or self.product_a
            po_line.product_qty = qty
            po_line.price_unit = price_unit
            # Removes all existing taxes in the PO line to no change price total
            po_line.taxes_id.clear()
        po = po.save()
        return po

    def _create_account_payment(self, amount, purchases=[]):
        payment_form = Form(self.env['account.payment'])
        payment_form.partner_type = 'supplier'
        payment_form.payment_type = 'outbound'
        payment_form.journal_id = self.env.company.bank_journal_ids[:1]
        for po in purchases:
            payment_form.purchase_order_ids.add(po)
        payment_form.amount = amount
        return payment_form.save()
