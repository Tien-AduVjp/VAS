from odoo import models
from odoo.osv import expression


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def reconcile(self):
        """
        This override is to add currency conversion diff. move lines of the related online payment to Self
        to ensure that all the related move lines will be taken into account for reconcilating with invoices.
        """
        if not self.env.context.get('ignore_add_currency_conversion_diff', False):
            related_online_payments = self.mapped('payment_id').filtered(
                lambda p: p.payment_transaction_id and p.payment_transaction_id.sudo().currency_id != p.currency_id
                )
            related_unreconciled_payment_lines = self.env['account.move.line'].search(related_online_payments._get_unreconciled_payment_move_lines_domain())
            if related_unreconciled_payment_lines:
                self |= related_unreconciled_payment_lines
            self = self.filtered(lambda l: not l.reconciled)
        return super(AccountMoveLine, self).reconcile()

    def open_reconcile_view(self):
        """
        This override is to add currency conversion diff. move of the related online payment
        to reconcile_view to avoid confusion.
        """
        res = super(AccountMoveLine, self).open_reconcile_view()

        line_ids = self._reconciled_lines()
        reconcile_ids = self.env['account.move.line'].browse(line_ids).full_reconcile_id.ids

        misc_line_ids = self.env['account.move.line'].search([
            ('id', 'not in', line_ids),
            ('full_reconcile_id', 'in', reconcile_ids)
            ]).ids

        res['domain'] = expression.OR([res['domain'], [('id', 'in', misc_line_ids)]])
        return res
