from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    count_receipt = fields.Integer(compute='_compute_count_receipt_invoice', string='Only Receipt Count')
    count_invoice = fields.Integer(compute='_compute_count_receipt_invoice', string='Only Invoice Count')

    def _compute_count_receipt_invoice(self):
        for r in self:
            invoices = r.invoice_ids
            r.count_invoice = len(invoices.filtered(lambda r: r.move_type != 'in_receipt' and r.state != 'cancel'))  # count invoices
            r.count_receipt = len(invoices.filtered(lambda r: r.move_type == 'in_receipt' and r.state != 'cancel'))  # count receipts

    @api.constrains('invoice_ids')
    def _check_invoice_ids(self):
        for r in self:
            if r.count_receipt and r.count_invoice:
                raise ValidationError(_("You may not have both invoices and receipts for the same purchase order `%s`. Either should be fine.") % r.name)

    def action_create_invoice(self):
        create_receipt = self.env.context.get('create_receipt', False)
        create_invoice = self.env.context.get('create_bill', False)
        if create_receipt:
            self = self.with_context(default_move_type='in_receipt')

        for r in self:
            if create_invoice and r.count_receipt:
                raise ValidationError(_("Receipts was created from this purchase order, You can't create Invoice"))
            if create_receipt and r.count_invoice:
                raise ValidationError(_("Invoice was created from this purchase order, You can't create Receipt"))

        return super(PurchaseOrder, self).action_create_invoice()
