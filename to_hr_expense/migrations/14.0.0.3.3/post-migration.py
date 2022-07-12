from odoo import api, SUPERUSER_ID

def _re_compute_expense_sheet_amount_residual(env):
    sheets = env['hr.expense.sheet'].search([])
    sheets._compute_amount_residual()

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _re_compute_expense_sheet_amount_residual(env)
