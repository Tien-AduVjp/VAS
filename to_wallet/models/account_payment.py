from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    wallet = fields.Boolean(string='Is Wallet Deposit/Withdraw',  compute='_compute_wallet', store=True, readonly=False,
                            help="Check this field if the payment is to deposit to or withdraw from wallet.")
    wallet_amount = fields.Monetary(currency_field='currency_id', compute='_compute_wallet_amount', store=True, tracking=True, readonly=False,
                                    states={
                                        'posted': [('readonly', True)],
                                        'cancel': [('readonly', True)],
                                    }, help="Wallet Amount deposit/withdraw through payments")
    wallet_id = fields.Many2one('wallet', string='Wallet', readonly=True, help="The related wallet of the payment")

    @api.constrains('payment_type', 'wallet')
    def _check_payment_type(self):
        for r in self:
            if r.wallet and r.payment_type not in ('inbound', 'outbound'):
                raise ValidationError(_('Only inbound/outbound payment can deposit or withdraw with wallet.'))

    @api.constrains('amount', 'wallet_amount', 'journal_id')
    def _check_wallet_amount_vs_amount(self):
        for r in self:
            currency = r.currency_id or r.journal_id.currency_id or r.company_id.currency_id
            if float_compare(r.wallet_amount, 0.0, precision_rounding=currency.rounding) == -1:
                raise ValidationError(_('Wallet amount must be greater or equal to 0'))
            if float_compare(r.wallet_amount, r.amount, precision_rounding=currency.rounding) == 1:
                raise ValidationError(_('Wallet amount must not be greater than the payment amount which is %s') % r.amount)

    @api.constrains('wallet_amount', 'wallet', 'partner_id', 'payment_type')
    def _check_wallet_withdrawal(self):
        for r in self:
            currency = r.currency_id or r.journal_id.currency_id or r.company_id.currency_id
            partner_wallet = r.partner_id.commercial_partner_id.wallet_ids.filtered(lambda w: w.currency_id == currency)[:1]
            if r.payment_type == 'outbound' and r.wallet:
                if not partner_wallet:
                    raise ValidationError(_("The partner %s does not have any wallet to withdraw by the payment %s!")
                                          % (r.partner_id.display_name, r.display_name))
                elif partner_wallet and float_compare(r.wallet_amount, partner_wallet.realtime_amount, precision_rounding=currency.rounding) > 0:
                    raise ValidationError(_("%s's wallet only remains %d which is not enough to withdraw by the payment %s!")
                                          % (r.partner_id.display_name, partner_wallet.realtime_amount, r.display_name))

    @api.depends('is_internal_transfer', 'partner_id')
    def _compute_wallet(self):
        for r in self:
            if r.is_internal_transfer or not r.partner_id:
                r.wallet = False

    @api.depends('wallet', 'amount', 'currency_id')
    def _compute_wallet_amount(self):
        for r in self:
            wallet_amount = 0.0
            if r.wallet:
                wallet_amount += r.amount
            r.wallet_amount = wallet_amount

    @api.depends('currency_id', 'wallet')
    def _compute_wallet_currency(self):
        for r in self:
            r.wallet_currency_id = r.payment_transaction_id.sudo().currency_id or r.currency_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('wallet') and vals.get('amount') and not vals.get('wallet_amount'):
                vals['wallet_amount'] = vals.get('amount')
        return super(AccountPayment, self).create(vals_list)

    def write(self, vals):
        res = super(AccountPayment, self).write(vals)
        if 'wallet' in vals or 'wallet_amount' in vals:
            self.create_wallets_if_not_exist()
            for r in self:
                r.line_ids.write(r._get_wallet_move_line_vals())
        return res

    def create_wallets_if_not_exist(self):
        for r in self:
            if r.partner_id and r.wallet:
                currency = r._get_wallet_currency()
                r.wallet_id = r.partner_id._create_wallet_if_not_exist(currency)

    def _get_wallet_currency(self):
        self.ensure_one()
        return self.payment_transaction_id.sudo().currency_id if self.payment_transaction_id else self.currency_id

    def _get_wallet_amount_origin(self):
        self.ensure_one()
        return self.payment_transaction_id.sudo().amount if self.payment_transaction_id else self.amount

    def _get_wallet_currency_conversion_rate(self):
        self.ensure_one()
        if self._get_wallet_currency() == self.company_id.currency_id:
            return 1
        receivable_move_lines = self.line_ids.filtered(lambda l: l.account_id.internal_type == 'receivable')
        amount = -sum(receivable_move_lines.mapped('balance'))
        if amount:
            wallet_amount = self._get_wallet_amount_origin()
            return wallet_amount / amount
        return 0

    def _get_wallet_move_line_vals(self):
        self.ensure_one()
        vals = {}
        if not self.wallet:
            return {
                'wallet': False,
                'wallet_id': False,
                'wallet_amount': False,
                'wallet_amount_currency': False
            }
        amount = self.currency_id._convert(self.wallet_amount, self.company_id.currency_id, self.company_id, self.date)
        amount_currency = self.wallet_amount
        sign = 1 if self.payment_type == 'inbound' else -1
        vals.update({
            'wallet': True,
            'wallet_id': self.wallet_id.id,
            'wallet_amount': sign * amount,
            'wallet_amount_currency': sign * amount_currency
        })
        return vals

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """
        Override to add wallet fields into account move line if payment contain wallet

        NOTE: on version 13.0 we override on `_prepare_payment_moves` that is not exist anymore
        """
        line_vals_list = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
        self.create_wallets_if_not_exist()
        for line_vals in line_vals_list:
            line_vals.update(self._get_wallet_move_line_vals())
        return line_vals_list
