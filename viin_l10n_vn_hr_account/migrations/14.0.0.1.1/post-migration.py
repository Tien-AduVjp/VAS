from odoo import api, SUPERUSER_ID

def _update_employee_payable_account(env):
    employees = env['hr.employee'].with_context(active_test=False).search([])
    employees._apply_vietnam_empoloyee_payable_account()

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_employee_payable_account(env)
