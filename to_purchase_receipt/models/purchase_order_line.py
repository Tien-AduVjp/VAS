from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        super(PurchaseOrderLine, self)._compute_qty_invoiced()

        for r in self:
            qty = 0.0
            for inv_line in r.invoice_lines:
                if inv_line.move_id.state not in ['cancel']:
                    if inv_line.move_id.type == 'in_receipt':
                        qty += inv_line.product_uom_id._compute_quantity(inv_line.quantity, r.product_uom)
            r.qty_invoiced += qty
