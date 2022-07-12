from odoo import models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_currency_context(self):
        self.ensure_one()
        # Customer Invoice, Sales Receipt, Customer Credit Note
        if self.move_type in self.get_sale_types(include_receipts=True):
            exchange_type = 'buy_rate'
        # Vendor Bill, Vendor Credit Note, Purchase Receipt
        elif self.move_type in self.get_purchase_types(include_receipts=True):
            exchange_type = 'sell_rate'
        # Journal Entry
        else:
            payment = self.payment_id
            if payment:
                if payment.payment_type == 'outbound':
                    exchange_type = 'sell_rate'
                elif payment.payment_type == 'inbound':
                    exchange_type = 'buy_rate'
            else:
                exchange_type = self.line_ids[:1]._get_currency_exchange_rate_type()

        if any(line.account_id.internal_type == 'liquidity' for line in self.line_ids):
            exchange_rate_bank = self.journal_id.bank_id or self.company_id.main_currency_bank_id
        else:
            exchange_rate_bank = self.company_id.main_currency_bank_id

        return exchange_rate_bank, exchange_type

    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        res = super(AccountMove, self).copy(default=default)
        res.with_context(check_move_validity=False)._onchange_currency()
        return res
