from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_currency_exchange_rate_type(self):
        if not self:
            return 'sell_rate'

        self.ensure_one()
        if self.account_id.internal_type == 'liquidity':
            if self.amount_currency > 0:
                exchange_type = 'buy_rate'
            else:
                exchange_type = 'sell_rate'
        elif self.account_id.internal_group in ('asset', 'income'):
            exchange_type = 'buy_rate'
        else:
            exchange_type = 'sell_rate'
        return exchange_type

    def _get_currency_context(self):
        moves = self.mapped('move_id')
        moves.ensure_one()
        return moves._get_currency_context()
