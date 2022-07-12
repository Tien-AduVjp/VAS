from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _get_currency_context(self):
        self.ensure_one()
        return self.order_id.company_id.main_currency_bank_id, 'sell_rate'
