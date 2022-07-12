from odoo import models, fields, api
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    amount_paid_by_voucher = fields.Monetary(string='Amount Paid by Voucher', readonly=True)

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        for r in self:
            super(AccountInvoice, r)._compute_amount()
            if r.move_type == 'entry' or r.is_outbound():
                sign = 1
            else:
                sign = -1
            if not (r.currency_id or r.env.company.currency_id).is_zero(r.amount_paid_by_voucher):
                r.amount_total -= -sign * r.amount_paid_by_voucher
                r.amount_total_signed -= abs(r.amount_paid_by_voucher) if r.move_type == 'entry' else r.amount_paid_by_voucher
