from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_currency_context(self):
        exchange_type = False
        # Send money : take bank sell rate (company buy foreign currency)
        if self.payment_type == 'outbound':
            exchange_type = 'sell_rate'
        # Receive money : take bank buy rate (company sell foreign currency)
        elif self.payment_type == 'inbound':
            exchange_type = 'buy_rate'
        # internal transfers
        else:
            journal_curency_id = self.journal_id.currency_id or self.journal_id.company_id.currency_id
            destination_journal_curency_id = self.destination_journal_id.currency_id or self.destination_journal_id.company_id.currency_id
            if journal_curency_id == self.company_id.currency_id and destination_journal_curency_id != self.company_id.currency_id:
                exchange_type = 'sell_rate'
            if journal_curency_id != self.company_id.currency_id and destination_journal_curency_id == self.company_id.currency_id:
                exchange_type = 'buy_rate'

        exchange_rate_bank = self.journal_id.bank_id or self.company_id.main_currency_bank_id
        if not exchange_rate_bank or not exchange_type:
            exchange_type = None
        return exchange_rate_bank, exchange_type
