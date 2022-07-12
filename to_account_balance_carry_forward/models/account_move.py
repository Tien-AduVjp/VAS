from odoo import models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def button_draft(self):
        balances_carry_forward = self.line_ids.mapped('forward_aml_id.balance_carry_forward_id').filtered(lambda b: b.state not in ('draft','cancelled'))
        if balances_carry_forward:
            raise UserError(_('You may need to set to draft the balances carry forward %s first.') % ','.join(balances_carry_forward.mapped('name')))
        return super(AccountMove, self).button_draft()
