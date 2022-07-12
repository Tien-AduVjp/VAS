from odoo import api, SUPERUSER_ID

def _update_employee_advance_state(env):
    env.cr.execute("""
        UPDATE employee_advance
        SET state = 'validate'
        WHERE state = 'spent'
    """)

def _link_payment_move_to_expense_sheet(env):
    env.cr.execute("""
        WITH tmpl AS (
            SELECT am.id as move_id, ap.expense_sheet_id as expense_sheet_id
            FROM account_move am
            JOIN account_payment ap ON am.payment_id = ap.id
            WHERE ap.expense_sheet_id IS NOT NULL
        )

        UPDATE account_move am
        SET hr_expense_sheet_id = tmpl.expense_sheet_id
        FROM tmpl
        WHERE am.id = tmpl.move_id
    """)

def _prepare_column(env):
    env.cr.execute("""
        ALTER TABLE account_payment
        ADD COLUMN IF NOT EXISTS legacy_14_0_old_move_id integer;

        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS legacy_14_0_old_payment_id integer
    """)

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_employee_advance_state(env)
    to_hr_expense_module = env['ir.module.module'].search([
        ('name', '=', 'to_hr_expense'),
        ('state', 'in', ('installed','to upgrade'))
    ])
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='account_payment' and column_name='expense_sheet_id'
    """)
    col_expense_sheet_id = cr.fetchone()
    if to_hr_expense_module and col_expense_sheet_id:
        _link_payment_move_to_expense_sheet(env)
    _prepare_column(env)
