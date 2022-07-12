from odoo import models, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def _get_currency_context(self):
        exchange_type = False
        if self.is_internal_transfer:
            if self.payment_type == 'outbound':
                exchange_type = 'buy_rate'
            elif self.payment_type == 'inbound':
                exchange_type = 'sell_rate'
        else:
            # Send money : take bank sell rate (company buy foreign currency)
            if self.payment_type == 'outbound':
                exchange_type = 'sell_rate'
            # Receive money : take bank buy rate (company sell foreign currency)
            elif self.payment_type == 'inbound':
                exchange_type = 'buy_rate'

        exchange_rate_bank = self.journal_id.bank_id or self.company_id.main_currency_bank_id
        if not exchange_rate_bank or not exchange_type:
            exchange_type = None
        return exchange_rate_bank, exchange_type

    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        res = super(AccountPayment, self).copy(default=default)
        res.move_id.with_context(check_move_validity=False)._onchange_currency()
        return res
