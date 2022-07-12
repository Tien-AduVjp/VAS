from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_paid(self):
        res = super(AccountMove, self).action_invoice_paid()
        self.mapped('invoice_line_ids.loan_borrow_interest_line_id').filtered(lambda l: l.fully_invoiced).action_paid()
        self.mapped('invoice_line_ids.loan_lend_interest_line_id').filtered(lambda l: l.fully_invoiced).action_paid()
        return res

    def _write(self, vals):
        res = super(AccountMove, self)._write(vals)
        payment_state = vals.get('payment_state', False)
        if payment_state and payment_state != 'paid':
            self.mapped('invoice_line_ids.loan_borrow_interest_line_id').filtered(
                lambda l: l.state == 'paid').action_re_confirm()
            self.mapped('invoice_line_ids.loan_lend_interest_line_id').filtered(
                lambda l: l.state == 'paid').action_re_confirm()
        return res

    def unlink(self):
        loan_borrow_interest_line_ids = self.mapped('invoice_line_ids.loan_borrow_interest_line_id')
        loan_lend_interest_line_ids = self.mapped('invoice_line_ids.loan_lend_interest_line_id')
        res = super(AccountMove, self).unlink()
        loan_borrow_interest_line_ids._compute_invoiced_amount()
        loan_lend_interest_line_ids._compute_invoiced_amount()
        return res
