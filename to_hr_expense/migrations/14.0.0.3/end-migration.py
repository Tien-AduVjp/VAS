from odoo import api, SUPERUSER_ID

def _update_payable_account_for_expense_move(env):
    """
    Some old data has payable account on employee is Trade payable
    So we need update expense moves has not invoice to Employee payable
    """
    env.cr.execute("""
        WITH tmpl AS (
            SELECT
                aml.id as move_line_id,
                ex.id as expense_id,
                em.address_home_id as partner_id,
                aml.partner_id as move_line_partner_id,
                (
                    SELECT CAST(SPLIT_PART(ip.value_reference, ',', 2) AS int)
                    FROM ir_property ip
                    WHERE ip.company_id = aml.company_id
                    AND ip.name = 'property_account_payable_id'
                    AND
                        CASE
                            WHEN EXISTS
                                (SELECT res_id,id FROM ir_property ip1
                                 WHERE res_id = CONCAT('res.partner,', em.address_home_id)
                                 AND ip1.name = 'property_account_payable_id'
                                 AND ip1.company_id = aml.company_id)
                            THEN ip.res_id = CONCAT('res.partner,', em.address_home_id)
                            ELSE res_id IS NULL
                        END
                    LIMIT 1
                ) as account_id,
                aml.account_id as aml_account_id
            FROM account_move_line aml
            JOIN account_account aa ON aml.account_id = aa.id
            JOIN hr_expense ex ON aml.expense_id = ex.id
            JOIN hr_employee em ON ex.employee_id = em.id
            JOIN res_partner rp ON em.address_home_id = rp.id
            WHERE ex.to_invoice = false
            AND aa.internal_type = 'payable'
        )

        UPDATE account_move_line aml
        SET account_id = tmpl.account_id, partner_id = tmpl.partner_id
        FROM tmpl
        WHERE aml.id = tmpl.move_line_id
    """)

def _update_exclude_from_invoice_tab(env):
    lines = env['account.move.line'].search([('expense_id', '!=', False)])
    if lines:
        env.cr.execute("""
            WITH tmpl AS (
                SELECT
                    aml.id as move_line_id,
                    (CASE WHEN aa.internal_type in ('receivable','payable') THEN false
                    ELSE true
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

def _generate_payable_transfer_move(env):
    expense_sheets = env['hr.expense.sheet'].search([
        ('state', 'in', ('post', 'done')),
        ('has_invoice', '=', True)
    ])

    for sheet in expense_sheets:
        to_unreconcile_lines = sheet.move_ids.filtered_domain([('move_type', '=', 'in_invoice')]) \
            .line_ids.filtered_domain([
                ('account_internal_type', '=', 'payable'),
                ('reconciled', '=', True),
            ])
        to_unreconcile_lines.remove_move_reconcile()

        sheet.generate_payable_transfer_move()

        to_reconcile_lines = sheet.move_ids.filtered_domain([('move_type', '=', 'entry')]) \
            .line_ids.filtered_domain([
                ('account_internal_type', '=', 'payable'),
                ('reconciled', '=', False),
                ('move_id.state', '=', 'posted'),
            ])
        to_reconcile_lines.reconcile()

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_payable_account_for_expense_move(env)
    _generate_payable_transfer_move(env)
    _update_exclude_from_invoice_tab(env)
