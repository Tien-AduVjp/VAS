from odoo import api, SUPERUSER_ID


def _fill_accounts(env):
    payslip_lines = env['hr.payslip.line'].sudo().search([
        ('salary_rule_id.account_debit', '!=', False),
        ('salary_rule_id.account_debit.internal_group', '=', 'expense')
        ], order='date_to DESC')

    seen_contracts = env['hr.contract']
    seen_departments = env['hr.department']
    for line in payslip_lines:
        rule = line.salary_rule_id
        update_vals = {
            'account_expense_id': rule.account_debit.id,
            }
        # update department with salary rule's debit account as expense
        if line.contract_id.department_id not in seen_departments:
            line.contract_id.department_id.write(update_vals)
            seen_departments |= line.contract_id.department_id

        # update contract
        if rule.analytic_account_id:
            update_vals['analytic_account_id'] = rule.analytic_account_id.id
        if rule.analytic_tag_ids:
            update_vals['analytic_tag_ids'] = [(6, 0, rule.analytic_tag_ids.ids)]

        if line.contract_id not in seen_contracts:
            line.contract_id.write(update_vals)
            seen_contracts |= line.contract_id


def _rule_accounting_enable(env):
    rules = env['hr.salary.rule'].sudo().search([
        ('generate_account_move_line', '=', False),
        '|', ('account_debit', '!=', False), ('account_credit', '!=', False)])
    if rules:
        rules.write({
            'generate_account_move_line': True,
            'account_debit': False,
            'analytic_account_id': False,
            'analytic_tag_ids': [(6, 0, [])]
            })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fill_accounts(env)
    _rule_accounting_enable(env)

