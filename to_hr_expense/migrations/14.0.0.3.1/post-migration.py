from odoo import api, SUPERUSER_ID

def _fix_exclude_from_invoice_tab(env):
    """
    Wrong exclude_from_invoice_tab for expense move at end migration 14.0.0.3
    """
    lines = env['account.move.line'].search([('expense_id', '!=', False)])
    if lines:
        env.cr.execute("""
            WITH tmpl AS (
                SELECT
                    aml.id as move_line_id,
                    (CASE
                        WHEN aa.internal_type in ('receivable','payable') THEN true
                        WHEN aml.tax_line_id is not NULL THEN true
                        ELSE false
                    END) as exclude_from_invoice_tab
                FROM account_move_line aml
                JOIN account_account aa ON aml.account_id = aa.id
                WHERE aml.id in %s
            )

            UPDATE account_move_line aml
            SET exclude_from_invoice_tab = tmpl.exclude_from_invoice_tab
            FROM tmpl
            WHERE aml.id = tmpl.move_line_id
        """, (tuple(lines.ids),))

        lines.filtered_domain([
            ('move_id.state', '=', 'posted')
        ]).move_id._compute_amount()

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_exclude_from_invoice_tab(env)
