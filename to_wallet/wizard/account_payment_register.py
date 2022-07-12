from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    wallet = fields.Boolean(string='Is Wallet Deposit/Withdraw', compute='_compute_wallet', store=True, readonly=False,
                            help="Check this field if the payment is to deposit to or withdraw from wallet.")
    wallet_amount = fields.Monetary(currency_field='currency_id', compute='_compute_wallet', store=True, readonly=False)

    @api.depends('line_ids.move_id.wallet_total', 'currency_id', 'company_id', 'payment_date')
    def _compute_wallet(self):
        for r in self:
            wallet_amount = abs(sum(r.line_ids.mapped('wallet_amount_residual_currency')))
            if wallet_amount > 0:
                r.wallet = True
                if r.source_currency_id == r.currency_id:
                    r.wallet_amount = wallet_amount
                else:
                    r.wallet_amount = r.source_currency_id._convert(wallet_amount, r.currency_id, r.company_id, r.payment_date)
            else:
                r.wallet = False
                r.wallet_amount = 0

    def _create_payment_vals_from_wizard(self):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard()
        res.update({
            'wallet': self.wallet,
            'wallet_amount': self.wallet_amount
        })
        return res

    def _create_payment_vals_from_batch(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_batch(batch_result)
        key_values = batch_result['key_values']
        lines = batch_result['lines']
        company = lines[0].company_id
        if key_values['currency_id'] == company.currency_id.id:
            wallet_amount = abs(sum(lines.mapped('wallet_amount_residual')))
        else:
            wallet_amount = abs(sum(lines.mapped('wallet_amount_residual_currency')))
        res.update({
            'wallet': True if wallet_amount > 0 else False,
            'wallet_amount': wallet_amount
        })
        return res
