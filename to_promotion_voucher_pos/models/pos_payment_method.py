from odoo import api, fields, models


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    voucher_payment = fields.Boolean(string='Voucher Payment method', compute='_compute_voucher_payment', store=True)

    @api.depends('is_cash_count', 'cash_journal_id')
    def _compute_voucher_payment(self):
        for r in self:
            r.voucher_payment = r.is_cash_count and r.cash_journal_id.voucher_payment or False
