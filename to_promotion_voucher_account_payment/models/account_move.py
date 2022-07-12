from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        if vals.get('state', False) in ('draft', 'cancel'):
            for r in self:
                if r.payment_id and r.payment_id.sudo().voucher_id:
                    r.payment_id.voucher_id.unspend(r.payment_id.amount)
        return res
