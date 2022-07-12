from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    wallet = fields.Boolean(string='Is Wallet Deposit/Withdraw', help='Check this field if the payment is to deposit to or withdraw from wallet.')
    wallet_amount = fields.Monetary(currency_field='currency_id', compute='_compute_wallet_amount', store=True, tracking=True, readonly=False,
                                    states={
                                        'posted': [('readonly', True)],
                                        'sent': [('readonly', True)],
                                        'reconciled': [('readonly', True)],
                                        'cancelled': [('readonly', True)],
                                    })
    wallet_id = fields.Many2one('wallet', string='Wallet', readonly=True, help="The related wallet of the payment")

    @api.model
    def default_get(self, fields):
        # automatic payment's wallet amount filling on register payment form views
        rec = super(AccountPayment, self).default_get(fields)
        invoices = self.new({'invoice_ids': rec.get('invoice_ids', [])}).invoice_ids._origin
        if len(invoices) == 1 and invoices.wallet_total:
            rec['wallet'] = True
            rec['wallet_amount'] = invoices.wallet_total
        return rec

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
                
    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        res = super(AccountPayment, self)._onchange_payment_type()
        if self.payment_type != 'inbound':
            self.wallet = False
            self.wallet_amount = 0.0
        return res

    @api.depends('wallet', 'amount', 'currency_id', 'invoice_ids')
    def _compute_wallet_amount(self):
        for r in self:
            wallet_amount = 0.0
            if r.wallet:
                payment_invoices = r.invoice_ids._origin or r.invoice_ids
                if r.state == 'draft' and payment_invoices:
                    for currency in payment_invoices.mapped('currency_id'):
                        for invoices in payment_invoices.filtered(lambda inv: inv.currency_id == currency):
                            if r.currency_id != currency:
                                wallet_amount += currency._convert(
                                    sum(invoices.mapped('wallet_total')),
                                    r.currency_id,
                                    r.company_id,
                                    r.payment_date
                                )
                            else:
                                wallet_amount += sum(invoices.mapped('wallet_total'))
                else:
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

    def post(self):
        self.create_wallets_if_not_exist()
        res = super(AccountPayment, self).post()
        return res

    def create_wallets_if_not_exist(self):
        for r in self:
            currency = r._get_wallet_currency()
            r.wallet_id = r.wallet and r.partner_id._create_wallet_if_not_exist(currency)

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
        receivable_move_lines = self.move_line_ids.filtered(lambda l: l.account_id.internal_type == 'receivable')
        amount = -sum(receivable_move_lines.mapped('balance'))
        if amount:
            wallet_amount = self._get_wallet_amount_origin()
            return wallet_amount / amount
        return 0

    def _get_wallet_move_line_vals(self):
        self.ensure_one()
        vals = {}
        if not self.wallet:
            return vals
        if self.currency_id == self.company_id.currency_id:
            amount = self.wallet_amount
            amount_currency = 0
        else:
            amount = self.currency_id._convert(self.wallet_amount, self.company_id.currency_id, self.company_id, self.payment_date)
            amount_currency = self.wallet_amount
        sign = 1 if self.payment_type == 'inbound' else -1
        vals.update({
            'wallet': True,
            'wallet_id': self.wallet_id.id,
            'wallet_amount': sign * amount,
            'wallet_amount_currency': sign * amount_currency
        })
        return vals
    
    def _prepare_payment_moves(self):
        """
        Override to add wallet fields into account move line if payment contain wallet
        
        NOTE: on version 12.0 we override on `_get_counterpart_move_line_vals` that is not exist anymore
        """
        all_move_vals = super(AccountPayment, self)._prepare_payment_moves()
        for move_vals in all_move_vals:
            for line_tuplet in move_vals['line_ids']:
                line_vals = line_tuplet[2]
                if 'payment_id' in line_vals:
                    payment = self.browse(line_vals['payment_id'])
                    if payment.exists():
                        line_vals.update(payment._get_wallet_move_line_vals())
        return all_move_vals
