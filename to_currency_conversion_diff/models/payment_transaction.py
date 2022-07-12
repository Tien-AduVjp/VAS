from odoo import models, fields


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    converted_currency_id = fields.Many2one('res.currency', string='Converted Currency',
                                         help="The currency to be used for online payment instead of the original"
                                         " currency that is not supported by the payment acquirer.")
    converted_amount = fields.Monetary(currency_field='converted_currency_id', string='Converted Amount',
                                       help="The amount in the converted currency to be used for online payment"
                                       " instead of the amount in the original currency that is not supported by"
                                       " the payment acquirer.")
    converted_fee = fields.Monetary(currency_field='converted_currency_id', string='Converted Fee',
                                    help="The fee in the converted currency to be used for online payment"
                                       " instead of the fee in the original currency that is not supported by"
                                       " the payment acquirer.")
    
    def _prepare_converted_vals(self):
        """
        Prepare values for converted_* fields in case the transaction is made with a currency that differs from its original currency
            For example, the transaction was created for VND to pay VND invoice/order. However, the acquirer does not support VND.
            In this case, we will fill the converted values for the converted_* fields for a currency supported by Paypal
        """
        self.ensure_one()
        if self.acquirer_id.supported_currency_ids and self.currency_id not in self.acquirer_id.supported_currency_ids and self.acquirer_id.default_converted_currency_id:
            converted_currency = self.acquirer_id.default_converted_currency_id
            converted_amount = self.currency_id._convert(
                self.amount,
                self.acquirer_id.default_converted_currency_id,
                self.acquirer_id.company_id,
                self.date and self.date.date() or fields.Date.today()
                )
            vals = {
                'converted_currency_id': converted_currency.id,
                'converted_amount': converted_amount
                }
            fees_method_name = '%s_compute_fees' % self.acquirer_id.provider
            if hasattr(self.acquirer_id, fees_method_name):
                vals['converted_fee'] = getattr(self.acquirer_id, fees_method_name)(converted_amount, converted_currency.id, self.partner_country_id.id)
            return vals
        return {}
    
    def _prepare_account_payment_vals(self):
        """
        This override is to ensure the account.payment record generated in Odoo is in the currency that
            is recorded in the payment acquirer's database

        Explanation: when request payment in a currency that is not accepted by the payment acquirer,
            we convert the amount to an accepted currency.
            Without this override, the account.payment record will be encoded in the original currency
            while the corresponding recorded in the payment acquirer is in another one
        """
        vals = super(PaymentTransaction, self)._prepare_account_payment_vals()
        # self.converted_currency_id could be null if the transaction was made for the company's currency
        # In case it has a currency specified, it means the online payment was made with a currency that is other than the company's
        # In this case, we will need to convert the transaction amount from the transaction's currency to the acquirer.currency
        # to ensure the payment recorded in Odoo will be in the same currency as the one recorded by the payment acquirer
        if self.converted_currency_id and self.converted_currency_id != self.currency_id:
            amount = self.currency_id._convert(
                self.amount,
                self.converted_currency_id,
                self.acquirer_id.company_id,
                self.date and self.date.date() or fields.Date.today()
                )
            injected_data = {
                'amount': amount,
                'currency_id': self.converted_currency_id.id,
                }
            vals.update(injected_data)
        return vals
