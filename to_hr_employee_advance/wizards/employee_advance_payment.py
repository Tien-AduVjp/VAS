from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class employee_advance_payment(models.TransientModel):
    _name = 'employee.advance.payment'
    _description = 'Employee Advance Payment'

    @api.model
    def _default_journal_id(self):
        company_id = self._context.get('company_id', self.env.company.id)
        domain = [
            ('type', 'in', ('cash', 'bank')),
            ('company_id', '=', company_id),
            ('code', '!=', 'EAJ')
        ]
        return self.env['account.journal'].search(domain, limit=1)

    emp_advance_id = fields.Many2one('employee.advance', string='Employee Advance')
    payment_date = fields.Date(string='Payment Date', required=True, default=fields.Date.today)
    journal_id = fields.Many2one('account.journal', string='Payment Method', required=True,
                                 domain=[('type', 'in', ('cash', 'bank'))], default=_default_journal_id)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    outbound_payment_method_ids = fields.Many2many(related='journal_id.outbound_payment_method_ids', string='Outbound Payment Methods')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True,
                                        domain="[('payment_type', '=', 'outbound'), ('id', 'in', outbound_payment_method_ids)]",
                                        compute='_compute_payment_method', readonly=False)
    hide_payment_method = fields.Boolean(compute='_compute_payment_method', string='Hide Payment Method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, readonly=True, required=True)
    ref = fields.Char(string='Memo')
    employee_advance_reconcile_id = fields.Many2one('employee.advance.reconcile', string='Employee Advance Reconcile')

    @api.depends('journal_id')
    def _compute_payment_method(self):
        for r in self:
            if r.journal_id:
                # Set default payment method (we consider the first to be the default one)
                payment_methods = r.journal_id.outbound_payment_method_ids
                journal_payment_methods = r.journal_id.outbound_payment_method_ids
                r.payment_method_id = payment_methods and payment_methods[0] or False
                r.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'
            else:
                r.payment_method_id =  r.payment_method_id
                r.hide_payment_method = r.hide_payment_method

    @api.onchange('emp_advance_id')
    def _onchange_emp_advance_id(self):
        if self.emp_advance_id:
            self.currency_id = self.emp_advance_id.currency_id
            self.amount = self.emp_advance_id.balance
            self.ref = self.emp_advance_id.name

    @api.onchange('employee_advance_reconcile_id')
    def _onchange_emp_advance_reconcile_id(self):
        if self.employee_advance_reconcile_id:
            ######### START MONKEY PATCHING ##############
            # Since Odoo recalls computing for the code field,
            # we must query the value from the database instead of employee_advance_reconcile_id.balance
            # see the issue https://github.com/odoo/odoo/issues/25169
            self.env.cr.execute("SELECT balance FROM employee_advance_reconcile WHERE id=%s", (self.employee_advance_reconcile_id.id,))
            row = self.env.cr.fetchone()
            self.amount = row[0]
            ######### END MONKEY PATCHING ##############
            # The line below should be uncommented when the issue a.m. is solve
            # self.amount = self.employee_advance_reconcile_id.balance
            self.ref = self.employee_advance_reconcile_id.name

    @api.constrains('amount')
    def _check_amount(self):
        precision = self.env['decimal.precision'].precision_get('Account')
        if any(r.emp_advance_id and float_compare(r.amount, r.emp_advance_id.balance, precision_digits=precision) == 1 for r in self):
            raise ValidationError(_('The amount exceeds the allowable limit of the advance request.'))
        if any(r.employee_advance_reconcile_id and float_compare(r.amount, r.employee_advance_reconcile_id.balance, precision_digits=precision) == 1 for r in self):
            raise ValidationError(_('The amount exceeds the allowable limit.'))

    def _prepare_payment_vals(self):
        if self.emp_advance_id:
            return {
                'partner_type': 'employee',
                'payment_type': 'outbound',
                'employee_id': self.emp_advance_id.employee_id.id,
                'partner_id': self.emp_advance_id.employee_id.sudo().address_home_id.id,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'payment_method_id': self.payment_method_id.id,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'date': self.payment_date,
                'ref': self.ref,
                'employee_advance_id': self.emp_advance_id.id
            }
        elif self.employee_advance_reconcile_id:
            payment_type = self.employee_advance_reconcile_id.difference_amount > 0 and 'inbound' or 'outbound'
            return {
                'partner_type': 'employee',
                'payment_type': payment_type,
                'employee_id': self.employee_advance_reconcile_id.employee_id.id,
                'partner_id': self.employee_advance_reconcile_id.employee_id.sudo().address_home_id.id,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'payment_method_id': self.payment_method_id.id,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'date': self.payment_date,
                'ref': self.ref,
                'employee_advance_reconcile_id': self.employee_advance_reconcile_id.id
            }

    def action_pay(self):
        self.ensure_one()
        if self.emp_advance_id:
            if not self.emp_advance_id.employee_id.sudo().address_home_id:
                raise UserError(_("You must configure Private Address for employee %s.") % self.emp_advance_id.employee_id.name)
        elif self.employee_advance_reconcile_id:
            if not self.employee_advance_reconcile_id.employee_id.sudo().address_home_id:
                raise UserError(_("You must configure Private Address for employee %s.") % self.employee_advance_reconcile_id.employee_id.name)
        # Create payment and post it
        payment = self.env['account.payment'].create(self._prepare_payment_vals())
        payment.action_post()
        return {'type': 'ir.actions.act_window_close'}
