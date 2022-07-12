from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrEmployeeAdvanceReconcile(models.Model):
    _name = 'employee.advance.reconcile'
    _description = 'HR Employee Advance Reconcile'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_employee(self):
        HREmployee = self.env['hr.employee']
        employee_id = HREmployee.search([('user_id', '=', self.env.user.id)], limit=1)

        if not employee_id:
            employee_id = HREmployee.search([('address_id', '=', self.env.user.partner_id.id)], limit=1)
            if not employee_id:
                # sudo() is required since the address_home_id requires hr.group_hr_user
                # See: https://github.com/tvtma/odoo/blob/5f35e97e917b3a15ac5e4202d6811fb0c30caa42/addons/hr/models/hr.py#L113
                employee_id = HREmployee.sudo().search([('address_home_id', '=', self.env.user.partner_id.id)], limit=1)

        return employee_id or False

    name = fields.Char(string='Reference', required=True, readonly=True, default='/')
    date = fields.Date(string='Reconciled Date', required=True, default=fields.Date.today,
        states={
            'confirm': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]
        })
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=_get_default_employee,
        states={
            'confirm': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]
        })
    job_id = fields.Many2one('hr.job', string='Job Position', related='employee_id.job_id', readonly=True)
    department_id = fields.Many2one('hr.department',
                                    string='Department', related='employee_id.department_id', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Employee Advance Journal',
                                required=True, domain=[('is_advance_journal', '=', True)],
                                states={
                                    'confirm': [('readonly', True)],
                                    'done': [('readonly', True)],
                                    'cancel': [('readonly', True)]
                                })
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    line_db_ids = fields.One2many('employee.advance.reconcile.line', 'reconcile_id',
                                    string='Debits', domain=[('type', '=', 'db')],
                                    states={
                                        'confirm': [('readonly', True)],
                                        'done': [('readonly', True)],
                                        'cancel': [('readonly', True)]
                                    }, groups='account.group_account_user', compute='_compute_data_line', store=True, readonly=False)
    line_cr_ids = fields.One2many('employee.advance.reconcile.line', 'reconcile_id',
                                    string='Credits', domain=[('type', '=', 'cr')],
                                    states={
                                        'confirm': [('readonly', True)],
                                        'done': [('readonly', True)],
                                        'cancel': [('readonly', True)]
                                    }, groups='account.group_account_user', compute='_compute_data_line', store=True, readonly=False)
    payment_ids = fields.One2many('account.payment', 'employee_advance_reconcile_id', string='Payment', readonly=True, groups='account.group_account_user')

    difference_amount = fields.Float(string='Difference Amount',
                                     compute='_compute_difference_amount', digits='Account', store=True)
    balance = fields.Float(string='Balance', compute='_compute_balance', digits='Account', store=True)
    has_outstanding_payment = fields.Boolean(string='Has Outstanding Payments', compute='_compute_has_outstanding_payment',
        store=True, help="Technical field to indicate this employee advance reconcile has draft or cancel payment."
            " If exists, user need to resolved them.")
    company_id = fields.Many2one('res.company', string='Company', related='journal_id.company_id', store=True)

    @api.depends('line_db_ids', 'line_db_ids.amount', 'line_cr_ids', 'line_cr_ids.amount')
    def _compute_difference_amount(self):
        reconcile_lines = self.env['employee.advance.reconcile.line'].search([('reconcile_id', 'in', self.ids)])
        for r in self:
            line_db = reconcile_lines.filtered(lambda l: l.reconcile_id == r and l.type == 'db')
            line_cr = reconcile_lines.filtered(lambda l: l.reconcile_id == r and l.type == 'cr')
            if line_db:
                amount_db = sum(x.amount for x in line_db)
            else:
                amount_db = sum(x.amount for x in r.line_db_ids)
            if line_cr:
                amount_cr = sum(x.amount for x in line_cr)
            else:
                amount_cr = sum(x.amount for x in r.line_cr_ids)
            r.difference_amount = amount_db - amount_cr

    @api.depends('difference_amount', 'payment_ids', 'payment_ids.amount', 'payment_ids.state')
    def _compute_balance(self):
        for r in self:
            r.balance = abs(r.difference_amount) - sum(r.payment_ids.mapped('amount'))

    @api.depends('payment_ids', 'payment_ids.state')
    def _compute_has_outstanding_payment(self):
        for r in self:
            if any(payment.state in ('draft', 'cancel') for payment in r.payment_ids):
                r.has_outstanding_payment = True
            else:
                r.has_outstanding_payment = False

    def generate_lines(self):
        self.ensure_one()
        if not self.employee_id.sudo().address_home_id:
                raise UserError(_("Your must specify the Private Address for the employee %s.") % self.employee_id.name)

        reconciled_line_ids = []
        reconciles = self.search([('name', '!=', self.name), ('company_id', '=', self.journal_id.company_id.id)])
        if reconciles:
            # 1. Get line of move in payment
            reconciled_line_ids += reconciles.payment_ids.move_id.line_ids.filtered(
                lambda ml: ml.account_id.id == self.employee_id.property_advance_account_id.id
            ).ids
            # 2. Get debit line in reconcile
            reconciled_line_ids += reconciles.line_db_ids.move_line_id.ids
            # 3. Get credit line in reconcile
            reconciled_line_ids += reconciles.line_cr_ids.move_line_id.ids

        unreconciled_move_lines_domain = self.employee_id._prepare_unreconciled_move_lines_domain(
            reconciled_line_ids, self.date, self.journal_id.company_id
        )
        unreconciled_move_lines = self.env['account.move.line'].search(unreconciled_move_lines_domain)
        line_dbs = []
        line_crs = []
        for item in unreconciled_move_lines:
            if item.name and item.name != item.ref:
                name = '%s [%s]' % (item.name, item.ref)
            elif item.name:
                name = item.name
            elif item.ref:
                name = item.ref
            else:
                name = '/'
            if item.debit > 0:
                line_dbs.append((0, 0, {
                    'name': name,
                    'move_line_id': item.id,
                    'account_id': item.account_id.id,
                    'date': item.date,
                    'amount': item.debit,
                    'type':'db'
                }))
            elif item.credit > 0:
                line_crs.append((0, 0, {
                    'name': name,
                    'move_line_id': item.id,
                    'account_id': item.account_id.id,
                    'date': item.date,
                    'amount': item.credit,
                    'type':'cr'
                }))
        # drop existing debit lines
        for item in self.line_db_ids:
            line_dbs.append((2, item.id))
        for item in self.line_cr_ids:
            line_crs.append((2, item.id))

        return {'line_dbs': line_dbs, 'line_crs': line_crs}

    @api.depends('employee_id', 'journal_id', 'date')
    def _compute_data_line(self):
        for r in self:
            if r.employee_id and r.journal_id and r.date:
                res = r.generate_lines()
                r.line_db_ids = res['line_dbs']
                r.line_cr_ids = res['line_crs']
            else:
                r.line_db_ids = False
                r.line_cr_ids = False

    def action_compute_data_line(self):
        self._compute_data_line()

    def action_confirm(self):
        for r in self:
            if not r.line_db_ids:
                raise UserError(_("You cannot confirm a reconcile without any debits."))

            if sum(r.line_db_ids.mapped('amount')) - sum(r.line_cr_ids.mapped('amount')) == 0:
                r.write({'state':'done'})
                r._update_employee_advance_state('done')
            else:
                r.write({'state':'confirm'})
        self._reconcile()

    def _reconcile(self):
        for r in self:
            (r.line_db_ids.move_line_id |
             r.line_cr_ids.move_line_id
            ) \
            .filtered(lambda line: line.account_id == r.employee_id.property_advance_account_id and not line.reconciled) \
            .reconcile()

    def action_cancel(self):
        for r in self:
            (r.line_db_ids.move_line_id |
             r.line_cr_ids.move_line_id
            ) \
            .filtered(lambda line: line.account_id == r.employee_id.property_advance_account_id and line.reconciled) \
            .remove_move_reconcile()
            if r.state == 'done':
                r._update_employee_advance_state('validate')
        self.write({'state':'cancel'})
        reconcile_payments = self.payment_ids
        reconcile_payments.action_draft()
        reconcile_payments.action_cancel()

    def _update_employee_advance_state(self, state):
        self.ensure_one()
        emp_advances = self.env['account.payment'].search([
            ('id', 'in', self.line_db_ids.move_line_id.payment_id.ids)
            ]).employee_advance_id
        if emp_advances:
            emp_advances.write({'state':state})

    def action_draft(self):
        for r in self:
            r.write({'state':'draft'})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('employee.advance.reconcile') or '/'
        return super(HrEmployeeAdvanceReconcile, self).create(vals_list)

    def unlink(self):
        for item in self:
            if item.state not in ('draft'):
                raise UserError(_("You can only delete records whose state is draft."))
        return super(HrEmployeeAdvanceReconcile, self).unlink()
