from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _recompute_payment_terms_lines(self):
        """ Hard code:
        Handling the case that the invoice has 2 lines, which are receivable or payable
        """
        if self.line_ids.filtered(lambda l: l.product_id and l.product_id.is_promotion_voucher):
            self.ensure_one()
            self = self.with_company(self.company_id)
            in_draft_mode = self != self._origin
            today = fields.Date.context_today(self)
            self = self.with_company(self.journal_id.company_id)

            def _get_payment_terms_computation_date(self):
                ''' Get the date from invoice that will be used to compute the payment terms.
                :param self:    The current account.move record.
                :return:        A datetime.date object.
                '''
                if self.invoice_payment_term_id:
                    return self.invoice_date or today
                else:
                    return self.invoice_date_due or self.invoice_date or today

            def _get_payment_terms_account(self, payment_terms_lines):
                ''' Get the account from invoice that will be set as receivable / payable account.
                :param self:                    The current account.move record.
                :param payment_terms_lines:     The current payment terms lines.
                :return:                        An account.account record.
                '''
                if payment_terms_lines:
                    # Retrieve account from previous payment terms lines in order to allow the user to set a custom one.
                    return payment_terms_lines[0].account_id
                elif self.partner_id:
                    # Retrieve account from partner.
                    if self.is_sale_document(include_receipts=True):
                        return self.partner_id.property_account_receivable_id
                    else:
                        return self.partner_id.property_account_payable_id
                else:
                    # Search new account.
                    domain = [
                        ('company_id', '=', self.company_id.id),
                        ('internal_type', '=', 'receivable' if self.move_type in ('out_invoice', 'out_refund', 'out_receipt') else 'payable'),
                    ]
                    return self.env['account.account'].search(domain, limit=1)

            def _compute_payment_terms(self, date, total_balance, total_amount_currency):
                ''' Compute the payment terms.
                :param self:                    The current account.move record.
                :param date:                    The date computed by '_get_payment_terms_computation_date'.
                :param total_balance:           The invoice's total in company's currency.
                :param total_amount_currency:   The invoice's total in invoice's currency.
                :return:                        A list <to_pay_company_currency, to_pay_invoice_currency, due_date>.
                '''
                if self.invoice_payment_term_id:
                    to_compute = self.invoice_payment_term_id.compute(total_balance, date_ref=date, currency=self.company_id.currency_id)
                    if self.currency_id == self.company_id.currency_id:
                        # Single-currency.
                        return [(b[0], b[1], b[1]) for b in to_compute]
                    else:
                        # Multi-currencies.
                        to_compute_currency = self.invoice_payment_term_id.compute(total_amount_currency, date_ref=date, currency=self.currency_id)
                        return [(b[0], b[1], ac[1]) for b, ac in zip(to_compute, to_compute_currency)]
                else:
                    return [(fields.Date.to_string(date), total_balance, total_amount_currency)]

            def _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute):
                ''' Process the result of the '_compute_payment_terms' method and creates/updates corresponding invoice lines.
                :param self:                    The current account.move record.
                :param existing_terms_lines:    The current payment terms lines.
                :param account:                 The account.account record returned by '_get_payment_terms_account'.
                :param to_compute:              The list returned by '_compute_payment_terms'.
                '''
                # As we try to update existing lines, sort them by due date.
                existing_terms_lines = existing_terms_lines.sorted(lambda line: line.date_maturity or today)
                existing_terms_lines_index = 0

                # Recompute amls: update existing line or create new one for each payment term.
                new_terms_lines = self.env['account.move.line']
                for date_maturity, balance, amount_currency in to_compute:
                    currency = self.journal_id.company_id.currency_id
                    if currency and currency.is_zero(balance) and len(to_compute) > 1:
                        continue

                    if existing_terms_lines_index < len(existing_terms_lines):
                        # Update existing line.
                        candidate = existing_terms_lines[existing_terms_lines_index]
                        existing_terms_lines_index += 1
                        candidate.update({
                            'date_maturity': date_maturity,
                            'amount_currency':-amount_currency,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                        })
                    else:
                        # Create new line.
                        create_method = in_draft_mode and self.env['account.move.line'].new or self.env['account.move.line'].create
                        candidate = create_method({
                            'name': self.payment_reference or '',
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'quantity': 1.0,
                            'amount_currency':-amount_currency,
                            'date_maturity': date_maturity,
                            'move_id': self.id,
                            'currency_id': self.currency_id.id,
                            'account_id': account.id,
                            'partner_id': self.commercial_partner_id.id,
                            'exclude_from_invoice_tab': True,
                        })
                    new_terms_lines += candidate
                    if in_draft_mode:
                        candidate.update(candidate._get_fields_onchange_balance(force_computation=True))
                return new_terms_lines

            existing_terms_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
            others_lines = self.line_ids.filtered(lambda line: line.account_id.user_type_id.type not in ('receivable', 'payable'))
            income_lines = existing_terms_lines.filtered(
                lambda line: (
                    line.product_id.property_account_income_id
                    and line.account_id.id == line.product_id.property_account_income_id.id
                )
                or (
                    line.product_id.categ_id.property_account_income_categ_id
                    and line.account_id.id
                    == line.product_id.categ_id.property_account_income_categ_id.id
                )
            )
            if income_lines:
                existing_terms_lines -= income_lines
                others_lines += income_lines
            company_currency_id = (self.company_id or self.env.company).currency_id
            total_balance = sum(others_lines.mapped(lambda l: company_currency_id.round(l.balance)))
            total_amount_currency = sum(others_lines.mapped('amount_currency'))

            if not others_lines:
                self.line_ids -= existing_terms_lines
                return

            computation_date = _get_payment_terms_computation_date(self)
            account = _get_payment_terms_account(self, existing_terms_lines)
            to_compute = _compute_payment_terms(self, computation_date, total_balance, total_amount_currency)
            new_terms_lines = _compute_diff_payment_terms_lines(self, existing_terms_lines, account, to_compute)

            # Remove old terms lines that are no longer needed.
            self.line_ids -= existing_terms_lines - new_terms_lines
            if new_terms_lines:
                self.payment_reference = new_terms_lines[-1].name or ''
                self.invoice_date_due = new_terms_lines[-1].date_maturity
        else:
            super(AccountMove, self)._recompute_payment_terms_lines()
