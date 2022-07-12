from odoo import fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ['account.move', 'to.vietnamese.number2words']

    total_in_word = fields.Char(string='In words', compute='_compute_total_in_word')
    in_out_payment = fields.Selection(string='Payment In/Out', selection=[('in', 'In'), ('out', 'Out')], compute='_compute_in_out_payment',
        help="This is technical field, use to specify this move is payment in or payment out.")

    def _compute_total_in_word(self):
        for r in self:
            r.total_in_word = r.num2words(abs(r.amount_total_signed), precision_rounding=r.currency_id.rounding)

    def _compute_in_out_payment(self):
        for rec in self:
            rec.in_out_payment = False
            if rec.journal_id.type in ('bank', 'cash'):
                if sum(rec.line_ids.filtered_domain([('account_id.internal_type', '=', 'liquidity')]).mapped('debit')) > 0:
                    rec.in_out_payment = 'in'
                else:
                    rec.in_out_payment = 'out'
        
