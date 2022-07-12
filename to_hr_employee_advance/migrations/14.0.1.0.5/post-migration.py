from odoo import api, SUPERUSER_ID

def _update_advance_journal_type(env):
    advance_journals = env['account.journal'].with_context(active_test=False).search([('is_advance_journal', '=', True)])
    advance_journals.write({'type': 'general'})

def _remove_link_between_advance_payment_and_move(env):
    # find payments of invoice paid by employee advance journal
    advance_payments = env['account.payment'].search([
        ('journal_id.is_advance_journal', '=', True)
    ])
    for payment in advance_payments:
        # we need to remove link between advance payment and move,
        # but we cannot cancel payment and create new. So we should copy
        # current move to new move and link the payment to new move and
        # cancel it
        old_move = payment.move_id
        new_move = payment.move_id.copy()
        env.cr.execute("""
            UPDATE account_payment
            SET
                move_id = {0},
                is_reconciled = false,
                is_matched = false,
                legacy_14_0_old_move_id = {1}
            WHERE id = {2};

            UPDATE account_move
            SET
                payment_id = NULL,
                legacy_14_0_old_payment_id = {2}
            WHERE id = {1};

            UPDATE account_move_line
            SET payment_id = NULL
            WHERE move_id = {1};
        """.format(new_move.id, old_move.id, payment.id))
        new_move.button_cancel()
        partner = False
        if payment.reconciled_bill_ids:
            partner = payment.reconciled_bill_ids[0].partner_id
            for old_move_line in old_move.line_ids:
                if old_move_line.account_id != payment.employee_id.property_advance_account_id:
                    env.cr.execute("""
                        UPDATE account_move_line
                        SET account_id = %s, partner_id = %s
                        WHERE id = %s
                    """, (partner.property_account_payable_id.id, partner.id, old_move_line.id))

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_advance_journal_type(env)
    _remove_link_between_advance_payment_and_move(env)
