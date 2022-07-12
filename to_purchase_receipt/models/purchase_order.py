from odoo import api, fields, models, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    count_receipt = fields.Integer(compute="_compute_count_receipt_invoice", string='Only Receipt Count', copy=False, store=True)
    count_invoice = fields.Integer(compute="_compute_count_receipt_invoice", string='Only Invoice Count', copy=False, store=True)
    
    @api.depends('invoice_ids', 'invoice_ids.type', 'invoice_ids.state')
    def _compute_count_receipt_invoice(self):
        for order in self:
            invoices = order.invoice_ids
            order.count_invoice = len(invoices.filtered(lambda r: r.type != "in_receipt" and r.state != "cancel"))  # count invoices
            order.count_receipt = len(invoices.filtered(lambda r: r.type == "in_receipt" and r.state != "cancel"))  # count receipts

    @api.constrains('count_receipt','count_invoice')
    def _check_invoice_ids(self):
        for r in self:
            if r.count_receipt > 0 and r.count_invoice > 0:
                raise ValidationError(_("You cannot create both invoice and receipt on Purchase Order: %s.") %r.name)
                  
    def action_view_invoice(self):
        create_receipt = self.env.context.get('create_receipt', False)
        create_invoice = self.env.context.get('create_bill', False)
             
        if create_invoice and self.count_receipt > 0:
            raise ValidationError(_("Receipts was created from this purchase order, You can't create Invoice"))
        if create_receipt and self.count_invoice > 0:
            raise ValidationError(_("Invoice was created from this purchase order, You can't create Receipt"))
        create_button = create_invoice or create_receipt
            
        res = super(PurchaseOrder, self.with_context(create_bill=create_button)).action_view_invoice()
        if create_receipt:
            res['context']['default_type'] = 'in_receipt'
        return res
 
            
