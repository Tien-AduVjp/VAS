from odoo import fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    account_move_id = fields.Many2one('account.move', string='Journal Entry', related='sheet_id.account_move_id', store=True, groups="account.group_account_invoice")
