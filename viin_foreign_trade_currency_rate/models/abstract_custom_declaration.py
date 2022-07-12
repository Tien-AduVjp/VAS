from odoo import models

class AbstractCustomDeclaration(models.AbstractModel):
    _inherit = 'abstract.custom.declaration'

    def _get_currency_context(self):
        exchange_type = False
        exchange_rate_bank = self.company_id.main_currency_bank_id
        if exchange_rate_bank:
            exchange_type = 'transfer_rate'
        return exchange_rate_bank, exchange_type
