from odoo import models, fields
from odoo.osv import expression


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    expense_sheet_id = fields.Many2one('hr.expense.sheet', string='Expense Report')

    def _seek_for_lines(self):
        """
            By default, move lines with accounts which are not in liquidity, receivable, payable types should be taken to
            writeoff_lines. So we should move these move lines which have accounts in expense_line_ids to counterpart_lines.
        """
        self.ensure_one()
        liquidity_lines, counterpart_lines, writeoff_lines = super(AccountPayment, self)._seek_for_lines()
        if self.expense_sheet_id:
            counterpart_missing_lines = writeoff_lines.filtered(lambda l: l.account_id.id in self.expense_sheet_id.expense_line_ids.account_id.ids)
            counterpart_lines |= counterpart_missing_lines
            writeoff_lines -= counterpart_missing_lines
        return liquidity_lines, counterpart_lines, writeoff_lines
