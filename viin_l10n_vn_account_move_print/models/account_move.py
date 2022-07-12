from odoo import fields, models


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'to.vietnamese.number2words']

    total_in_word = fields.Char(string='In words', compute='_compute_total_in_word')

    def _compute_total_in_word(self):
        for r in self:
            r.total_in_word = r.num2words(abs(r.amount_total_signed), precision_rounding=r.currency_id.rounding)
