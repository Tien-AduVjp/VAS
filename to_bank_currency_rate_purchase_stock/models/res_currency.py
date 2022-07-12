from odoo import models


class ResCurrency(models.Model):
    _inherit = "res.currency"
    
    def _get_bank_currency_ex_rate_supported_models(self):
        res = super(ResCurrency, self)._get_bank_currency_ex_rate_supported_models()
        res.update({
            'stock.move': '_get_currency_context',
            'purchase.order.line': '_get_currency_context',
            })
        return res
