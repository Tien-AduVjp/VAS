from odoo import models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_company_currency_transaction_wallet_amount(self):
        self.ensure_one()
        """
        Get the total transaction amount and wallet amount in the payment's company currency
        from the corresponding transaction.

        :return: tx_amount, tx_wallet_amount
        """
        if self.payment_transaction_id:
            return self.payment_transaction_id._get_company_currency_wallet_amount(self.company_id)
        else:
            return 0, self.currency_id._convert(self.wallet_amount, self.company_id.currency_id, self.company_id, self.date)

    def _prepare_currency_conversion_diff_move_lines_data(self, journal, diff_amount):
        lines = super(AccountPayment, self)._prepare_currency_conversion_diff_move_lines_data(journal, diff_amount)
        if self.wallet and self.payment_transaction_id:
            # find the total wallet amount and transaction amount in the company currency
            tx_amount, tx_wallet_amount = self._get_company_currency_transaction_wallet_amount()
            wallet_amount = diff_amount * (tx_wallet_amount / tx_amount) if tx_amount and tx_wallet_amount else 0.0
            wallet_amount_currency = self.company_id.currency_id._convert(wallet_amount, self.currency_id, self.company_id, self.date)
            lines[0].update({
                'wallet_id': self.wallet_id and self.wallet_id.id or False,
                'wallet': True if wallet_amount else False,
                'wallet_amount': wallet_amount,
                'wallet_amount_currency': wallet_amount_currency,
            })
            lines[1].update({
                'wallet_id': self.wallet_id and self.wallet_id.id or False,
                'wallet': True if wallet_amount else False,
                'wallet_amount': wallet_amount * -1,
                'wallet_amount_currency': wallet_amount_currency * -1,
            })
        return lines

    def _get_wallet_move_line_vals(self):
        """
        This override ensures the wallet_amount of the receivable payment move line will NOT be greater
        than the transaction's wallet_amount
        """
        self.ensure_one()
        vals = super(AccountPayment, self)._get_wallet_move_line_vals()
        if self.wallet and self.payment_transaction_id:
            # find the total wallet amount and transaction amount in the company currency
            tx_amount, tx_wallet_amount = self._get_company_currency_transaction_wallet_amount()
            payment_different = self._get_payment_transaction_diff()
            wallet_amount_currency_diff = payment_different * (tx_wallet_amount / tx_amount) if tx_amount and tx_wallet_amount else 0.0
            tx_wallet_amount -= wallet_amount_currency_diff
            vals['wallet_amount'] = tx_wallet_amount
        return vals
