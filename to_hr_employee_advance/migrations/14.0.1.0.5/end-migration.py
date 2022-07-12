from odoo import api, SUPERUSER_ID

def _reconcile_payment_with_employee_advance_reconcile(env):
    payments = env['account.payment'].search([
        ('employee_advance_reconcile_id', '!=', False),
        ('state', '=', 'posted')
    ])
    if payments:
        payments._reconcile_employee_advance_reconcile()

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _reconcile_payment_with_employee_advance_reconcile(env)
