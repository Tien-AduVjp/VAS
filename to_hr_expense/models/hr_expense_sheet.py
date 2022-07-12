from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.model
    def _default_journal_id(self):
        default_company_id = self.default_get(['company_id'])['company_id']
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('code', '=', 'EXJ'),
            ('company_id', '=', default_company_id)], limit=1)
        if journal:
            return journal.id
        else:
            return super(HrExpenseSheet, self)._default_journal_id()

    @api.model
    def _default_vendor_bill_journal_id(self):
        """
        The journal is determining the company of the vendor bill generated from expense.
        """
        default_company_id = self.default_get(['company_id'])['company_id']
        journal = self.env['account.journal'].search([
            ('type', '=', 'purchase'),
            ('company_id', '=', default_company_id)], limit=1)
        return journal.id

    payment_ids = fields.One2many('account.payment', 'expense_sheet_id', string='Payments', groups='account.group_account_user')
    payments_count = fields.Integer(string='Payments Count', groups='account.group_account_user', compute='_compute_payments_count')
    # TODO: this field is deprecated, remove in master/15+
    aggregate_payments = fields.Boolean(string='Lump-sum Payment?', default=True,
        help="If checked, in case this expense sheet was paid by company,"
        " all expense lines of this sheet will be paid by one single payment.")
    move_ids = fields.One2many('account.move', 'hr_expense_sheet_id', string='Journal Entries', groups='account.group_account_user', readonly=True)
    move_count = fields.Integer(string='Journal Entries Count', groups='account.group_account_user', compute='_compute_move_count')
    has_invoice = fields.Boolean(string="Has Invoice", compute='_compute_has_invoice', store=True)
    vendor_bill_journal_id = fields.Many2one('account.journal', string='Vendor Bill Journal',
        states={'done': [('readonly', True)], 'post': [('readonly', True)]}, check_company=True,
        domain="[('type', '=', 'purchase'), ('company_id', '=', company_id)]",
        default=_default_vendor_bill_journal_id, help="The journal used when the expense sheet has invoice.")

    journal_id = fields.Many2one(default=_default_journal_id)

    # Override state to change string Paid to Done.
    # TODO: remove in 15.0 because it resolved from 15.0
    # Ref. https://github.com/odoo/odoo/pull/65528
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Done'),
        ('cancel', 'Refused')
    ])
    # Override compute amount_residual because we use move_ids instead of account_move_id.
    amount_residual = fields.Monetary(
        string="Amount Due", store=True,
        currency_field='currency_id',
        compute='_compute_amount_residual', compute_sudo=True)

    # Override compute payment_state (in 15.0) because we use move_ids instead of account_move_id.
    # Ref. https://github.com/odoo/odoo/pull/65528
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
    ], string="Payment Status", store=True, readonly=True, copy=False, tracking=True, compute='_compute_payment_state', compute_sudo=True)

    # TODO: rename this field to invisible_payment in v15
    is_paid = fields.Boolean(string='Is Paid', copy=False, compute='_compute_is_paid', store=True, help="Technical field is used to show/hide button Payment")

    @api.depends('move_ids')
    def _compute_move_count(self):
        move_data = self.env['account.move'].read_group([('hr_expense_sheet_id', 'in', self.ids)], ['hr_expense_sheet_id'], ['hr_expense_sheet_id'])
        mapped_data = dict([(dict_data['hr_expense_sheet_id'][0], dict_data['hr_expense_sheet_id_count']) for dict_data in move_data])
        for r in self:
            r.move_count = mapped_data.get(r.id, 0)

    @api.depends('payment_ids')
    def _compute_payments_count(self):
        payment_data = self.env['account.payment'].read_group([('expense_sheet_id', 'in', self.ids)], ['expense_sheet_id'], ['expense_sheet_id'])
        mapped_data = dict([(dict_data['expense_sheet_id'][0], dict_data['expense_sheet_id_count']) for dict_data in payment_data])
        for r in self:
            r.payments_count = mapped_data.get(r.id, 0)

    @api.depends('expense_line_ids', 'expense_line_ids.to_invoice')
    def _compute_has_invoice(self):
        for r in self:
            has_invoice = False
            if any(expense.to_invoice for expense in r.expense_line_ids):
                has_invoice = True
            r.has_invoice = has_invoice

    @api.depends(
        'currency_id',
        'move_ids.line_ids.amount_residual',
        'move_ids.line_ids.amount_residual_currency',
        'move_ids.line_ids.account_internal_type',)
    def _compute_amount_residual(self):
        for r in self:
            if r.currency_id == r.company_id.currency_id:
                residual_field = 'amount_residual'
            else:
                residual_field = 'amount_residual_currency'

            domain = r._prepare_amount_residual_domain()
            payment_term_lines = r.move_ids.line_ids.filtered_domain(domain)
            r.amount_residual = -sum(payment_term_lines.mapped(residual_field))

    def _compute_is_paid(self):
        for r in self:
            r.is_paid = False

    @api.depends('state', 'amount_residual', 'total_amount')
    def _compute_payment_state(self):
        for r in self:
            payment_state = 'not_paid'
            if r.state in ('post', 'done'):
                if r.currency_id.is_zero(r.amount_residual):
                    payment_state = 'paid'
                elif r.currency_id.compare_amounts(r.total_amount, r.amount_residual) != 0:
                    payment_state = 'partial'
            r.payment_state = payment_state

    def _prepare_amount_residual_domain(self):
        self.ensure_one()
        return [
            ('account_internal_type', 'in',('receivable', 'payable')),
            ('parent_state', '=', 'posted')
        ]

    def action_sheet_move_create(self):
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        for move in res.values():
            payments = move.line_ids.payment_id
            expense_sheets = self.filtered(lambda x: x.account_move_id == move)
            if expense_sheets:
                payments.write({'expense_sheet_id': expense_sheets[0].id})
        self.filtered(lambda sheet: sheet.has_invoice and sheet.state == 'done').write({'state': 'post'})
        self.generate_payable_transfer_move()
        return res

    def generate_payable_transfer_move(self):
        """
        Create account move to transfer vendor payable to employee payable
        """
        for r in self.filtered_domain([('has_invoice', '=', True), ('payment_mode', '=', 'own_account')]):
            for bill in r.move_ids.filtered_domain([
                    ('move_type', '=', 'in_invoice'),
                    ('state', '=', 'posted'),
                ]):
                transfer_move = r._create_payable_transfer_move(bill)
                transfer_move._post()
                r._reconcile_transfer_payable_move(transfer_move, bill)

    def _create_payable_transfer_move(self, bill):
        self.ensure_one()
        vals = self._prepare_transfer_payable_move_vals(bill)
        return self.env['account.move'].with_context(default_journal_id=vals['journal_id']).create(vals)

    def _prepare_transfer_payable_move_vals(self, bill):
        self.ensure_one()
        bill_payable_lines = bill.line_ids.filtered_domain([('account_internal_type', '=', 'payable')])
        if not bill_payable_lines:
            return {}
        res = {
            'journal_id': self.journal_id.id,
            'company_id': self.company_id.id,
            'date': self.accounting_date or bill.date or fields.Date.context_today(self),
            'ref': self.name,
            'name': '/',
            'move_type': 'entry',
            'hr_expense_sheet_id': self.id,
            'line_ids': [(0, 0, line_vals) for line_vals in self._prepare_transfer_payable_move_line_vals_list(bill_payable_lines)]
        }
        return res

    def _prepare_transfer_payable_move_line_vals_list(self, bill_payable_lines):
        self.ensure_one()
        line_vals_list = []
        for line in bill_payable_lines:
            line_vals_list.append(self._prepare_vendor_line_vals(line))
            line_vals_list.append(self._prepare_employee_line_vals(line))
        return line_vals_list

    def _prepare_vendor_line_vals(self, bill_payable_line):
        res = {
            'name': self.name,
            'date_maturity': self.accounting_date or bill_payable_line.move_id.date or fields.Date.context_today(self),
            'amount_currency': bill_payable_line.amount_currency,
            'currency_id': bill_payable_line.currency_id.id,
            'debit': bill_payable_line.credit,
            'credit': 0.0,
            'partner_id': bill_payable_line.partner_id.id,
            'account_id': bill_payable_line.account_id.id,
            'expense_id': bill_payable_line.expense_id.id,
            'exclude_from_invoice_tab': True
        }
        return res

    def _prepare_employee_line_vals(self, bill_payable_line):
        res = {
            'name': self.name,
            'date_maturity': self.accounting_date or bill_payable_line.move_id.date or fields.Date.context_today(self),
            'amount_currency': bill_payable_line.amount_currency,
            'currency_id': bill_payable_line.currency_id.id,
            'debit': 0.0,
            'credit': bill_payable_line.credit,
            'partner_id': self.employee_id.sudo().address_home_id.id,
            'account_id': self.employee_id.sudo().address_home_id.property_account_payable_id.id,
            'expense_id': bill_payable_line.expense_id.id,
            'exclude_from_invoice_tab': False
        }
        return res

    def _reconcile_transfer_payable_move(self, transfer_move, bill):
        domain = [('account_internal_type', 'in', ('receivable', 'payable')), ('reconciled', '=', False)]
        transfer_move_lines = transfer_move.line_ids.filtered_domain(domain)
        to_reconcile_move_lines = bill.line_ids.filtered_domain(domain)
        for account in transfer_move_lines.account_id:
            (transfer_move_lines + to_reconcile_move_lines)\
                .filtered_domain([
                    ('account_id', '=', account.id),
                    ('reconciled', '=', False),
                    ('move_id.state', '=', 'posted'),
                ]).reconcile()

    def action_view_payments(self):
        result = self.env['ir.actions.actions']._for_xml_id('account.action_account_payments_payable')
        if self.payments_count != 1:
            result['domain'] = "[('expense_sheet_id', 'in', %s)]" % str(self.ids)
        elif self.payments_count == 1:
            res = self.env.ref('account.view_account_payment_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.payment_ids.id
        return result

    def action_view_moves(self):
        result = self.env['ir.actions.actions']._for_xml_id('to_hr_expense.expense_entry_action')
        if self.move_count != 1:
            result['domain'] = "[('hr_expense_sheet_id', 'in', %s)]" % str(self.ids)
        elif self.move_count == 1:
            res = self.env.ref('account.view_move_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.move_ids.id
        return result

    def action_submit_sheet(self):
        """
        check lines: partner, to_invoice on all lines are the same
        """
        for r in self:
            invoice = r.expense_line_ids.filtered(lambda x: x.to_invoice)
            if invoice and invoice != r.expense_line_ids:
                raise ValidationError(_("Expenditures must be set to the same 'Create Invoice?' value (either billed or invoiced)"))

        super(HrExpenseSheet, self).action_submit_sheet()

    def action_cancel(self):
        self._check_state_moves_and_payments()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.expense.refuse.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'hr_expense_refuse_model':'hr.expense.sheet'}
        }

    def unlink(self):
        for r in self:
            if r.sudo().move_ids or r.sudo().payment_ids:
                raise UserError(_("You cannot delete the expense '%s' which has been posted once entry !") % (r.name))
        return super(HrExpenseSheet, self).unlink()

    def _check_state_moves_and_payments(self):
        for r in self:
            moves = r.sudo().move_ids.filtered(lambda m: m.state != 'cancel')
            payments = r.sudo().payment_ids.filtered(lambda m: m.state != 'cancel')
            if moves or payments:
                raise UserError(_("You must cancel all invoices and payments of the expense sheet,"
                                  " before you reset to draft or cancel that expense sheet '%s'") % (r.name))
        return True

    def reset_expense_sheets(self):
        res = super(HrExpenseSheet, self).reset_expense_sheets()
        if res:
            self._check_state_moves_and_payments()
        return res

    def action_register_payment(self):
        res = super(HrExpenseSheet, self).action_register_payment()
        context = res.get('context', False)
        if context and self.sudo().move_ids:
            context.update({
                'expense_ids': self.ids,
                'active_model': 'account.move.line',
                'active_ids': self.sudo().move_ids.line_ids.filtered_domain([
                    ('account_internal_type', '=', 'payable'),
                    ('amount_residual', '!=', 0),
                    ('move_id.state', '=', 'posted')
                ]).ids
            })
            res.update({
                'context': context
            })
        return res
