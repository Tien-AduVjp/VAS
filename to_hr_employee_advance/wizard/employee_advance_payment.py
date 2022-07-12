from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class employee_advance_payment(models.TransientModel):
    _name = 'employee.advance.payment'
    _description = 'Employee Advance Payment'

    @api.model
    def _get_default_journal(self):
        company_id = self._context.get('company_id', self.env.company.id)
        domain = [
            ('type', 'in', ('cash', 'bank')),
            ('company_id', '=', company_id),
            ('code', '!=', 'EAJ')
        ]
        return self.env['account.journal'].search(domain, limit=1)

    emp_advance_id = fields.Many2one('employee.advance', string="Employee Advance")
    payment_date = fields.Date(string="Payment Date", required=True, default=fields.Date.today)
    journal_id = fields.Many2one('account.journal', string="Payment Method",
                                 required=True, domain=[('type', 'in', ('cash', 'bank')), ('is_advance_journal', '=', False)], default=_get_default_journal)
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True, required=True)
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Type', required=True)
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id, readonly=True, required=True)
    communication = fields.Char(string='Memo')
    employee_advance_reconcile_id = fields.Many2one('employee.advance.reconcile', string="Employee Advance Reconcile")

    @api.onchange('emp_advance_id')
    def _onchange_emp_advance_id(self):
        if self.emp_advance_id:
            self.currency_id = self.emp_advance_id.currency_id
            self.amount = self.emp_advance_id.balance
            self.communication = self.emp_advance_id.name

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
            self.communication = self.employee_advance_reconcile_id.name

    @api.constrains('amount')
    def _constrains_amount(self):
        precision = self.env['decimal.precision'].precision_get('Account')
        if any(r.emp_advance_id and float_compare(r.amount, r.emp_advance_id.balance, precision_digits=precision) == 1 for r in self):
            raise ValidationError(_('The amount exceeds the allowable limit of the advance request.'))
        if any(r.employee_advance_reconcile_id and float_compare(r.amount, r.employee_advance_reconcile_id.balance, precision_digits=precision) == 1 for r in self):
            raise ValidationError(_('The amount exceeds the allowable limit.'))

    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        for r in self:
            if not r.journal_id:
                r.hide_payment_method = True
            else:
                journal_payment_methods = r.journal_id.outbound_payment_method_ids
                r.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            return {'domain': {'payment_method_id': [('payment_type', '=', 'outbound'), ('id', 'in', payment_methods.ids)]}}
        return {}

    def get_payment_vals(self):
        if self.emp_advance_id:
            return {
                'partner_type': 'supplier',
                'payment_type': 'outbound',
                'partner_id': self.emp_advance_id.employee_id.sudo().address_home_id.id,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'payment_method_id': self.payment_method_id.id,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'payment_date': self.payment_date,
                'communication': self.communication,
                'employee_advance_id': self.emp_advance_id.id
            }
        elif self.employee_advance_reconcile_id:
            payment_type = self.employee_advance_reconcile_id.difference_amount > 0 and 'inbound' or 'outbound'
            partner_type = self.employee_advance_reconcile_id.difference_amount > 0 and 'customer' or 'supplier'
            return {
                'partner_type': partner_type,
                'payment_type': payment_type,
                'partner_id': self.employee_advance_reconcile_id.employee_id.sudo().address_home_id.id,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'payment_method_id': self.payment_method_id.id,
                'amount': self.amount,
                'currency_id': self.currency_id.id,
                'payment_date': self.payment_date,
                'communication': self.communication,
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
        payment = self.env['account.payment'].create(self.get_payment_vals())
        payment.post()
        return {'type': 'ir.actions.act_window_close'}

