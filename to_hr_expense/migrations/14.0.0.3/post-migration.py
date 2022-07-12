from odoo import api, SUPERUSER_ID

def _update_expense_move(env):
    """
    Update account move set account to Trade payable and partner to Vendor for expense sheet has invoice
    """
    env.cr.execute("""
        WITH tmpl AS (
            SELECT
                aml.id as move_line_id,
                am.partner_id as partner_id,
                CASE
                    WHEN aa.internal_type != 'payable' THEN aml.account_id
                    WHEN aa.internal_type = 'payable' THEN
                        (SELECT CAST(SPLIT_PART(ip.value_reference, ',', 2) AS int)
                        FROM ir_property ip
                        WHERE ip.company_id = am.company_id
                        AND ip.name = 'property_account_payable_id'
                        AND
                            CASE
                                WHEN EXISTS
                                    (SELECT res_id,id FROM ir_property ip1
                                     WHERE res_id = CONCAT('res.partner,', am.partner_id)
                                     AND ip1.name = 'property_account_payable_id'
                                     AND ip1.company_id = am.company_id)
                                THEN ip.res_id = CONCAT('res.partner,', am.partner_id)
                                ELSE res_id IS NULL
                            END
                        LIMIT 1)
                END AS account_id,
                aa.internal_type
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN hr_expense_sheet exs ON am.hr_expense_sheet_id = exs.id
            JOIN account_account aa ON aml.account_id = aa.id
            WHERE am.move_type = 'in_invoice'
        )

        UPDATE account_move_line aml
        SET
            partner_id = tmpl.partner_id,
            account_id = tmpl.account_id
        FROM tmpl
        WHERE aml.id = tmpl.move_line_id

    """)

def _update_expense_payment_move(env):
    """
    Update account move set account to Employee payable and partner to Employee for payments
    """
    env.cr.execute("""
        WITH tmpl AS (
            SELECT
                aml.id as move_line_id,
                am.id as move_id,
                emp.address_home_id as partner_id,
                CASE
                    WHEN aa.internal_type != 'payable' THEN aml.account_id
                    WHEN aa.internal_type = 'payable' THEN
                        (SELECT CAST(SPLIT_PART(ip.value_reference, ',', 2) AS int)
                        FROM ir_property ip
                        WHERE ip.company_id = am.company_id
                        AND ip.name = 'property_account_payable_id'
                        AND
                            CASE
                                WHEN EXISTS
                                    (SELECT res_id FROM ir_property ip1
                                     WHERE res_id = CONCAT('res.partner,', emp.address_home_id)
                                     AND ip1.name = 'property_account_payable_id'
                                     AND ip1.company_id = am.company_id)
                                THEN ip.res_id = CONCAT('res.partner,', emp.address_home_id)
                                ELSE res_id IS NULL
                            END
                        LIMIT 1)
                END AS account_id,
                aa.internal_type
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            JOIN account_payment ap on am.payment_id = ap.id
            JOIN hr_expense ex on aml.expense_id = ex.id
            JOIN hr_employee emp on ex.employee_id = emp.id
            JOIN account_account aa ON aml.account_id = aa.id
            WHERE ex.payment_mode = 'own_account'
        ), update_move_line AS (
            UPDATE account_move_line aml
            SET
                partner_id = tmpl.partner_id,
                account_id = tmpl.account_id
            FROM tmpl
            WHERE aml.id = tmpl.move_line_id
        ), update_move AS (
            UPDATE account_move am
            SET partner_id = tmpl.partner_id
            FROM tmpl
            WHERE am.id = tmpl.move_id
        )

        UPDATE account_payment ap
        SET destination_account_id = tmpl.account_id
        FROM tmpl
        WHERE ap.move_id = tmpl.move_id

    """)

def _create_expense_journal(env):
    companies = env['res.company']
    companies._generate_expense_account_journals()

def _update_expense_journal_to_expense_sheet(env):
    expense_sheets = env['hr.expense.sheet'].search([])
    for sheet in expense_sheets:
        expense_journal = env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('code', '=', 'EXJ'),
            ('company_id', '=', sheet.company_id.id)], limit=1)
        vendor_bill_journal = env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', sheet.company_id.id)], limit=1)
        vals = {}
        if expense_journal:
            vals['journal_id'] = expense_journal.id
        if vendor_bill_journal:
            vals['vendor_bill_journal_id'] = vendor_bill_journal.id
        if vals:
            sheet.write(vals)

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _create_expense_journal(env)
    _update_expense_journal_to_expense_sheet(env)
    _update_expense_move(env)
    _update_expense_payment_move(env)
