from odoo import models, fields, api, _
from odoo.exceptions import UserError


class account_payment(models.Model):
    _inherit = "account.payment"

    account_payment_line_ids = fields.One2many("account.payment.line", 'payment_id', string="Payment Details",
                                               readonly=False, states={'posted': [('readonly', True)],
                                                                       'sent': [('readonly', True)],
                                                                       'reconciled': [('readonly', True)],
                                                                       'cancelled': [('readonly', True)]},
                                               help="The lines to record counterparts of the bank/cash move of this payment. By default, when posting"
                                               " a payment, Odoo will generate a receivable or payable journal item of the account specified on the"
                                               " corresponding partner of the payment to counter the bank/cash move of the payment. If you specify a"
                                               " line here, the account set on the line will be used instead of the default partner's payable/receivable"
                                               " account.")

    suggest_lines = fields.Boolean(string='Suggest Lines', help="If checked, Odoo will try to find the journal items"
                                   " related to this partner that have not been fully reconciled and fill into the"
                                   " Payment Details.")
    
    def _get_suggest_payment_lines(self):
        account_payment_lines = self.env['account.payment.line']
        if self.partner_id and self.suggest_lines and self.payment_type != 'transfer' and self.company_id:
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
                        'currency_id': self.currency_id.id
                        })
                    account_payment_lines |= new_line
        return account_payment_lines

    @api.onchange('partner_id', 'suggest_lines', 'currency_id', 'company_id')
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
                if r.currency_id.compare_amounts(sum_payment_lines_amount, r.amount) != 0:
                    raise UserError(_("Payment Amount of the payment %s must be equal to the summary of its lines amount")
                                    % (r.display_name,))
    
    def _prepare_payment_moves(self):
        """
        Override to process payments that have payment lines
        """
        all_move_vals = super(account_payment, self)._prepare_payment_moves()
        #update label of all move lines to value of memo
        for move_vals in all_move_vals:
            for line in move_vals['line_ids']:
                payment = self.filtered(lambda p: p.id == line[2].get('payment_id', False))
                if payment and payment.communication:
                    line[2].update({'name': payment.communication})

        # for all the payments that have payment lines and are not internal transfer,
        # we will replace their Receivable / Payable lines with a reconciliable lines defined by payment lines
        to_process = self.filtered(lambda p: p.account_payment_line_ids and p.payment_type != 'transfer')
        for idx, payment in enumerate(to_process):
            move_vals = all_move_vals[idx]
            # remove the Receivable / Payable line which is the very first line in lines_ids
            move_vals['line_ids'].pop(0)
            liquidity_balance = 0
            # update data in payment lines
            for payment_line in payment.account_payment_line_ids:

                company_currency = payment.company_id.currency_id

                # Compute amounts.
                if payment.payment_type == 'outbound':
                    counterpart_amount = payment_line.amount
                else:
                    counterpart_amount = -payment_line.amount

                # Manage currency.
                if payment.currency_id == company_currency:
                    # Single-currency.
                    balance = counterpart_amount
                    counterpart_amount = 0.0
                    currency_id = False
                else:
                    # Multi-currencies.
                    balance = payment.currency_id._convert(counterpart_amount, company_currency,
                                                           payment.company_id, payment.payment_date)
                    currency_id = payment.currency_id.id
                    liquidity_balance += balance

                move_vals['line_ids'].insert(0, (0, 0, {
                    'name': payment_line.name,
                    'amount_currency': counterpart_amount if currency_id else 0.0,
                    'currency_id': currency_id,
                    'debit': balance > 0.0 and balance  or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'date_maturity': payment.payment_date,
                    'partner_id': payment.partner_id.commercial_partner_id.id,
                    'account_id': payment_line.account_id.id,
                    'payment_id': payment.id,
                }))

            if payment.currency_id != company_currency:
                # update after exchanging currency to avoid difference between debit and credit in journal entries
                move_vals['line_ids'][-1][2].update({
                    'debit': liquidity_balance < 0.0 and -liquidity_balance or 0.0,
                    'credit': liquidity_balance > 0.0 and liquidity_balance or 0.0,
                    })
        return all_move_vals
