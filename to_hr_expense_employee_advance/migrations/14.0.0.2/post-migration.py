from odoo import api, SUPERUSER_ID

def _update_payment_and_move(env):
    """
    - Issue 1: Remove expense sheet from advance payment and its move because we will not generate payment for employee advance payment
    These payments and its move will be cancelled and we don't want link them to expense sheet

    - Issue 2: These payments mentioned above was cancelled but we copied its move to old move and link it to new move.
    This was done in post migration (14.0.1.0.5) of to_hr_employee_advance module
    But this module should migrate to update old move of advance payments and set its account to Employee payable and partner to Employee
    for advance payments has linked to expense sheet
    """
    expense_advance_payments = env['account.payment'].search([
        ('journal_id.is_advance_journal', '=', True),
        ('expense_sheet_id', '!=', False)
    ])
    for payment in expense_advance_payments:
        # Begin issue 1
        env.cr.execute("""
            UPDATE account_payment
            SET
                expense_sheet_id = NULL,
                legacy_14_0_old_expense_sheet_id = %s
            WHERE id = %s;

            UPDATE account_move
            SET
                hr_expense_sheet_id = NULL,
                legacy_14_0_old_hr_expense_sheet_id = %s
            WHERE id = %s
        """, (payment.expense_sheet_id.id, payment.id, payment.expense_sheet_id.id, payment.move_id.id))
        # End issue 1

        # Begin issue 2
        if payment.expense_sheet_id.payment_mode == 'own_account':
            # legacy_14_0_old_move_id copied in pre-migration (14.0.1.0.5) of to_hr_employee_advance
            env.cr.execute("""
                SELECT legacy_14_0_old_move_id from account_payment
                WHERE id = %s
            """, (payment.id,))
            move_dict = env.cr.dictfetchall()
            if move_dict:
                move = env['account.move'].browse(move_dict[0]['legacy_14_0_old_move_id'])
                if move.exists() and move.line_ids.expense_id:
                    for move_line in move.line_ids:
                        if move_line.account_id != payment.employee_id.property_advance_account_id:
                            env.cr.execute("""
                                UPDATE account_move_line aml
                                SET
                                    account_id = %s,
                                    partner_id = %s
                                WHERE aml.id = %s
                            """, (
                                    payment.employee_id.address_home_id.property_account_payable_id.id,
                                    payment.employee_id.address_home_id.id,
                                    move_line.id))
        # End issue 2

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_payment_and_move(env)
