from odoo import models, fields, api
from odoo.tools import float_is_zero


class ResCurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    rate = fields.Float(group_operator="avg")
    inverse_rate = fields.Float(string='Inverse Rate', digits=0, group_operator="avg",
                                compute='_compute_inverse_rate', inverse='_set_inverse_rate', store=True)
    currency_id = fields.Many2one(index=True)

    @api.depends('rate', 'currency_id')
    def _compute_inverse_rate(self):
        for r in self:
            if not float_is_zero(r.rate, precision_digits=16):
                r.inverse_rate = 1.0 / r.rate
            else:
                r.inverse_rate = 1.0

    def _set_inverse_rate(self):
        for r in self:
            if not float_is_zero(r.inverse_rate, precision_digits=16):
                r.rate = 1.0 / r.inverse_rate
            else:
                r.rate = 1.0
