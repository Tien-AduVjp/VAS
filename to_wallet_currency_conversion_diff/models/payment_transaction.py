from odoo import models, fields, api


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    wallet_converted_amount = fields.Monetary(currency_field='converted_currency_id', string='Wallet Converted Amount',
                                              compute='_compute_wallet_converted_amount', store=True,
                                              help="The wallet amount in the converted currency to be used for online payment"
                                              " instead of the amount in the original currency that is not supported by"
                                              " the payment acquirer.")
    
    @api.depends('converted_currency_id', 'currency_id', 'wallet_amount')
    def _compute_wallet_converted_amount(self):
        for r in self:
            wallet_converted_amount = 0.0
            if r.converted_currency_id and r.wallet_amount and r.converted_currency_id != r.currency_id:
                wallet_converted_amount = r.currency_id._convert(
                    r.wallet_amount,
                    r.converted_currency_id,
                    r.acquirer_id.company_id,
                    r.date and r.date.date() or fields.Date.today()
                    )
            r.wallet_converted_amount = wallet_converted_amount
            
    def _get_company_currency_wallet_amount(self, company, date=None):
        self.ensure_one()
        """
        Get the total transaction amount and wallet amount in the given company's currency from the transaction self
        """
        date = date or self.date and self.date.date() or fields.Date.today()
        wallet_vals = self._get_wallet_vals()
        tx_wallet_amount = wallet_vals.get('wallet_amount', self.wallet_amount)
        if self.currency_id and self.currency_id != company.currency_id:
            wallet_amount = self.currency_id._convert(tx_wallet_amount, company.currency_id, company, date)
            tx_amount = self.currency_id._convert(self.amount, company.currency_id, company, date)
        else:
            wallet_amount = tx_wallet_amount
            tx_amount = self.amount
        return tx_amount, wallet_amount

    def _prepare_account_payment_vals(self):
        self.ensure_one()
        vals = super(PaymentTransaction, self)._prepare_account_payment_vals()
        # the vals is already contain value for wallet_amount but it could be in transaction currency
        # this override ensure that the wallet_amount is converted to payment's currency in case 
        # the online payment is made in acquirer's currency instead of the origin currency (the transaction's currency)
        if self._is_wallet_transaction() and self.converted_currency_id:
            vals.update({
                'wallet_amount': self.wallet_converted_amount
                })
        return vals
