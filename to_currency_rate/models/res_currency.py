from odoo import models, fields
from odoo.tools import float_is_zero


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    inverse_rate = fields.Float(string='Inverse Rate', compute='_compute_inverse_rate', digits=0)

    def _compute_inverse_rate(self):
        rates_data = self.read(['rate'])
        mapped_data = dict([(currency['id'], currency['rate']) for currency in rates_data])
        for r in self:
            rate = mapped_data.get(r.id, 1.0)
            if not float_is_zero(rate, precision_digits=16):
                r.inverse_rate = 1.0 / rate
            else:
                r.inverse_rate = 1.0
