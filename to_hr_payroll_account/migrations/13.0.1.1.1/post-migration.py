from odoo import api, SUPERUSER_ID


def _remove_wrong_payslip_analytic_lines(env):
    salary_move_lines = env['account.move.line'].search([('salary_rule_id', '!=', False)])
    salary_move_lines_to_fix = salary_move_lines.filtered(lambda l: l.analytic_line_ids and l.account_id == l.salary_rule_id.account_credit)

    if salary_move_lines_to_fix:
        salary_move_lines_to_fix.write({'analytic_account_id': False})

    analytic_lines = salary_move_lines_to_fix.mapped('analytic_line_ids')
    if analytic_lines:
        analytic_lines.unlink()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _remove_wrong_payslip_analytic_lines(env)

