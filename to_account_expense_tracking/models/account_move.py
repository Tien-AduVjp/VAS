from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    expense_ids = fields.One2many('hr.expense', 'account_move_id', string='HR Expenses')
    expense_sheet_ids = fields.One2many('hr.expense.sheet', 'account_move_id', string='HR Expense Sheets')
    expense_sheet_id = fields.Many2one('hr.expense.sheet', string='HR Expense Sheet', compute='compute_expense_sheet_id', store=True)

    
    @api.depends('expense_sheet_ids')
    def compute_expense_sheet_id(self):
        for r in self:
            r.expense_sheet_id = r.expense_sheet_ids and r.expense_sheet_ids[0] or False

