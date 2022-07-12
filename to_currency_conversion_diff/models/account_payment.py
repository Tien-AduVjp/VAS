from datetime import date

from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_payment_transaction_diff(self):
        """
        This method is to get the difference between the payment and its corresponding payment transaction
        in company's currency.
        If the result is positive, it means the payment amount is less than the transaction amount and the
        difference will be encoded in the loss account specified in the company's currency conversion difference journal.
        Otherwise, the difference will be done in the profit account specified in the company's currency conversion difference journal
        """
        self.ensure_one()
        payment = self.filtered(lambda p: \
                                p.payment_transaction_id \
                                and p.payment_transaction_id.currency_id != p.currency_id \
                                and p.partner_type == 'customer' \
                                and p.payment_type == 'inbound')
        if payment:
            # convert payment transaction amount to company currency for later comparison for difference
            payment_transaction_amount = payment.payment_transaction_id.amount
            if payment.payment_transaction_id.currency_id != payment.company_id.currency_id:
                payment_transaction_amount = payment.payment_transaction_id.currency_id._convert(
                    payment.payment_transaction_id.amount,
                    payment.company_id.currency_id,
                    payment.company_id,
                    payment.payment_transaction_id.date and payment.payment_transaction_id.date or fields.Date.today()
                    )
            payment_amount = payment.currency_id._convert(
                payment.amount,
                payment.company_id.currency_id,
                payment.company_id,
                payment.date
                )
            # because payment_transaction_amount has no sign (it is always positive)
            # we will absolute payment_amount before making devision
            payment_different = payment_transaction_amount - abs(payment_amount)
        else:
            payment_different = 0.0
        return payment_different

    def _prepare_currency_conversion_diff_move_lines_data(self, journal, diff_amount):
        self.ensure_one()
        # receivable line
        line1 = {
            'name': _('Currency conversion difference'),
            'debit': diff_amount < 0 and -diff_amount or 0.0,
            'credit': diff_amount > 0 and diff_amount or 0.0,
            'account_id': self.partner_id.commercial_partner_id.property_account_receivable_id.id,
            'partner_id': self.partner_id.commercial_partner_id.id,
        }

        if diff_amount > 0:
            diff_account_id = journal.company_id.expense_currency_conversion_diff_account_id.id
        else:
            diff_account_id = journal.company_id.income_currency_conversion_diff_account_id.id

        line2 = {
            'name': _('Currency conversion difference'),
            'debit': diff_amount > 0 and diff_amount or 0.0,
            'credit': diff_amount < 0 and -diff_amount or 0.0,
            'account_id': diff_account_id,
            'partner_id': self.partner_id.commercial_partner_id.id,
        }
        return [line1, line2]

    def _prepare_currency_conversion_diff_move_data(self, diff_amount):
        self.ensure_one()
        company = self.company_id
        if not company.currency_conversion_diff_journal_id:
            raise UserError(_("You should configure the 'Currency Conversion Difference Journal' in the accounting settings, to manage automatically the booking of accounting entries related to differences between currency conversions."))
        if not company.income_currency_conversion_diff_account_id:
            raise UserError(_("You should configure the 'Gain Currency Conversion Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
        if not company.expense_currency_conversion_diff_account_id:
            raise UserError(_("You should configure the 'Loss Currency Conversion Account' in the accounting settings, to manage automatically the booking of accounting entries related to differences between exchange rates."))
        res = {
            'payment_id': self.id,
            'partner_id': self.partner_id.commercial_partner_id.id,
            'journal_id': company.currency_conversion_diff_journal_id.id,
            'ref': self.name,
            'line_ids': [(0, 0, line) for line in self._prepare_currency_conversion_diff_move_lines_data(company.currency_conversion_diff_journal_id, diff_amount)]
            }
        # The move date should be the maximum date between payment and invoice
        # (in case of payment in advance). However, we should make sure the
        # move date is not recorded after the end of year closing.
        if self.date > (company.fiscalyear_lock_date or date.min):
            res['date'] = self.date
        return res

    def _get_unreconciled_payment_move_lines_domain(self):
        """
        Get the domain for searching for payment move lines (move lines that link to the current payment)
            that have not been fully reconciled
        """
        return [
            ('payment_id', 'in', self.ids),
            ('account_id.internal_type', '=', 'receivable'),
            ('reconciled', '=', False)
            ]

    def action_post(self):
        for payment in self.filtered(lambda p: \
                                     p.payment_transaction_id \
                                     and p.payment_transaction_id.currency_id != p.currency_id \
                                     and p.state == 'draft' \
                                     and p.partner_type == 'customer' \
                                     and p.payment_type == 'inbound'):
            payment_different = payment._get_payment_transaction_diff()

            # if difference found, create exchange rate diff move
            if not payment.company_id.currency_id.is_zero(payment_different):
                # exchange rate profit/lost
                currency_conversion_diff_move_data = payment._prepare_currency_conversion_diff_move_data(payment_different)
                currency_conversion_diff_move = self.env['account.move'].create(currency_conversion_diff_move_data)
                currency_conversion_diff_move.action_post()

        res = super(AccountPayment, self).action_post()

        all_payment_lines = self.env['account.move.line'].search(self._get_unreconciled_payment_move_lines_domain())
        for payment in self:
            payment_lines = all_payment_lines.filtered(lambda aml: aml.payment_id == payment)

            diff_lines = payment_lines.filtered(lambda l: l.move_id.journal_id == l.company_id.currency_conversion_diff_journal_id)
            if diff_lines:
                # there is a chance the diff move has no ref because it is created and posted before the payment posted.
                # so, we will find it and update its ref here
                moves = diff_lines.move_id.filtered(lambda move: not move.ref or move.ref == '/')
                if moves:
                    moves.write({'ref': payment.name})

                if len(payment_lines) > 1:
                    payment_lines.reconcile()
        return res

    def action_cancel(self):
        for rec in self:
            rec.line_ids.remove_move_reconcile()
        return super(AccountPayment, self).action_cancel()
