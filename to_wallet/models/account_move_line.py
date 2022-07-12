import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    wallet = fields.Boolean(string='Is Wallet Operation',
                            help="This field indicates if this journal item is related to eWallet operations."
                            " If this is an invoice line, this indicates if the item could be paid with wallet only.")
    wallet_id = fields.Many2one('wallet', string='Related Wallet', readonly=True)
    wallet_amount = fields.Monetary(currency_field='company_currency_id', readonly=True)
    wallet_amount_currency = fields.Monetary(currency_field='currency_id', readonly=True)
    wallet_amount_residual = fields.Monetary(currency_field='company_currency_id', compute='_compute_wallet_amount_residual', store=True)
    wallet_amount_residual_currency = fields.Monetary(currency_field='currency_id', compute='_compute_wallet_amount_residual', store=True)
    non_wallet_amount_residual = fields.Monetary(currency_field='company_currency_id', compute='_compute_non_wallet_amount_residual', store=True)
    non_wallet_amount_residual_currency = fields.Monetary(currency_field='currency_id', compute='_compute_non_wallet_amount_residual', store=True)

    @api.constrains('balance', 'currency_id', 'amount_currency', 'wallet_amount', 'wallet_amount_currency')
    def _check_wallet_amount(self):
        for r in self:
            if r.account_id.internal_type != 'receivable':
                continue
            sign = 1 if r.balance > 0 else -1
            if sign * r.wallet_amount > 0:
                raise ValidationError(_('%s: Sign of wallet amount is wrong!') % r.display_name)
            elif sign * r.wallet_amount_currency > 0:
                raise ValidationError(_('%s: Sign of wallet amount currency is wrong!') % r.display_name)
            elif r.company_id.currency_id.compare_amounts(abs(r.wallet_amount), abs(r.balance)) > 1:
                raise ValidationError(_('%s: Wallet amount must not be greater than total amount!') % r.display_name)
            elif r.currency_id and r.currency_id.compare_amounts(abs(r.wallet_amount_currency), abs(r.amount_currency)) > 1:
                raise ValidationError(_('%s: Wallet amount currency must not be greater than total amount currency!') % r.display_name)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountMoveLine, self)._onchange_product_id()
        for r in self:
            if r.product_id and r.product_id.wallet:
                r.wallet = True
            else:
                r.wallet = False
        return res

    def _compute_wallet_amount(self):
        """
        :deprecated: This method is not compliant with the naming convention
        """
        _logger.warning("The method `_compute_wallet_amount()` is deprecated, please use the `_update_wallet_amount()` instead.")
        self._update_wallet_amount()

    def _update_wallet_amount(self):
        """
        This compute wallet fields for:
            1. customer invoice lines
            2. customer invoice's receivable lines
            3. payment move lines
            4. If the line is not either of the above, set zero for the numeric fields
        """
        # the wallet amount computation on 'receivable' account depend on the computation result of other move lines
        # so, we need to sort lines to calculate move line of 'receivable' account in the last
        for r in self.sorted(lambda a: a.account_id.internal_type == 'receivable'):
            wallet_amount = 0.0
            wallet_amount_currency = 0.0
            if r.move_id.type in ('out_invoice', 'out_refund'):
                # calculate wallet fields for invoice lines
                if r.account_id.internal_type != 'receivable':
                    if r.wallet:
                        if r.currency_id and r.currency_id != r.company_currency_id:
                            wallet_amount = r.currency_id._convert(
                                r.price_total,
                                r.company_currency_id,
                                r.company_id,
                                r.move_id.invoice_date or fields.Date.today()
                                )
                            wallet_amount_currency = r.price_total
                        else:
                            wallet_amount = r.price_total
                # calculate wallet fields for invoice receivable lines
                else:
                    wallet_ctp_ids = r.ctp_aml_ids.filtered(lambda r: r.wallet)
                    if wallet_ctp_ids:
                        r.wallet = True
                        wallet_amount = -sum(wallet_ctp_ids.mapped('wallet_amount'))
                        wallet_amount_currency = -sum(wallet_ctp_ids.mapped('wallet_amount_currency'))
                r.wallet_amount = wallet_amount
                r.wallet_amount_currency = wallet_amount_currency
            elif r.move_id.type == 'entry' and not r.payment_id and r.account_id.internal_type == 'receivable' and r.partner_id:
                currency = r.currency_id or r.company_currency_id
                if not currency.is_zero(r.move_id.wallet_total):
                    r.wallet_id = r.partner_id._create_wallet_if_not_exist(currency)
                    if r.currency_id and r.currency_id != r.company_currency_id:
                        wallet_amount = r.currency_id._convert(
                            r.move_id.wallet_total,
                            r.company_currency_id,
                            r.company_id,
                            r.move_id.date or fields.Date.today()
                            )
                        wallet_amount_currency = r.move_id.wallet_total
                    else:
                        wallet_amount = r.move_id.wallet_total
                    r.wallet = True
                r.wallet_amount = wallet_amount
                r.wallet_amount_currency = wallet_amount_currency

    @api.depends('move_id.company_id', 'wallet', 'wallet_amount', 'wallet_amount_currency', 'currency_id',
                 'matched_debit_ids.amount', 'matched_credit_ids.amount',
                 'matched_debit_ids.amount_currency', 'matched_credit_ids.amount_currency',
                 'matched_debit_ids.wallet', 'matched_credit_ids.wallet',
                 'amount_residual', 'amount_residual_currency', 'reconciled', 'parent_state')
    def _compute_wallet_amount_residual(self):
        """Fork from the method _amount_residual().

        Computation is almost same as _amount_residual(). The differences are:
            * Use wallet_amount (and wallet_amount_currency) as base amount instead of balance (and amount_currency).
            * Subtract total amount of wallet partial reconcile records instead of all matching partial reconcile records.
        """
        for line in self:
            if not line.wallet or line.account_id.internal_type != 'receivable':
                line.wallet_amount_residual = 0
                line.wallet_amount_residual_currency = 0
                continue

            amount_residual = abs(line.wallet_amount)
            amount_residual_currency = abs(line.wallet_amount_currency)
            sign = 1 if (line.debit - line.credit) > 0.0 else -1

            for partial_line in (line.matched_debit_ids + line.matched_credit_ids):
                if not partial_line.wallet:
                    continue

                # If line is a credit (sign = -1) we:
                #  - subtract matched_debit_ids (partial_line.credit_move_id == line)
                #  - add matched_credit_ids (partial_line.credit_move_id != line)
                # If line is a debit (sign = 1), do the opposite.
                sign_partial_line = sign if partial_line.credit_move_id == line else -sign

                amount_residual += sign_partial_line * partial_line.amount
                # compute amount_residual_currency if available
                if line.currency_id and line.wallet_amount_currency:
                    # in case of line and partial line had same currency id, compute like normal amount
                    if partial_line.currency_id and partial_line.currency_id == line.currency_id:
                        amount_residual_currency += sign_partial_line * partial_line.amount_currency
                    else:
                        # in case of line and partial line do not have same currency then we need
                        # find the rate to conversion to correct amount
                        if line.balance and line.amount_currency:
                            rate = line.amount_currency / line.balance
                        else:
                            # get conversion rate at exact date of move
                            date = partial_line.credit_move_id.date if partial_line.debit_move_id == line else partial_line.debit_move_id.date
                            rate = line.currency_id.with_context(date=date).rate
                        amount_residual_currency += sign_partial_line * line.currency_id.round(partial_line.amount * rate)

            line.wallet_amount_residual = line.move_id.company_id.currency_id.round(amount_residual * sign)
            line.wallet_amount_residual_currency = line.currency_id and line.currency_id.round(amount_residual_currency * sign) or 0.0

    @api.depends('amount_residual', 'wallet_amount_residual', 'amount_residual_currency', 'wallet_amount_residual_currency')
    def _compute_non_wallet_amount_residual(self):
        for line in self:
            if not line.wallet or line.account_id.internal_type != 'receivable':
                line.non_wallet_amount_residual = line.amount_residual
                line.non_wallet_amount_residual_currency = line.amount_residual_currency
                continue
            else:
                line.non_wallet_amount_residual = line.amount_residual - line.wallet_amount_residual
                line.non_wallet_amount_residual_currency = line.amount_residual_currency - line.wallet_amount_residual_currency

    def _reconcile_lines(self, debit_moves, credit_moves, field):
        """
        This override ensures the followings:
            1. If all the lines are non-wallet lines, fall back to the Odoo's default behavior
            2. If all the lines are wallet lines, reconcile them with reconcile amount of wallet
              residual instead of normal residual amount
            3. If one or more (not all) of the lines are wallet, reconcile with
              non_wallet_amount_residual or non_wallet_amount_residual_currency
            4. after the operation above mentioned, fall back for the remaining unreconciled lines
        """
        # fall back to the default behavior if neither debit_moves nor credit_moves are wallet lines
        if all(not debit_move.wallet for debit_move in debit_moves) and all(not credit_move.wallet for credit_move in credit_moves):
            return super(AccountMoveLine, self)._reconcile_lines(debit_moves, credit_moves, field)
        # define wallet related fields for reconciliation
        if self[0].account_id.currency_id and self[0].account_id.currency_id != self[0].account_id.company_id.currency_id:
            wallet_field = 'wallet_amount_residual_currency'
        else:
            wallet_field = 'wallet_amount_residual'
        non_wallet_field = 'non_%s' % wallet_field

        remaining_moves = self.env['account.move.line']
        # loop over the debit moves and credit moves until either of them is not able to get reconciled anymore
        while (sum(debit_moves.mapped(wallet_field)) and sum(credit_moves.mapped(wallet_field))):
            valid_debit_moves = debit_moves.filtered(lambda l: getattr(l, wallet_field))
            valid_credit_moves = credit_moves.filtered(lambda l: getattr(l, wallet_field))
            if not valid_debit_moves or not valid_credit_moves:
                break
            ctx = {'partial_reconcile_wallet':True}
            # if no payment define for the debit move, the super()._reconcile_lines() will not work properlly with foreign currency wallet and invoice
            if valid_debit_moves[0].currency_id == valid_credit_moves[0].currency_id \
                and valid_debit_moves[0].currency_id != valid_debit_moves[0].account_id.company_id.currency_id:
                force_amount_currency = min(valid_debit_moves[0].wallet_amount_residual_currency, -valid_credit_moves[0].wallet_amount_residual_currency)
                ctx.update({
                    'force_reconcile_currency_id': valid_debit_moves[0].currency_id.id if force_amount_currency else False,
                    'force_amount_currency': force_amount_currency
                    })
            remaining_moves |= super(AccountMoveLine, self.with_context(ctx))._reconcile_lines(valid_debit_moves[0], valid_credit_moves[0], wallet_field)
        while (sum(debit_moves.mapped(non_wallet_field)) and sum(credit_moves.mapped(non_wallet_field))):
            valid_debit_moves = debit_moves.filtered(lambda l: getattr(l, non_wallet_field))
            valid_credit_moves = credit_moves.filtered(lambda l: getattr(l, non_wallet_field))
            if not valid_debit_moves or not valid_credit_moves:
                break
            remaining_moves |= super(AccountMoveLine, self)._reconcile_lines(valid_debit_moves[0], valid_credit_moves[0], non_wallet_field)

        # ensure reconciled move lines will not be returned
        remaining_moves = remaining_moves.filtered(lambda l: not l.reconciled)
        return remaining_moves
