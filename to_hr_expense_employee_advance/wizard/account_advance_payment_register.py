from odoo import models, fields


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.advance.payment.register'

    expense_sheet_id = fields.Many2one('hr.expense.sheet', string='Expense Report')

    def _create_advance_move(self):
        move = super(AccountPaymentRegister, self)._create_advance_move()
        if self.expense_sheet_id:
            move.write({'hr_expense_sheet_id': self.expense_sheet_id.id})
        return move
