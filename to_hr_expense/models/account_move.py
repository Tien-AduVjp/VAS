import inspect
from odoo import fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    hr_expense_sheet_id = fields.Many2one('hr.expense.sheet', string='HR Expense')

    def button_draft(self):
        for l in self.line_ids:
            if l.expense_id.state == 'done':
                l.expense_id.refuse_expense(reason=_("Journal Entry was set to draft"))
        return super().button_draft()

    # TODO: replace this method to _payment_state_matters in 15.0
    # Ref. https://github.com/odoo/odoo/pull/65528
    def is_invoice(self, include_receipts=False):
        stact = inspect.stack()
        for i, stack in enumerate(stact):
            if stack.function == '_compute_amount':
                if self.line_ids.expense_id:
                    return True

        return super(AccountMove, self).is_invoice(include_receipts=include_receipts)

    def _post(self, soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        for r in self:
            if r.hr_expense_sheet_id:
                domain = [
                    ('account_internal_type', 'in', ('receivable', 'payable')),
                    ('reconciled', '=', False),
                    ('move_id.move_type', '=', 'entry')
                ]
                move_lines = r.line_ids.filtered_domain(domain)
                to_reconcile = r.hr_expense_sheet_id.move_ids.line_ids.filtered_domain(domain + [
                    ('id', 'not in', move_lines.ids),
                    ('move_id.state', '=', 'posted'),
                ])
                for account in move_lines.account_id:
                    (move_lines + to_reconcile)\
                        .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                        .reconcile()

        return res
