import time
import calendar

from odoo import models, fields, _


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    wallet_id = fields.Many2one('wallet', string='Wallet', readonly=True)
    wallet_amount = fields.Monetary(string='Wallet Amount', readonly=True)

    def _get_wallet_vals(self):
        """
        Hooking method for modifying the current wallet before submitted to acquirer.
        Currently, this method will check any invoice here that has a wallet line, we will put the wallet residual amount here
        """
        vals = {}
        # if online payment is made for in invoice
        invoice_receivable_wallet_lines = self.invoice_ids._get_receivable_wallet_lines()
        if invoice_receivable_wallet_lines:
            wallet_amount = sum(invoice_receivable_wallet_lines.mapped('wallet_amount_residual'))
            wallet_amount_currency = sum(invoice_receivable_wallet_lines.mapped('wallet_amount_residual_currency'))
            if wallet_amount:
                currency_diff = self.currency_id == invoice_receivable_wallet_lines[0].company_currency_id
                vals.update({
                    'wallet': True,
                    'wallet_amount': wallet_amount if currency_diff else wallet_amount_currency,
                    'wallet_amount_currency': wallet_amount_currency if currency_diff else 0.0
                    })
        return vals

    def render_wallet_payment_form(self):
        self.ensure_one()
        if self.wallet_id:
            return self.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=_('Pay Now')).sudo().render(
                self.reference,
                self.amount,
                self.currency_id.id,
                partner_id=self.wallet_id.partner_id.id
            )
        return False

    def _compute_reference_prefix(self, values):
        wallet_id = values.get('wallet_id')
        if wallet_id:
            return 'WALLET-%s-%s' % (wallet_id, calendar.timegm(time.gmtime()))
        return super(PaymentTransaction, self)._compute_reference_prefix(values)

    def _create_payment(self, add_payment_vals={}):
        self.ensure_one()
        if self._is_wallet_transaction():
            add_payment_vals.update(self._prepare_wallet_payment_vals())
        return super(PaymentTransaction, self)._create_payment(add_payment_vals)

    def _prepare_wallet_payment_vals(self):
        return {
            'wallet': True,
            'wallet_amount': self.wallet_amount
        }

    def _is_wallet_transaction(self):
        self.ensure_one()
        invoice_receivable_wallet_lines = self.invoice_ids._get_receivable_wallet_lines()
        wallet_amount_residual = sum(invoice_receivable_wallet_lines.mapped('wallet_amount_residual'))
        if self.wallet_id or wallet_amount_residual:
            return True
        return False
