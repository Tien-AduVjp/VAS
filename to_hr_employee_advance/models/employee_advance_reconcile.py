from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrEmployeeAdvanceReconcileLine(models.Model):
    _name = 'employee.advance.reconcile.line'
    _description = 'HR Employee Advance Reconcile Line'

    reconcile_id = fields.Many2one('employee.advance.reconcile',
                                   string="Reconcile", ondelete='cascade', index=True)
    name = fields.Char(string="Description", required=True, readonly=True)
    move_line_id = fields.Many2one('account.move.line',
                                   string="Journal Item", required=True, readonly=True, ondelete='cascade')
    account_id = fields.Many2one('account.account',
                                 string="Account", required=True, readonly=True)
    date = fields.Date(string="Date", required=True, readonly=True)
    amount = fields.Float(string="Amount", required=True, readonly=True, digits='Account')
    type = fields.Selection([
        ('db', 'Debit'),
        ('cr', 'Credit'),
    ], string="Status", required=True, readonly=True)


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

    name = fields.Char(string="Reference", required=True, readonly=True, default='/')
    date = fields.Date(string="Reconciled Date", required=True, default=fields.Date.today,
        states={
            'confirm': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]
        })
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, default=_get_default_employee,
        states={
            'confirm': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)]
        })
    job_id = fields.Many2one('hr.job', string="Job Position", related='employee_id.job_id', readonly=True)
    department_id = fields.Many2one('hr.department',
                                    string="Department", related='employee_id.department_id', readonly=True)
    journal_id = fields.Many2one('account.journal', string="Employee Advance Journal",
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
    ], string="Status", default='draft', tracking=True)
    line_db_ids = fields.One2many('employee.advance.reconcile.line', 'reconcile_id',
                                    string="Debits", domain=[('type', '=', 'db')],
                                    states={
                                        'confirm': [('readonly', True)],
                                        'done': [('readonly', True)],
                                        'cancel': [('readonly', True)]
                                    }, compute='_compute_data_line', store=True, readonly=False)
    line_cr_ids = fields.One2many('employee.advance.reconcile.line', 'reconcile_id',
                                    string="Credits", domain=[('type', '=', 'cr')],
                                    states={
                                        'confirm': [('readonly', True)],
                                        'done': [('readonly', True)],
                                        'cancel': [('readonly', True)]
                                    }, compute='_compute_data_line', store=True, readonly=False)
#     settlement_ids = fields.One2many('employee.advance.settlement', 'reconcile_id',
#                                      string="Settlements", readonly=True)
    payment_ids = fields.One2many('account.payment', 'employee_advance_reconcile_id', string="Payment", readonly=True)

    difference_amount = fields.Float(string="Difference Amount",
                                     compute='_compute_difference_amount', digits='Account', store=True)
    balance = fields.Float(string="Balance", compute='_compute_balance', digits='Account', store=True)

    move_id = fields.Many2one('account.move', string="Journal Entry")
    move_lines = fields.One2many('account.move.line', related='move_id.line_ids', string="Journal Items", readonly=True)

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
            r.balance = abs(r.difference_amount) - sum(x.amount for x in r.payment_ids.filtered(lambda line: line.state in ['posted', 'reconciled']))

    def generate_lines(self, journal_id, employee_id, date=None):
        date = date or self.date
        if not employee_id.sudo().address_home_id:
                raise UserError(_("Your must specify the Private Address for the employee %s.") % employee_id.name)

        reconcile_lines = self.env['employee.advance.reconcile.line'].search([('reconcile_id.name', '!=', self.name)])
        move_line_ids = []
        for item in reconcile_lines:
            move_line_ids.append(item.move_line_id.id)

        reconciles = self.env['employee.advance.reconcile'].search([('name', '!=', self.name)])
        for item in reconciles:
            for line in item.move_lines.filtered(lambda ml: ml.account_id.id == journal_id.default_debit_account_id.id):
                move_line_ids.append(line.id)

            for line in item.payment_ids.move_line_ids.filtered(lambda ml: ml.account_id.id == journal_id.default_debit_account_id.id):
                move_line_ids.append(line.id)

        employee_advances = self.env['employee.advance'].search([('state', '=', 'validate')])
        for item in employee_advances:
            for line in item.move_lines.filtered(lambda ml: ml.account_id.id == journal_id.default_debit_account_id.id):
                move_line_ids.append(line.id)

        move_lines = self.env['account.move.line'].search([
            ('partner_id', '=', employee_id.sudo().address_home_id.id),
            ('account_id', '=', journal_id.default_debit_account_id.id),
            ('parent_state', '=', 'posted'),
            ('id', 'not in', tuple(move_line_ids)),
            ('date', '<=', date)
        ])
        line_dbs = []
        line_crs = []
        for item in move_lines:
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
                res = r.generate_lines(r.journal_id, r.employee_id, r.date)
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
            if r.employee_id.company_id.use_employee_advance_pass_through_account:
                difference_amount = sum(r.line_db_ids.mapped('amount')) - sum(r.line_cr_ids.mapped('amount'))
                move_obj = self.env['account.move']
                address_home_id = r.employee_id.sudo().address_home_id

                move_lines = []
                if difference_amount > 0:
                    move_lines.append((0, 0, {
                        'name': r.name,
                        'partner_id': address_home_id.id,
                        'account_id': r.journal_id.default_credit_account_id.id,
                        'credit': difference_amount
                    }))
                    move_lines.append((0, 0, {
                        'name': r.name,
                        'partner_id': address_home_id.id,
                        'account_id': address_home_id.property_account_receivable_id.id,
                        'debit': difference_amount
                    }))
                elif difference_amount < 0:
                    move_lines.append((0, 0, {
                        'name': r.name,
                        'partner_id': address_home_id.id,
                        'account_id': address_home_id.property_account_payable_id.id,
                        'credit':-difference_amount
                    }))
                    move_lines.append((0, 0, {
                        'name': r.name,
                        'partner_id': address_home_id.id,
                        'account_id': r.journal_id.default_credit_account_id.id,
                        'debit':-difference_amount
                    }))
                elif difference_amount == 0:
                    r.write({'state':'done'})
                    r._update_employee_advance_state('done')
                    return
                if move_lines:
                    move = move_obj.create({
                        'journal_id': r.journal_id.id,
                        'date': r.date,
                        'ref': r.name,
                        'line_ids': move_lines,
                    })
                    move.post()
                    r.write({'move_id': move.id})
                # else:
            r.write({'state':'confirm'})
        self._reconcile()

    def _reconcile(self):
        for r in self:
            (r.line_db_ids.move_line_id | 
             r.line_cr_ids.move_line_id | 
             r.move_id.line_ids
            ) \
            .filtered(lambda line: line.account_id == r.journal_id.default_debit_account_id and not line.reconciled) \
            .reconcile()

    def action_cancel(self):
        for r in self:
            (r.line_db_ids.move_line_id | 
             r.line_cr_ids.move_line_id | 
             r.move_id.line_ids
            ) \
            .filtered(lambda line: line.account_id == r.journal_id.default_debit_account_id and line.reconciled) \
            .remove_move_reconcile()
            if r.move_id:
                move_id = r.move_id.with_context(force_delete=True)
                if move_id.state == 'draft':
                    move_id.unlink()
                elif move_id.state == 'posted':
                    move_id.button_cancel()
                    move_id.unlink()
            if r.state == 'done':
                r._update_employee_advance_state('spent')
        self.write({'state':'cancel'})
        reconcile_payments = self.payment_ids
        reconcile_payments.action_draft()
        reconcile_payments.cancel()

    def _update_employee_advance_state(self, state):
        self.ensure_one()
        emp_advances = self.env['employee.advance']
        if self.employee_id.company_id.use_employee_advance_pass_through_account:
            emp_advances = self.env['employee.advance'].search([
                ('move_id', 'in', self.line_db_ids.move_line_id.move_id.ids)
                ])
        else:
            emp_advances = self.env['account.payment'].search([
                ('id', 'in',self.line_db_ids.move_line_id.payment_id.ids)
                ]).employee_advance_id
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

