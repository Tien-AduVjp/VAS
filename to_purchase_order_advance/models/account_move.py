import json

from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_payments_widget_to_reconcile_info(self):
        Line = self.env['account.move.line']
        for move in self:
            po_ids = move.invoice_line_ids.mapped('purchase_line_id.order_id')
            this = move.with_context(advance_payment_purchase_ids=po_ids.ids)
            super(AccountMove, this)._compute_payments_widget_to_reconcile_info()

            info = json.loads(this.invoice_outstanding_credits_debits_widget)
            if info:
                for content in info.get('content', []):
                    move_line = Line.browse(content.get('id', False))
                    move_line.read([])
                    if move_line.payment_id.purchase_order_ids:
                        content['payment_with_po'] = True
            move.invoice_outstanding_credits_debits_widget = json.dumps(info)
            move.invoice_has_outstanding = this.invoice_has_outstanding
