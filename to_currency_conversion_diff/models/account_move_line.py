from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        """
        This override is to add currency conversion diff. move lines of the related online payment to Self
        to ensure that all the related move lines will be taken into account for reconcilating with invoices.
        """
        related_online_payments = self.mapped('payment_id').filtered(
            lambda p: p.payment_transaction_id and p.payment_transaction_id.sudo().currency_id != p.currency_id
            )
        related_unreconciled_payment_lines = self.env['account.move.line'].search(related_online_payments._get_unreconciled_payment_move_lines_domain())
        if related_unreconciled_payment_lines:
            self |= related_unreconciled_payment_lines
        self = self.filtered(lambda l: not l.reconciled)
        return super(AccountMoveLine, self).reconcile(writeoff_acc_id, writeoff_journal_id)
    
