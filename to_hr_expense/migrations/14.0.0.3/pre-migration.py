from odoo import api, SUPERUSER_ID

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

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _link_payment_move_to_expense_sheet(env)
