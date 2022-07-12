from odoo import models, api


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def _get_bank_currency_ex_rate_supported_models(self):
        res = super(ResCurrency, self)._get_bank_currency_ex_rate_supported_models()
        res.update({
            'custom.declaration.export': '_get_currency_context',
            'custom.declaration.import': '_get_currency_context',
            })
        return res
