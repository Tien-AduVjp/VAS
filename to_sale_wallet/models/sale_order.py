from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_wallet_lines(self):
        return self.mapped('order_line').filtered(lambda l: l.product_id.wallet)

    def _get_sale_order_wallet_amount_for_transaction(self, transaction):
        wallet_amount = 0.0
        for so in self:
            odoo_plan_order_lines = so._get_wallet_lines()
            if so.currency_id == transaction.currency_id:
                for line in odoo_plan_order_lines:
                    wallet_amount += line.price_total
            else:
                currency_price_total = 0.0
                for line in odoo_plan_order_lines:
                    currency_price_total += line.price_total
                wallet_amount += so.currency_id._convert(
                        currency_price_total,
                        transaction.currency_id,
                        so.company_id,
                        transaction.date and transaction.date.date() or fields.Date.today()
                        )
        return wallet_amount
