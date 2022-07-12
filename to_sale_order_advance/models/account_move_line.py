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

    def _reconcile_lines(self, debit_moves, credit_moves, field):
        """ This function loops on the 2 recordsets given as parameter as long as it
            can find a debit and a credit to reconcile together. It returns the recordset of the
            account move lines that were not reconciled during the process.
        """
        amount = abs(self._context.get('force_amount', False))
        line_id = self._context.get('line_id', False)
        invoice_currency_id = self._context.get('invoice_currency_id', False)
        if not amount or not line_id or not invoice_currency_id:
            return super(AccountMoveLine, self)._reconcile_lines(debit_moves, credit_moves, field)

        (debit_moves + credit_moves).read([field])
        to_create = []
        cash_basis = debit_moves and debit_moves[0].account_id.internal_type in ('receivable', 'payable') or False
        cash_basis_percentage_before_rec = {}
        dc_vals ={}
        while (debit_moves and credit_moves):
            debit_move = debit_moves[0]
            credit_move = credit_moves[0]
            company_currency = debit_move.company_id.currency_id
            # We need those temporary value otherwise the computation might be wrong below
            debit_amount_residual, debit_amount_residual_currency = debit_move._get_force_amount_of_line(line_id, amount, invoice_currency_id)
            credit_amount_residual, credit_amount_residual_currency = credit_move._get_force_amount_of_line(line_id, amount, invoice_currency_id)

            temp_amount_residual = min(debit_amount_residual, credit_amount_residual)
            temp_amount_residual_currency = min(debit_amount_residual_currency, credit_amount_residual_currency)
            dc_vals[(debit_move.id, credit_move.id)] = (debit_move, credit_move, temp_amount_residual_currency)

            if field == 'amount_residual':
                amount_reconcile = min(debit_amount_residual, credit_amount_residual)
            else:
                amount_reconcile = min(debit_amount_residual_currency, credit_amount_residual_currency)

            #Remove from recordset the one(s) that will be totally reconciled
            # For optimization purpose, the creation of the partial_reconcile are done at the end,
            # therefore during the process of reconciling several move lines, there are actually no recompute performed by the orm
            # and thus the amount_residual are not recomputed, hence we have to do it manually.
            if amount_reconcile == debit_move[field] or debit_move.id == line_id:
                debit_moves -= debit_move
            else:
                debit_moves[0].amount_residual -= temp_amount_residual
                debit_moves[0].amount_residual_currency -= temp_amount_residual_currency

            if amount_reconcile == -credit_move[field] or credit_move.id == line_id:
                credit_moves -= credit_move
            else:
                credit_moves[0].amount_residual += temp_amount_residual
                credit_moves[0].amount_residual_currency += temp_amount_residual_currency
            #Check for the currency and amount_currency we can set
            currency = False
            amount_reconcile_currency = 0
            if field == 'amount_residual_currency':
                currency = credit_move.currency_id.id
                amount_reconcile_currency = temp_amount_residual_currency
                amount_reconcile = temp_amount_residual
            elif bool(debit_move.currency_id) != bool(credit_move.currency_id):
                # If only one of debit_move or credit_move has a secondary currency, also record the converted amount
                # in that secondary currency in the partial reconciliation. That allows the exchange difference entry
                # to be created, in case it is needed. It also allows to compute the amount residual in foreign currency.
                currency = debit_move.currency_id or credit_move.currency_id
                currency_date = debit_move.currency_id and credit_move.date or debit_move.date
                amount_reconcile_currency = company_currency._convert(amount_reconcile, currency, debit_move.company_id, currency_date)
                currency = currency.id

            if cash_basis:
                tmp_set = debit_move | credit_move
                cash_basis_percentage_before_rec.update(tmp_set._get_matched_percentage())

            to_create.append({
                'debit_move_id': debit_move.id,
                'credit_move_id': credit_move.id,
                'amount': amount_reconcile,
                'amount_currency': amount_reconcile_currency,
                'currency_id': currency,
            })

        cash_basis_subjected = []
        part_rec = self.env['account.partial.reconcile']
        for partial_rec_dict in to_create:
            debit_move, credit_move, amount_residual_currency = dc_vals[partial_rec_dict['debit_move_id'], partial_rec_dict['credit_move_id']]
            # /!\ NOTE: Exchange rate differences shouldn't create cash basis entries
            # i. e: we don't really receive/give money in a customer/provider fashion
            # Since those are not subjected to cash basis computation we process them first
            if not amount_residual_currency and debit_move.currency_id and credit_move.currency_id:
                part_rec.create(partial_rec_dict)
            else:
                cash_basis_subjected.append(partial_rec_dict)

        for after_rec_dict in cash_basis_subjected:
            new_rec = part_rec.create(after_rec_dict)
            # if the pair belongs to move being reverted, do not create CABA entry
            if cash_basis and not (
                    new_rec.debit_move_id.move_id == new_rec.credit_move_id.move_id.reversed_entry_id
                    or
                    new_rec.credit_move_id.move_id == new_rec.debit_move_id.move_id.reversed_entry_id
            ):
                new_rec.create_tax_cash_basis_entry(cash_basis_percentage_before_rec)
        return debit_moves+credit_moves

    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        if 'force_amount' in self._context:
            self = self.with_context(no_exchange_difference=True)
        return super(AccountMoveLine, self).reconcile(writeoff_acc_id=writeoff_acc_id, writeoff_journal_id=writeoff_journal_id)

    def _get_force_amount_of_line(self, line_id, amount, invoice_currency_id):
        self.ensure_one()
        company_currency = self.company_id.currency_id
        amount_residual = abs(self.amount_residual)
        amount_residual_currency = abs(self.amount_residual_currency)
        if self.id == line_id:
            invoice_currency = self.env['res.currency'].browse(invoice_currency_id)
            if invoice_currency != company_currency:
                if self.currency_id and self.currency_id != invoice_currency:
                    amount_residual_currency = invoice_currency._convert(
                        amount,
                        self.currency_id,
                        self.company_id,
                        self.date or fields.Date.today()
                        )
                    amount_residual = self.currency_id._convert(
                        amount_residual_currency,
                        company_currency,
                        self.company_id,
                        self.date or fields.Date.today()
                        )
                else:
                    amount_residual_currency = amount
                    amount_residual = (self.currency_id or invoice_currency)._convert(
                        amount,
                        company_currency,
                        self.company_id,
                        self.date or fields.Date.today()
                        )
            else:
                amount_residual = amount
                amount_residual_currency = company_currency._convert(
                    amount,
                    self.currency_id,
                    self.company_id,
                    self.date or fields.Date.today()
                    )
        return amount_residual, amount_residual_currency

    def _check_reconcile_validity(self):
        super(AccountMoveLine, self)._check_reconcile_validity()
        inv_ids = self.filtered(lambda l: l.move_id.type == 'out_invoice').mapped('move_id')
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
