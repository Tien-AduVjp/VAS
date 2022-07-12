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
        for r in self.filtered(lambda l: not l.payment_id or (l.payment_id and l in l.payment_id.line_ids)).\
            sorted(lambda a: a.account_id.internal_type == 'receivable'):
            wallet_amount = 0.0
            wallet_amount_currency = 0.0
            if r.move_id.move_type in ('out_invoice', 'out_refund'):
                # calculate wallet fields for invoice lines
                if r.account_id.internal_type != 'receivable':
                    if r.wallet:
                        wallet_amount = r.currency_id._convert(
                            r.price_total,
                            r.company_currency_id,
                            r.company_id,
                            r.move_id.invoice_date or fields.Date.today()
                            )
                        wallet_amount_currency = r.price_total

                # calculate wallet fields for invoice receivable lines
                else:
                    wallet_ctp_ids = r.ctp_aml_ids.filtered(lambda r: r.wallet)
                    if wallet_ctp_ids:
                        r.wallet = True
                        wallet_amount = -sum(wallet_ctp_ids.mapped('wallet_amount'))
                        wallet_amount_currency = -sum(wallet_ctp_ids.mapped('wallet_amount_currency'))

            elif r.move_id.move_type == 'entry' and not r.payment_id and r.account_id.internal_type == 'receivable' and r.partner_id:
                currency = r.currency_id
                if not currency.is_zero(r.move_id.wallet_total):
                    r.wallet_id = r.partner_id._create_wallet_if_not_exist(currency)
                    wallet_amount = currency._convert(
                        r.move_id.wallet_total,
                        r.company_currency_id,
                        r.company_id,
                        r.move_id.date or fields.Date.today()
                        )
                    wallet_amount_currency = r.move_id.wallet_total
                    r.wallet = True
            elif r.payment_id:
                move_line_vals = r.payment_id._get_wallet_move_line_vals()
                wallet_amount = move_line_vals.get('wallet_amount', 0.0)
                wallet_amount_currency = move_line_vals.get('wallet_amount_currency', 0.0)
                r.wallet = move_line_vals.get('wallet', False)
            r.wallet_amount = wallet_amount
            r.wallet_amount_currency = wallet_amount_currency

    @api.depends('wallet', 'wallet_amount', 'wallet_amount_currency',
                 'matched_debit_ids', 'matched_credit_ids', 'account_id',)
    def _compute_wallet_amount_residual(self):
        """Fork from the method _compute_amount_residual().

        Computation is almost same as _compute_amount_residual(). The differences are:
            * Use wallet_amount (and wallet_amount_currency) as base amount instead of balance (and amount_currency).
            * Subtract total amount of wallet partial reconcile records instead of all matching partial reconcile records.
        """
        for line in self:
            if not line.wallet or line.account_id.internal_type != 'receivable':
                line.wallet_amount_residual = 0
                line.wallet_amount_residual_currency = 0
                continue
            sign = 1 if line.balance > 0.0 else -1
            wallet_matched_credit = line.matched_credit_ids.filtered(lambda r: r.wallet)
            wallet_matched_debit = line.matched_debit_ids.filtered(lambda r: r.wallet)
            wallet_reconciled_balance = sum(wallet_matched_credit.mapped('amount')) - sum(wallet_matched_debit.mapped('amount'))
            wallet_reconciled_amount_currency = sum(wallet_matched_credit.mapped('debit_amount_currency')) - sum(wallet_matched_debit.mapped('credit_amount_currency'))

            line.wallet_amount_residual = sign * abs(line.wallet_amount) - wallet_reconciled_balance
            line.wallet_amount_residual_currency = sign * abs(line.wallet_amount_currency) - wallet_reconciled_amount_currency

    @api.depends('amount_residual', 'wallet_amount_residual', 'amount_residual_currency', 'wallet_amount_residual_currency')
    def _compute_non_wallet_amount_residual(self):
        for line in self:
            if not line.wallet or line.account_id.internal_type != 'receivable':
                line.non_wallet_amount_residual = line.amount_residual
                line.non_wallet_amount_residual_currency = line.amount_residual_currency
            else:
                line.non_wallet_amount_residual = line.amount_residual - line.wallet_amount_residual
                line.non_wallet_amount_residual_currency = line.amount_residual_currency - line.wallet_amount_residual_currency

    def reconcile(self):
        """
        This override ensures the followings:
            1. If all the lines are non-wallet lines, fall back to the Odoo's default behavior
            2. If all the lines are wallet lines, reconcile them with reconcile amount of wallet
              residual instead of normal residual amount
            3. If one or more (not all) of the lines are wallet, reconcile with
              non_wallet_amount_residual or non_wallet_amount_residual_currency
            4. after the operation above mentioned, fall back for the remaining unreconciled lines
        """

        self = self.sorted(key=lambda line: (line.date_maturity or line.date, line.currency_id))
        debit_lines = self.filtered(lambda line: line.balance > 0.0 or line.amount_currency > 0.0)
        credit_lines = self.filtered(lambda line: line.balance < 0.0 or line.amount_currency < 0.0)
        # fall back to the default behavior if neither debit_lines nor credit_lines are wallet lines
        if all(not debit_move.wallet for debit_move in debit_lines) and all(not credit_move.wallet for credit_move in credit_lines):
            return super(AccountMoveLine, self).reconcile()

        res = {
            'partials': self.env['account.partial.reconcile'],
            'tax_cash_basis_moves': self.env['account.move'],
            'full_reconcile': self.env['account.full.reconcile']
        }
        ctx = self._context.copy()

        def _reconcile(wallet):
            if wallet:
                amount_field = 'wallet_amount_residual'
                amount_currency_field = 'wallet_amount_residual_currency'
            else:
                amount_field = 'non_wallet_amount_residual'
                amount_currency_field = 'non_wallet_amount_residual_currency'
            excluded_debit_lines = excluded_credit_lines = self.browse()
            while True:
                valid_debit_lines = (debit_lines - excluded_debit_lines).filtered(
                    lambda l: not l.reconciled \
                        and getattr(l, amount_field if l.currency_id == l.company_currency_id else amount_currency_field)
                    )
                valid_credit_lines = (credit_lines - excluded_credit_lines).filtered(
                    lambda l: not l.reconciled \
                        and getattr(l, amount_field if l.currency_id == l.company_currency_id else amount_currency_field)
                    )
                if not valid_debit_lines or not valid_credit_lines:
                    break

                debit_line = valid_debit_lines[0]
                credit_line = valid_credit_lines[0]
                # Refer to _prepare_reconciliation_partials method
                force_amount = min(getattr(debit_line, amount_field), -getattr(credit_line, amount_field))
                if debit_line.currency_id == credit_line.currency_id:
                    min_amount_currency = min(
                        getattr(debit_line, amount_currency_field),
                        -getattr(credit_line, amount_currency_field)
                        )
                    force_debit_amount_currency = min_amount_currency
                    force_credit_amount_currency = min_amount_currency
                else:
                    if not force_amount or not debit_line.balance or not credit_line.balance:
                        if not getattr(debit_line, amount_field) or not debit_line.balance:
                            excluded_debit_lines += debit_line
                        if not getattr(credit_line, amount_field) or not credit_line.balance:
                            excluded_credit_lines += credit_line
                        continue
                    # convert force_amount to the line's corresponding currency
                    force_debit_amount_currency = force_amount * (debit_line.amount_currency / debit_line.balance)
                    force_credit_amount_currency = force_amount * (credit_line.amount_currency / credit_line.balance)

                ctx.update({
                    'partial_reconcile_wallet': wallet,
                    'force_amount': force_amount,
                    'force_debit_amount_currency': force_debit_amount_currency,
                    'force_credit_amount_currency': force_credit_amount_currency
                })
                result = super(AccountMoveLine, (debit_line + credit_line).with_context(ctx)).reconcile()
                res['partials'] |= result['partials']
                if result.get('tax_cash_basis_moves', False):
                    res['tax_cash_basis_moves'] |= result['tax_cash_basis_moves']
                if result.get('full_reconcile', False):
                    res['full_reconcile'] |= result['full_reconcile']

        _reconcile(True)
        _reconcile(False)
        return res

    def _create_exchange_difference_move(self):
        return super(
            AccountMoveLine,
            self.with_context(
                force_debit_amount_currency=False,
                force_credit_amount_currency=False,
                force_amount=False
                )
            )._create_exchange_difference_move()
