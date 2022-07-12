from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"
    
    def _get_currency_context(self):
        self.ensure_one()
        exchange_type = None
        exchange_rate_bank = None
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            exchange_type = 'sell_rate'
            exchange_rate_bank = self.company_id.main_currency_bank_id
        return exchange_rate_bank, exchange_type
