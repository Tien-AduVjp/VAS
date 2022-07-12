from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    crossovered_budget_line_ids = fields.One2many('crossovered.budget.line', 'analytic_account_id', 'Budget Lines')
