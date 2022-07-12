from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_currency_context(self):
        self.ensure_one()
        # Customer Invoice, Sales Receipt, Customer Credit Note
        if self.type in self.get_sale_types(include_receipts=True):
            exchange_type = 'buy_rate'
        # Vendor Bill, Vendor Credit Note, Purchase Receipt
        elif self.type in self.get_purchase_types(include_receipts=True):
            exchange_type = 'sell_rate'
        # Journal Entry
        else:
            exchange_type = self.line_ids[:1]._get_currency_exchange_rate_type()
            
        if any(line.account_id.internal_type == 'liquidity' for line in self.line_ids):
            exchange_rate_bank = self.journal_id.bank_id or self.company_id.main_currency_bank_id
        else:
            exchange_rate_bank = self.company_id.main_currency_bank_id

        return exchange_rate_bank, exchange_type
