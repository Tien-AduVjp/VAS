from odoo import models
from odoo.tools import float_compare


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"
    
    def _get_currency_context(self):
        exchange_type = None
        currency = self.currency_id or self.statement_id.currency_id or self.journal_currency_id
        if currency:
            # if amount is positive, it means we receive money, then the bank's buy rate
            # will be applied (we may sell foreign currency to the bank)
            if float_compare(self.amount, 0.0, precision_rounding=currency.rounding) == 1:
                exchange_type = 'buy_rate'
            # apply the rate of bank of the corresponding journal if any
        exchange_rate_bank = self.statement_id.journal_id.bank_id or self.company_id.main_currency_bank_id
        return exchange_rate_bank, exchange_type
