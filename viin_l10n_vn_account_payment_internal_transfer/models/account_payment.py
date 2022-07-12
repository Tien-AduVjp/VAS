from odoo import models

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _prepare_payment_moves(self):
        res = super(AccountPayment, self)._prepare_payment_moves()
        remove_move_vals_list = []
        for payment in self:
            if payment.payment_type == 'transfer' and not payment.company_id.use_intermediary_account:
                for move_vals in res:
                    if move_vals['line_ids'][0][2]['payment_id'] == payment.id and move_vals not in remove_move_vals_list:
                        remove_index = res.index(move_vals) + 1
                        move_vals['line_ids'][0] = res[remove_index]['line_ids'][1]
                        remove_move_vals_list.append(res[remove_index])
        if remove_move_vals_list:
            for mv in remove_move_vals_list:
                res.remove(mv)
        return res
