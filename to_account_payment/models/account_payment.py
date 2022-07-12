from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import float_compare


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    account_payment_line_ids = fields.One2many('account.payment.line', 'payment_id', string='Payment Details',
                                               readonly=False, states={'posted': [('readonly', True)],
                                                                       'cancel': [('readonly', True)]},
                                               help="The lines to record counterparts of the bank/cash move of this payment. By default, when posting"
                                               " a payment, Odoo will generate a receivable or payable journal item of the account specified on the"
                                               " corresponding partner of the payment to counter the bank/cash move of the payment. If you specify a"
                                               " line here, the account set on the line will be used instead of the default partner's payable/receivable"
                                               " account.")

    suggest_lines = fields.Boolean(string='Suggest Lines', states={'posted': [('readonly', True)],
                                                                   'cancel': [('readonly', True)]},
                                   help="If checked, Odoo will try to find the journal items"
                                   " related to this partner that have not been fully reconciled and fill into the"
                                   " Payment Details.")
    manual_reconcile = fields.Boolean(string='Manual Reconcile', compute='_compute_manual_reconcile',
                                      help="If True, show the button which was linked to reconciliation widget for manual reconcile.")
    

    def _get_suggest_payment_lines(self):
        account_payment_lines = self.env['account.payment.line']
        if self.partner_id and self.suggest_lines and self.is_internal_transfer == False and self.company_id:
            not_full_reconciled_move_lines = self.partner_id.commercial_partner_id._get_not_full_reconciled_account_move_lines(self.company_id)
            if self.currency_id != self.company_id.currency_id:
                not_full_reconciled_move_lines = not_full_reconciled_move_lines.filtered(lambda l: l.currency_id == self.currency_id)
            else:
                not_full_reconciled_move_lines = not_full_reconciled_move_lines.filtered(lambda l: not l.currency_id or l.currency_id == self.company_id.currency_id)

            if self.payment_type == 'inbound':
                not_full_reconciled_move_lines = not_full_reconciled_move_lines.filtered(lambda l: l.debit > 0.0)
            elif self.payment_type == 'outbound':
                not_full_reconciled_move_lines = not_full_reconciled_move_lines.filtered(lambda l: l.credit > 0.0)

            for account in not_full_reconciled_move_lines.mapped('account_id'):
                lines = not_full_reconciled_move_lines.filtered(lambda l: l.account_id == account)
                amount_residual_field = 'amount_residual_currency' if self.currency_id != self.company_id.currency_id else 'amount_residual'
                amount = abs(sum(lines.mapped(amount_residual_field)))
                if amount > 0.0:
                    new_line = account_payment_lines.new({
                        'name': ', '.join(lines.mapped('move_id.display_name')),
                        'account_id': account.id,
                        'payment_id': self.id,
                        'amount': amount,
                        'amount_suggested': amount,
                        'currency_id': self.currency_id.id,
                        'move_line_ids': [(6, 0, lines.ids)]
                        })
                    account_payment_lines |= new_line
        return account_payment_lines

    @api.onchange('partner_id', 'payment_type', 'suggest_lines', 'currency_id', 'company_id')
    def _onchange_suggest_lines(self):
        self.account_payment_line_ids = self._get_suggest_payment_lines()

    @api.onchange('account_payment_line_ids')
    def _onchange_account_payment_line_ids(self):
        self.amount = sum(self.account_payment_line_ids.mapped('amount'))

    @api.constrains('account_payment_line_ids', 'amount')
    def _check_account_payment_line_ids(self):
        for r in self:
            if r.account_payment_line_ids:
                sum_payment_lines_amount = sum(r.account_payment_line_ids.mapped('amount'))
                if r.currency_id and r.currency_id.compare_amounts(sum_payment_lines_amount, r.amount) != 0:
                    raise UserError(_("Payment Amount of the payment %s must be equal to the summary of its lines amount")
                                    % (r.display_name,))
                    
    @api.depends('state', 'account_payment_line_ids.move_line_ids.reconciled', 'move_id.line_ids.reconciled')
    def _compute_manual_reconcile(self):
        for r in self:
            r.manual_reconcile = False 
            if r.state =='posted' and r.account_payment_line_ids.move_line_ids \
                and not all(line.reconciled for line in r.account_payment_line_ids.move_line_ids) \
                and not all (line.reconciled for line in r.move_id.line_ids.filtered(lambda l: l.account_id.id in r.account_payment_line_ids.move_line_ids.account_id.ids)):
                r.manual_reconcile = True

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        """
        Override to process payments that have payment lines
        """
        res = super(AccountPayment, self)._prepare_move_line_default_vals(write_off_line_vals)
        # update label of all move lines to value of memo
        for line in res:
            if self.ref:
                line.update({'name': self.ref})

        # for all the payments that have payment lines and are not internal transfer,
        # we will replace their Receivable / Payable lines with a reconciliable lines defined by payment lines
        if self.account_payment_line_ids and self.is_internal_transfer == False:
            # remove the Receivable / Payable line
            res.pop(1)
            # update data in payment lines
            company_currency = self.company_id.currency_id
            for payment_line in self.account_payment_line_ids:
                # Compute amounts.
                if self.payment_type == 'inbound':
                    # Receive money.
                    liquidity_amount_currency = payment_line.amount
                elif self.payment_type == 'outbound':
                    # Send money.
                    liquidity_amount_currency = -payment_line.amount
                else:
                    liquidity_amount_currency = 0.0
                liquidity_balance = self.currency_id._convert(
                    liquidity_amount_currency,
                    company_currency,
                    self.company_id,
                    self.date,
                )
                counterpart_amount_currency = -liquidity_amount_currency
                counterpart_balance = -liquidity_balance
                currency_id = self.currency_id.id
                res.append({
                    'name': self.ref or payment_line.name,
                    'date_maturity': self.date,
                    'amount_currency': counterpart_amount_currency,
                    'currency_id': currency_id,
                    'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                    'credit':-counterpart_balance if counterpart_balance < 0.0 else 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': payment_line.account_id.id,
                })
        return res

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        skip_account_move_synchronization_payments_vals_list = []
        account_move_synchronization_payments_vals_list = []
        Payments = self.env['account.payment']
        for vals in vals_list:
            if vals.get('account_payment_line_ids', []):
                skip_account_move_synchronization_payments_vals_list.append(vals)
            else:
                account_move_synchronization_payments_vals_list.append(vals)
        if skip_account_move_synchronization_payments_vals_list:
            skip_payments = super(AccountPayment, self.with_context(skip_account_move_synchronization=True))\
            .create(skip_account_move_synchronization_payments_vals_list)
            Payments |= skip_payments
        if account_move_synchronization_payments_vals_list:
            payments = super(AccountPayment, self).create(account_move_synchronization_payments_vals_list)
            Payments |= payments
        for payment in Payments:
            liquidity_lines, counterpart_lines, writeoff_lines = payment._seek_for_lines()
            if len(liquidity_lines) > 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal entry must always contains:\n"
                        "- one journal item involving the outstanding payment/receipts account.\n"
                        "- one or more journal items involving a receivable/payable account.\n"
                    ) % payment.move_id.display_name)
        return Payments

    def _synchronize_multi_line_from_moves(self, changed_fields):
        for r in self:
            move = r.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if r.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = r._seek_for_lines()

                if len(liquidity_lines) != 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal entry must always have only one journal item involving the outstanding payment/receipts account"
                    ) % move.display_name)

                if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, all the write-off journal items must share the same account."
                    ) % move.display_name)
                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same currency."
                    ) % move.display_name)
                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal items must share the same partner."
                    ) % move.display_name)
                partner_type = r.partner_type
                if counterpart_lines and counterpart_lines[0].account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                elif counterpart_lines and counterpart_lines[0].account_id.user_type_id.type == 'payable':
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if counterpart_lines:
                    payment_vals_to_write.update({'destination_account_id': counterpart_lines[0].account_id.id})
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            r.write(move._cleanup_write_orm_values(r, payment_vals_to_write))

    def _get_multi_line_payment_domain(self):
        return [
                    ('account_payment_line_ids', '!=', False),
                    ('is_internal_transfer', '=', False)
                ]

    def _synchronize_from_moves(self, changed_fields):
        if self._context.get('skip_account_move_synchronization'):
            return
        domain = self._get_multi_line_payment_domain()
        domain = expression.AND([domain, [('move_id.statement_line_id', '=', False)]])
        multi_line_payments = self.filtered_domain(domain)
        payments = self - multi_line_payments

        if multi_line_payments:
            multi_line_payments.with_context(skip_account_move_synchronization=True)._synchronize_multi_line_from_moves(changed_fields)
        if payments:
            super(AccountPayment, payments)._synchronize_from_moves(changed_fields)

    def _synchronize_multi_line_to_moves(self, changed_fields):
        if not any(field_name in changed_fields for field_name in (
            'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
            'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id', 'journal_id',
        )):
            return

        for r in self:
            liquidity_lines, counterpart_lines, writeoff_lines = r._seek_for_lines()
            if liquidity_lines and counterpart_lines and writeoff_lines:
                counterpart_amount = sum(counterpart_lines.mapped('amount_currency'))
                writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))

                if (counterpart_amount > 0.0) == (writeoff_amount > 0.0):
                    sign = -1
                else:
                    sign = 1
                writeoff_amount = abs(writeoff_amount) * sign

                write_off_line_vals = {
                    'name': writeoff_lines[0].name,
                    'amount': writeoff_amount,
                    'account_id': writeoff_lines[0].account_id.id,
                }
            else:
                write_off_line_vals = {}
            line_vals_list = r._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)

            line_ids_commands = []
            if liquidity_lines:
                if len(liquidity_lines) > 1:
                    raise UserError(_(
                        "The journal entry %s reached an invalid state relative to its payment.\n"
                        "To be consistent, the journal entry must always contains:\n"
                        "- one journal item involving the outstanding payment/receipts account.\n"
                        "- one or more journal items involving a receivable/payable account.\n"
                    ) % r.move_id.display_name)
                line_ids_commands.append((1, liquidity_lines.id, line_vals_list[0]))
            else:
                line_ids_commands.append((0, 0, line_vals_list[0]))
            if counterpart_lines:
                for line in counterpart_lines:
                    line_ids_commands.append((2, line.id, 0))
                for counterpart_vals in line_vals_list[1:]:
                    line_ids_commands.append((0, 0, counterpart_vals))
            else:
                line_ids_commands.append((0, 0, line_vals_list[1]))

            for line in writeoff_lines:
                line_ids_commands.append((2, line.id))

            r.move_id.write({
                'partner_id': r.partner_id.id,
                'currency_id': r.currency_id.id,
                'partner_bank_id': r.partner_bank_id.id,
                'line_ids': line_ids_commands,
            })

    def _synchronize_to_moves(self, changed_fields):
        if self._context.get('skip_account_move_synchronization'):
            return

        domain = self._get_multi_line_payment_domain()
        multi_line_payments = self.filtered_domain(domain)
        payments = self - multi_line_payments

        if multi_line_payments:
            multi_line_payments.with_context(skip_account_move_synchronization=True)._synchronize_multi_line_to_moves(changed_fields)
        if payments:
            super(AccountPayment, payments)._synchronize_to_moves(changed_fields)

    def _seek_for_lines(self):
        """
            By default, move lines with accounts which are not in liquidity, receivable, payable types should be taken to
            writeoff_lines. So we should move these move lines which have accounts in account_payment_line_ids to counterpart_lines.
        """
        self.ensure_one()
        liquidity_lines, counterpart_lines, writeoff_lines = super(AccountPayment, self)._seek_for_lines()
        if self.account_payment_line_ids:
            counterpart_missing_lines = writeoff_lines.filtered(
                                                                lambda l: l.account_id.id in self.account_payment_line_ids.account_id.ids
                                                                    or l.account_id.reconcile
                                                                )
            counterpart_lines |= counterpart_missing_lines
            writeoff_lines -= counterpart_missing_lines
        return liquidity_lines, counterpart_lines, writeoff_lines
    
    def action_post(self):
        super(AccountPayment, self).action_post()
        for r in self:
            for line in r.account_payment_line_ids.filtered(
                                                            lambda l: l.move_line_ids 
                                                            and float_compare(l.amount, l.amount_suggested, r.currency_id.rounding) == 0
                                                            ):
                lines_to_reconcile = self.env['account.move.line']
                lines_to_reconcile |= line.move_line_ids
                lines_to_reconcile |= r.move_id.line_ids.filtered(lambda l: l.account_id == line.account_id)
                lines_to_reconcile.reconcile()
