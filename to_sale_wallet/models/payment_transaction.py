from odoo import models


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_wallet_vals(self):
        """
        Hooking method for modifying the current wallet amount of the transaction before submitting to the acquirer.
        """
        vals = super(PaymentTransaction, self)._get_wallet_vals()
        if not self.invoice_ids:
            wallet_amount = self.sale_order_ids._get_sale_order_wallet_amount_for_transaction(self)
            # ensure we will not modify the vals's wallet_amount if the newly calculated wallet_amount here is zero
            if not self.currency_id.is_zero(wallet_amount):
                vals['wallet_amount'] = wallet_amount
        return vals

    def _is_wallet_transaction(self):
        self.ensure_one()
        if self.sale_order_ids and self.sale_order_ids._get_sale_order_wallet_amount_for_transaction(self):
            return True
        return super(PaymentTransaction, self)._is_wallet_transaction()
