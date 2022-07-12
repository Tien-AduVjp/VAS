from odoo import api, SUPERUSER_ID

def _prepare_column(env):
    env.cr.execute("""
        ALTER TABLE account_payment
        ADD COLUMN IF NOT EXISTS legacy_14_0_old_expense_sheet_id integer;

        ALTER TABLE account_move
        ADD COLUMN IF NOT EXISTS legacy_14_0_old_hr_expense_sheet_id integer
    """)

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _prepare_column(env)
