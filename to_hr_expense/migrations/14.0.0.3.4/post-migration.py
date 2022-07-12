from odoo import api, SUPERUSER_ID

def _re_compute_expense_sheet_is_paid(env):
    sheets = env['hr.expense.sheet'].search([])
    sheets._compute_is_paid()

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _re_compute_expense_sheet_is_paid(env)
