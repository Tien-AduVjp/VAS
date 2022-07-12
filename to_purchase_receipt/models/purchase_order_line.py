from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _compute_qty_invoiced(self):
        res = super(PurchaseOrderLine, self)._compute_qty_invoiced()

        for r in self:
            qty = 0.0
            for inv_line in r.invoice_lines:
                if inv_line.move_id.state != 'cancel':
                    if inv_line.move_id.move_type == 'in_receipt':
                        qty += inv_line.product_uom_id._compute_quantity(inv_line.quantity, r.product_uom)
            r.qty_invoiced += qty

            # compute qty_to_invoice
            if r.order_id.state in ['purchase', 'done']:
                r.qty_to_invoice = r.qty_to_invoice - qty
        return res
