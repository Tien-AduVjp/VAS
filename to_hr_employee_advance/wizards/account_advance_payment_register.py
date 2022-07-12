from odoo import fields, models, api, _
from odoo.exceptions import UserError

class AccountAdvancePaymentRegister(models.TransientModel):
    _name = 'account.advance.payment.register'
    _description = "Account Employee Advance Payment Register"

    # == Business fields ==
    payment_date = fields.Date(string="Payment Date", required=True,
        default=fields.Date.context_today)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
        compute='_compute_employee_id', store=True, readonly=False)
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=False,
        compute='_compute_amount')
    communication = fields.Char(string="Memo", store=True, readonly=False,
        compute='_compute_from_lines')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id',
        help="The payment's currency.")
    journal_id = fields.Many2one('account.journal', store=True, readonly=False,
        compute='_compute_journal_id',
        domain="[('company_id', '=', company_id), ('is_advance_journal', '=', True)]")
    company_currency_id = fields.Many2one('res.currency', string="Company Currency",
        related='company_id.currency_id')

    # == Fields given through the context ==
    line_ids = fields.Many2many('account.move.line', 'account_advance_payment_register_move_line_rel', 'wizard_id', 'line_id',
        string="Journal items", readonly=True, copy=False,)
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
    ], string='Payment Type', store=True, copy=False,
        compute='_compute_from_lines')
    company_id = fields.Many2one('res.company', store=True, copy=False,
        compute='_compute_from_lines')
    partner_id = fields.Many2one('res.partner',
        string="Customer/Vendor", store=True, copy=False, ondelete='restrict',
        compute='_compute_from_lines')
    source_amount = fields.Monetary(
        string="Amount to Pay (company currency)", store=True, copy=False,
        currency_field='company_currency_id',
        compute='_compute_from_lines')
    source_amount_currency = fields.Monetary(
        string="Amount to Pay (foreign currency)", store=True, copy=False,
        currency_field='source_currency_id',
        compute='_compute_from_lines')
    source_currency_id = fields.Many2one('res.currency',
        string='Source Currency', store=True, copy=False,
        compute='_compute_from_lines',
        help="The payment's currency.")
    destination_account_id = fields.Many2one('account.account',
        string='Receivable / Payable', store=True, copy=False,
        compute='_compute_from_lines')

    # == Payment difference fields ==
    payment_difference = fields.Monetary(
        compute='_compute_payment_difference')
    payment_difference_handling = fields.Selection([
        ('open', 'Keep open'),
        ('reconcile', 'Mark as fully paid'),
    ], default='open', string="Payment Difference Handling")
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", copy=False,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
    writeoff_label = fields.Char(string='Journal Item Label', default='Write-Off',
        help='Change label of the counterpart that will hold the payment difference')

    @api.model
    def default_get(self, fields_list):
        # OVERRIDE
        res = super().default_get(fields_list)

        if 'line_ids' in fields_list and 'line_ids' not in res:

            # Retrieve moves to pay from the context.

            if self._context.get('active_model') == 'account.move':
                lines = self.env['account.move'].browse(self._context.get('active_ids', [])).line_ids
            elif self._context.get('active_model') == 'account.move.line':
                lines = self.env['account.move.line'].browse(self._context.get('active_ids', []))
            else:
                raise UserError(_(
                    "The register advance payment wizard should only be called on journal entry record."
                ))

            # Keep lines having a residual amount to pay.
            available_lines = self.env['account.move.line']
            for line in lines:
                if line.move_id.state != 'posted':
                    raise UserError(_("You can only register advance payment for posted journal entries."))

                if line.account_internal_type not in ('receivable', 'payable'):
                    continue
                if line.currency_id:
                    if line.currency_id.is_zero(line.amount_residual_currency):
                        continue
                else:
                    if line.company_currency_id.is_zero(line.amount_residual):
                        continue
                available_lines |= line

            # Check.
            if not available_lines:
                raise UserError(_("You can't register a advance payment because there is nothing left to pay on the selected journal items."))
            if len(lines.company_id) > 1:
                raise UserError(_("You can't create advance payments for entries belonging to different companies."))

            res['line_ids'] = [(6, 0, available_lines.ids)]

        return res

    @api.depends('journal_id')
    def _compute_employee_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        for r in self:
            if r.journal_id and r.journal_id.is_advance_journal:
                r.employee_id = employee_id

    @api.depends('source_amount', 'source_amount_currency', 'source_currency_id', 'company_id', 'currency_id', 'payment_date')
    def _compute_amount(self):
        for r in self:
            if r.source_currency_id == r.currency_id:
                # Same currency.
                r.amount = r.source_amount_currency
            elif r.currency_id == r.company_id.currency_id:
                # Payment expressed on the company's currency.
                r.amount = r.source_amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = r.company_id.currency_id._convert(r.source_amount, r.currency_id, r.company_id, r.payment_date)
                r.amount = amount_payment_currency

    @api.depends('company_id')
    def _compute_journal_id(self):
        for r in self:
            r.journal_id = self.env['account.journal'].search([
                ('is_advance_journal', '=', 'True'),
                ('company_id', '=', r.company_id.id),
            ], limit=1)

    @api.depends('line_ids')
    def _compute_from_lines(self):
        ''' Load initial values from the account.move passed through the context. '''
        for r in self:
            lines = r.line_ids._origin
            company = lines[0].company_id
            currency_id = lines[0].currency_id
            source_amount = abs(sum(lines.mapped('amount_residual')))
            if currency_id == company.currency_id:
                source_amount_currency = source_amount
            else:
                source_amount_currency = abs(sum(lines.mapped('amount_residual_currency')))
            communication = set(line.name or line.move_id.ref or line.move_id.name for line in lines)
            r.update({
                'company_id': company.id,
                'partner_id': lines[0].partner_id,
                'source_currency_id': currency_id.id,
                'source_amount': source_amount,
                'source_amount_currency': source_amount_currency,
                'communication': ' '.join(sorted(communication)),
                'payment_type': 'inbound' if lines[0].balance > 0.0 else 'outbound',
                'destination_account_id': lines[0].account_id.id
            })

    @api.depends('journal_id')
    def _compute_currency_id(self):
        for r in self:
            r.currency_id = r.journal_id.currency_id or r.source_currency_id or r.company_id.currency_id

    @api.depends('amount')
    def _compute_payment_difference(self):
        for r in self:
            if r.source_currency_id == r.currency_id:
                # Same currency.
                r.payment_difference = r.source_amount_currency - r.amount
            elif r.currency_id == r.company_id.currency_id:
                # Payment expressed on the company's currency.
                r.payment_difference = r.source_amount - r.amount
            else:
                # Foreign currency on payment different than the one set on the journal entries.
                amount_payment_currency = r.company_id.currency_id._convert(r.source_amount, r.currency_id, r.company_id, r.payment_date)
                r.payment_difference = amount_payment_currency - r.amount

    def action_create_advance_journal_entries(self):
        self.ensure_one()
        advance_move = self._create_advance_move()
        advance_move._post()
        self._reconcile_advance_payments(advance_move)
        return advance_move

    def _create_advance_move(self):
        move_vals = self._prepare_move_vals()
        move = self.env['account.move'].with_context(default_journal_id=move_vals['journal_id']).create(move_vals)
        return move

    def _reconcile_advance_payments(self, advance_move):
        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
        advance_move_line = advance_move.line_ids.filtered_domain(domain)
        to_reconcile_move_line = self.line_ids.filtered_domain(domain)
        for account in advance_move_line.account_id:
            (advance_move_line + to_reconcile_move_line)\
                .filtered_domain([('account_id', '=', account.id), ('reconciled', '=', False)])\
                .reconcile()

    def _prepare_move_vals(self):
        self.ensure_one()

        write_off_line_vals = {}
        if not self.currency_id.is_zero(self.payment_difference) and self.payment_difference_handling == 'reconcile':
            write_off_line_vals = {
                'name': self.writeoff_label,
                'amount': self.payment_difference,
                'account_id': self.writeoff_account_id.id,
            }
        res = {
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'date': self.payment_date,
            'ref': self.communication,
            'name': '/',
            'move_type': 'entry',
            'line_ids': [(0, 0, line_vals) for line_vals in self._prepare_move_line_vals_list(write_off_line_vals=write_off_line_vals)]
        }
        return res

    def _prepare_move_line_vals_list(self, write_off_line_vals):
        self.ensure_one()
        if not self.employee_id.property_advance_account_id:
            raise UserError(_("Cannot find Advance Account for Employee '%s'. Please define it before register advance payment.") % self.employee_id.name)

        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            advance_amount_currency = self.amount
        else:
            # Send money.
            advance_amount_currency = -self.amount
            write_off_amount_currency *= -1

        write_off_balance = self.currency_id._convert(
            write_off_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.payment_date,
        )
        advance_balance = self.currency_id._convert(
            advance_amount_currency,
            self.company_id.currency_id,
            self.company_id,
            self.payment_date,
        )

        counterpart_amount_currency = -advance_amount_currency - write_off_amount_currency
        counterpart_balance = -advance_balance - write_off_balance

        line_vals_list = [
            # Advance line.
            self._prepare_advance_move_line_vals(advance_amount_currency, advance_balance),
            # Receivable / Payable.
            self._prepare_destination_move_line_vals(counterpart_amount_currency, counterpart_balance),
        ]

        if not self.currency_id.is_zero(write_off_amount_currency):
            # Write-off line.
            line_vals_list.append(self._prepare_write_off_line_vals(write_off_line_vals, write_off_amount_currency, write_off_balance))

        return line_vals_list

    def _prepare_advance_move_line_vals(self, advance_amount_currency, advance_balance):
        res = {
            'name': self.communication,
            'date_maturity': self.payment_date,
            'amount_currency': advance_amount_currency,
            'currency_id': self.currency_id.id,
            'debit': advance_balance if advance_balance > 0.0 else 0.0,
            'credit': -advance_balance if advance_balance < 0.0 else 0.0,
            'partner_id': self.employee_id.sudo().address_home_id.id,
            'account_id': self.employee_id.property_advance_account_id.id,
        }
        return res

    def _prepare_destination_move_line_vals(self, counterpart_amount_currency, counterpart_balance):
        res = {
            'name': self.communication,
            'date_maturity': self.payment_date,
            'amount_currency': counterpart_amount_currency,
            'currency_id': self.currency_id.id,
            'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
            'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.destination_account_id.id,
        }
        return res

    def _prepare_write_off_line_vals(self, write_off_line_vals, write_off_amount_currency, write_off_balance):
        res = {
            'name': write_off_line_vals.get('name'),
            'amount_currency': write_off_amount_currency,
            'currency_id': self.currency_id.id,
            'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
            'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
            'partner_id': self.partner_id.id,
            'account_id': write_off_line_vals.get('account_id'),
        }
        return res
