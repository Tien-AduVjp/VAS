from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class HrEmployeeAdvance(models.Model):
    _name = 'employee.advance'
    _order = 'date desc, id'
    _description = 'HR Employee Advance'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_employee(self):
        employee_obj_sudo = self.env['hr.employee'].sudo()
        employee_id = self._context.get(
            'default_employee_id',
            employee_obj_sudo.search([('address_home_id', '=', self.env.user.partner_id.id)], limit=1).id
            )
        return employee_obj_sudo.browse(employee_id)

    @api.model
    def _get_default_journal(self):
        company_id = self.env.company.id
        return self.env['account.journal'].search([('is_advance_journal', '=', True), ('company_id', '=', company_id)], limit=1)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Waiting Approved'),
        ('refuse', 'Refused'),
        ('validate1', 'First Approval'),
        ('validate', 'Approved'),
        ('done', 'Reconciled'),
    ], string='Status', default='draft', required=True, tracking=True)
    name = fields.Char(string='Reference', readonly=True, default='/', copy=False)
    date = fields.Date(string='Advance Date', required=True, default=fields.Date.today, readonly=False,
                       states={
                           'confirm': [('readonly', True)],
                           'refuse': [('readonly', True)],
                           'validate1': [('readonly', True)],
                           'validate': [('readonly', True)],
                           'done': [('readonly', True)]
                           }
                       )
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=_get_default_employee, readonly=False,
                                  states={
                                      'confirm': [('readonly', True)],
                                      'refuse': [('readonly', True)],
                                      'validate1': [('readonly', True)],
                                      'validate': [('readonly', True)],
                                      'done': [('readonly', True)]
                                      }
                                  )
    job_id = fields.Many2one('hr.job', string='Job Position', compute='_compute_job_and_department', store=True)
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_job_and_department', store=True)

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, compute='_compute_currency', store=True,
                                  readonly=False, states={
                                      'confirm': [('readonly', True)],
                                      'refuse': [('readonly', True)],
                                      'validate1': [('readonly', True)],
                                      'validate': [('readonly', True)],
                                      'done': [('readonly', True)]
                                      },
                                  copy=True
                                  )
    lines = fields.One2many('employee.advance.line', 'advance_id', string='Advance Lines', readonly=False,
                            states={
                                'confirm': [('readonly', True)],
                                'refuse': [('readonly', True)],
                                'validate1': [('readonly', True)],
                                'validate': [('readonly', True)],
                                'done': [('readonly', True)]
                                }, copy=True
                            )
    amount = fields.Monetary(string='Total Amount', compute='_compute_amount',
                          store=True, currency_field='currency_id')
    balance = fields.Monetary(string='Balance', compute='_compute_balance', currency_field='currency_id', store=True, copy=False)
    payment_ids = fields.One2many('account.payment', 'employee_advance_id', string='Payment', readonly=True, copy=False,
                                  groups='account.group_account_user')
    manager_id = fields.Many2one('hr.employee', string='First Approval', readonly=True, copy=False,
        help='This area is automatically filled by the user who validate the request')
    manager_id2 = fields.Many2one('hr.employee', string='Second Approval', readonly=True, copy=False,
        help='This area is automaticly filled by the user who validate the request with second level (If it need second validation)')
    company_id = fields.Many2one('res.company', string='Company', related='journal_id.company_id', store=True)
    journal_id = fields.Many2one('account.journal', string='Employee Advance Journal',
                             required=True, domain="[('is_advance_journal', '=', True),('company_id','=',company_id)]",
                             default=_get_default_journal,
                             context="{'default_is_advance_journal': True, 'default_company_id': company_id}",
                             readonly=False,
                             states={'confirm': [('readonly', True)],
                                     'refuse': [('readonly', True)],
                                     'validate1': [('readonly', True)],
                                     'validate': [('readonly', True)],
                                     'done': [('readonly', True)]})
    has_outstanding_payment = fields.Boolean(string='Has Outstanding Payments', compute='_compute_has_outstanding_payment',
        store=True, help="Technical field to indicate this employee advance has draft or cancel payment."
            " If exists, user need to resolved them.")
    payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid')],
        string="Payment Status", store=True, readonly=True, copy=False, tracking=True,
        compute='_compute_payment_state')

    @api.model
    def default_get(self, fields):
        res = super(HrEmployeeAdvance, self).default_get(fields)
        journal_id = self.env.context.get('journal_id', False)
        employee_id = self.env.context.get('employee_id', False)
        if journal_id:
            currency_id = journal_id.currency_id
        elif employee_id:
            currency_id = employee_id.company_id.currency_id
        else:
            currency_id = self.env.company.currency_id
        if 'currency_id' in fields:
            res['currency_id'] = currency_id.id
        return res

    @api.constrains('company_id', 'journal_id')
    def _check_journal_company(self):
        for r in self:
            if r.journal_id.company_id != r.company_id:
                raise UserError(_("The journal %s does not belong to the company %s.")
                                % (r.journal_id.name, r.company_id.name))

    @api.depends('journal_id', 'employee_id')
    def _compute_currency(self):
        for r in self:
            r.currency_id = r.journal_id.currency_id or r.employee_id.company_id.currency_id or self.env.company.currency_id

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id and not self.employee_id.sudo().address_home_id:
            employee_id = self.employee_id
            self.employee_id = False
            raise ValidationError(_("The employee '%s' you've selected has no Private Address specified. Please specify one for this employee first.")
                                  % (employee_id.name,))

    @api.depends('employee_id')
    def _compute_job_and_department(self):
        for r in self:
            r.job_id = r.employee_id.job_id
            r.department_id = r.employee_id.department_id

    @api.depends('lines.amount')
    def _compute_amount(self):
        for r in self:
            r.amount = sum(x.amount for x in r.lines)

    @api.depends('amount', 'payment_ids', 'payment_ids.amount', 'payment_ids.state')
    def _compute_balance(self):
        for r in self:
            r.balance = r.amount - sum(r.payment_ids.mapped('amount'))

    @api.depends('balance', 'amount', 'state', 'has_outstanding_payment')
    def _compute_payment_state(self):
        for r in self:
            payment_state = 'not_paid'
            if r.state in ('validate', 'done') and not r.has_outstanding_payment:
                if r.currency_id.is_zero(r.balance):
                    payment_state = 'paid'
                elif r.currency_id.compare_amounts(r.amount, r.balance) != 0:
                    payment_state = 'partial'
            r.payment_state = payment_state

    @api.depends('payment_ids', 'payment_ids.state')
    def _compute_has_outstanding_payment(self):
        for r in self:
            if any(payment.state in ('draft', 'cancel') for payment in r.payment_ids):
                r.has_outstanding_payment = True
            else:
                r.has_outstanding_payment = False

    @api.constrains('amount')
    def _constrains_amount(self):
        for r in self:
            if r.currency_id.is_zero(r.amount):
                raise ValidationError(_('Total Amount must not be zero (0)!'))

    def action_confirm(self):
        for r in self:
            if not r.lines:
                raise UserError(_("You cannot confirm an employee advance without any details."))

        self.write({'state':'confirm'})

    def _double_validation_required(self):
        self.ensure_one()
        if self.company_id.currency_id.is_zero(self.amount):
            return False

        date = self.date or fields.Date.today()
        if not self.env.user.has_group('to_hr_employee_advance.group_employee_advance_manager') \
        and self.currency_id.compare_amounts(self.amount, self.company_id.currency_id._convert(self.company_id.amount_double_validation, self.currency_id, self.company_id, date)) >= 0:
            return True
        else:
            return False

    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_manager = self.env.user.has_group('to_hr_employee_advance.group_employee_advance_manager')
        is_approver = self.env.user.has_group('to_hr_employee_advance.group_employee_advance_approver')
        for r in self:
            if not is_manager:
                if not is_approver or not r._check_is_parent(r.employee_id):
                    raise UserError(_("You must be an Employee Advance Approver and manager of employee %s.") % r.employee_id.name)
            if r.state != 'confirm':
                raise UserError(_("Advance request must be confirmed ('To Approve') in order to approve it."))
            if r._double_validation_required():
                r.write({
                    'state': 'validate1',
                    'manager_id': manager.id if manager else False
                    })
            else:
                r.action_validate()

    def action_validate(self):
        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for r in self:
            if r.state not in ['confirm', 'validate1']:
                raise UserError(_('Advance request must be confirmed in order to approve it.'))
            if not self.env.user.has_group('to_hr_employee_advance.group_employee_advance_manager'):
                if r.state == 'validate1':
                    raise UserError(_('Only an Administrator can apply the second approval on leave requests.'))
                else:
                    if not self.env.user.has_group('to_hr_employee_advance.group_employee_advance_approver') or \
                        not self._check_is_parent(r.employee_id):
                        raise UserError(_("You must be an Employee Advance Approver and manager of employee %s.") % r.employee_id.name)
            if not r.employee_id.sudo().address_home_id:
                raise UserError(_("Your must specify the Private Address for the employee %s.") % r.employee_id.name)

            update_data = {
                'state': 'validate',
                }
            if r._double_validation_required():
                update_data['manager_id2'] = manager.id
            else:
                update_data['manager_id'] = manager.id
            r.write(update_data)

    def action_refuse(self):
        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for r in self:
            if not self.env.user.has_group('to_hr_employee_advance.group_employee_advance_manager'):
                if not self.env.user.has_group('to_hr_employee_advance.group_employee_advance_approver') or \
                    not r._check_is_parent(r.employee_id):
                    raise UserError(_("You must be an Employee Advance Approver and manager of employee %s.") % r.employee_id.name)

            if self.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Advance request must be confirmed or validated in order to refuse it.'))

            if r.state == 'validate1':
                r.write({'state': 'refuse', 'manager_id': manager.id})
            else:
                r.write({'state': 'refuse', 'manager_id2': manager.id})
            r.payment_ids.sudo().action_draft()

    def action_draft(self):
        self.write({'state':'draft'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('employee.advance') or '/'
        return super(HrEmployeeAdvance, self).create(vals_list)

    def unlink(self):
        for item in self:
            if item.state not in ('draft'):
                raise UserError(_("You can only delete records whose state is draft."))
        return super(HrEmployeeAdvance, self).unlink()

    def _check_is_parent(self, employee_id):
        while (employee_id and employee_id.parent_id != False):
            if employee_id.parent_id.user_id.id == self.env.user.id:
                return True
            else:
                employee_id = employee_id.parent_id
        return False
