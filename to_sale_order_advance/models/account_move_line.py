from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    @api.returns('self',
                 upgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value if count else self.browse(value),
                 downgrade=lambda self, value, args, offset=0, limit=None, order=None, count=False: value if count else value.ids)
    def search(self, args, offset=0, limit=None, order=None, count=False):
        advance_payment_sale_ids = self._context.get('advance_payment_sale_ids', False)
        if isinstance(advance_payment_sale_ids, list):
            domain = [
                '|', '|',
                ('payment_id.sale_order_ids', 'in', advance_payment_sale_ids),
                ('payment_id.sale_order_ids', '=', False),
                ('payment_id', '=', False),
            ]
            args = expression.AND([args, domain])
        return super(AccountMoveLine, self).search(args, offset, limit, order, count)

    def _prepare_reconciliation_partials(self):
        ''' Prepare the partials on the current journal items to perform the reconciliation.
        /!\ The order of records in self is important because the journal items will be reconciled using this order.
        :return: A recordset of account.partial.reconcile.
        '''
        # HACKING Odoo since there is no way to extend.
        amount = abs(self._context.get('force_amount', False))
        line_id = self._context.get('line_id', False)
        invoice_currency_id = self._context.get('invoice_currency_id', False)
        if not amount or not line_id or not invoice_currency_id:
            return super(AccountMoveLine, self)._prepare_reconciliation_partials()

        debit_lines = iter(self.filtered(lambda line: line.balance > 0.0 or line.amount_currency > 0.0))
        credit_lines = iter(self.filtered(lambda line: line.balance < 0.0 or line.amount_currency < 0.0))
        debit_line = None
        credit_line = None

        debit_amount_residual = 0.0
        debit_amount_residual_currency = 0.0
        credit_amount_residual = 0.0
        credit_amount_residual_currency = 0.0
        debit_line_currency = None
        credit_line_currency = None

        partials_vals_list = []

        while True:

            # Move to the next available debit line.
            if not debit_line:
                debit_line = next(debit_lines, None)
                if not debit_line:
                    break
                debit_amount_residual, debit_amount_residual_currency, debit_line_currency = debit_line._get_force_amount_of_line(line_id, amount, invoice_currency_id)

            # Move to the next available credit line.
            if not credit_line:
                credit_line = next(credit_lines, None)
                if not credit_line:
                    break
                credit_amount_residual, credit_amount_residual_currency, credit_line_currency = credit_line._get_force_amount_of_line(line_id, amount, invoice_currency_id)

            min_amount_residual = min(debit_amount_residual, -credit_amount_residual)
            has_debit_residual_left = not debit_line.company_currency_id.is_zero(debit_amount_residual) and debit_amount_residual > 0.0
            has_credit_residual_left = not credit_line.company_currency_id.is_zero(credit_amount_residual) and credit_amount_residual < 0.0
            has_debit_residual_curr_left = not debit_line_currency.is_zero(debit_amount_residual_currency) and debit_amount_residual_currency > 0.0
            has_credit_residual_curr_left = not credit_line_currency.is_zero(credit_amount_residual_currency) and credit_amount_residual_currency < 0.0

            if debit_line_currency == credit_line_currency:
                # Reconcile on the same currency.

                # The debit line is now fully reconciled because:
                # - either amount_residual & amount_residual_currency are at 0.
                # - either the credit_line is not an exchange difference one.
                if not has_debit_residual_curr_left and (has_credit_residual_curr_left or not has_debit_residual_left):
                    debit_line = None
                    continue

                # The credit line is now fully reconciled because:
                # - either amount_residual & amount_residual_currency are at 0.
                # - either the debit is not an exchange difference one.
                if not has_credit_residual_curr_left and (has_debit_residual_curr_left or not has_credit_residual_left):
                    credit_line = None
                    continue

                min_amount_residual_currency = min(debit_amount_residual_currency, -credit_amount_residual_currency)
                min_debit_amount_residual_currency = min_amount_residual_currency
                min_credit_amount_residual_currency = min_amount_residual_currency

            else:
                # Reconcile on the company's currency.

                # The debit line is now fully reconciled since amount_residual is 0.
                if not has_debit_residual_left:
                    debit_line = None
                    continue

                # The credit line is now fully reconciled since amount_residual is 0.
                if not has_credit_residual_left:
                    credit_line = None
                    continue

                min_debit_amount_residual_currency = credit_line.company_currency_id._convert(
                    min_amount_residual,
                    debit_line.currency_id,
                    credit_line.company_id,
                    credit_line.date,
                )
                min_credit_amount_residual_currency = debit_line.company_currency_id._convert(
                    min_amount_residual,
                    credit_line.currency_id,
                    debit_line.company_id,
                    debit_line.date,
                )

            debit_amount_residual -= min_amount_residual
            debit_amount_residual_currency -= min_debit_amount_residual_currency
            credit_amount_residual += min_amount_residual
            credit_amount_residual_currency += min_credit_amount_residual_currency

            partials_vals_list.append({
                'amount': min_amount_residual,
                'debit_amount_currency': min_debit_amount_residual_currency,
                'credit_amount_currency': min_credit_amount_residual_currency,
                'debit_move_id': debit_line.id,
                'credit_move_id': credit_line.id,
            })

        return partials_vals_list

    def reconcile(self):
        self._check_reconcile_with_so()
        if 'force_amount' in self._context and 'invoice_currency_id' in self._context:
            self = self.with_context(no_exchange_difference=True)
        return super(AccountMoveLine, self).reconcile()

    def _get_force_amount_of_line(self, line_id, amount, invoice_currency_id):
        self.ensure_one()
        company_currency = self.company_id.currency_id
        amount_residual = self.amount_residual
        amount_residual_currency = self.amount_residual_currency
        amount = amount if amount_residual > 0 else -amount
        if self.id == line_id:
            invoice_currency = self.env['res.currency'].browse(invoice_currency_id)
            if invoice_currency != company_currency:
                if self.currency_id and self.currency_id != invoice_currency:
                    amount_residual_currency = invoice_currency._convert(amount,
                                                                            self.currency_id,
                                                                            self.company_id,
                                                                            self.date or fields.Date.today())
                    amount_residual = self.currency_id._convert(amount_residual_currency,
                                                                company_currency,
                                                                self.company_id,
                                                                self.date or fields.Date.today())
                else:
                    amount_residual_currency = amount
                    amount_residual = (self.currency_id or invoice_currency)._convert(amount,
                                                                                      company_currency,
                                                                                      self.company_id,
                                                                                      self.date or fields.Date.today())
            else:
                amount_residual = amount
                amount_residual_currency = company_currency._convert(amount,
                                                                     self.currency_id,
                                                                     self.company_id,
                                                                     self.date or fields.Date.today())
        return amount_residual, amount_residual_currency, self.currency_id

    def _check_reconcile_with_so(self):
        inv_ids = self.move_id.filtered(lambda l: l.move_type == 'out_invoice')
        if not inv_ids:
            return

        # Check on every payment
        for aml in self:
            payment = aml.payment_id
            sale_orders = payment.sale_order_ids
            if payment and sale_orders:
                so_on_invoice = inv_ids.invoice_line_ids.sale_line_ids.order_id
                for so in so_on_invoice:
                    if so not in sale_orders:
                        raise UserError(_("You can not reconcile entries those belong to different sale orders."
                                          " Please add the sale order '%s' to the payment '%s' to reconcile.")
                                          % (so.name, payment.name))
