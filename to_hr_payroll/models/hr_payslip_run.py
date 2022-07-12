from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_date


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_end DESC, id DESC'
    _description = 'Payslip Batches'

    name = fields.Char(required=True,
                       readonly=False, states={'verified': [('readonly', True)], 'close': [('readonly', True)], 'cancelled': [('readonly', True)]},
                       compute='_compute_name', store=True)
    thirteen_month_pay = fields.Boolean(string='13th-Month Pay', readonly=False, states={'verified': [('readonly', True)],
                                                                                         'close': [('readonly', True)],
                                                                                         'cancelled': [('readonly', True)]}, tracking=True,
                                            help="If checked, this payslip batch will be considered as 13th-Month payslip batch")
    thirteen_month_pay_year = fields.Integer('13th-Month Pay Year', readonly=False, states={'verified': [('readonly', True)],
                                                                                            'close': [('readonly', True)],
                                                                                            'cancelled': [('readonly', True)]},
                                             help="The year for thirteen month pay calculation")
    thirteen_month_pay_include_trial = fields.Boolean(string='13th-Month Pay Incl. Trial',
                                                      readonly=False, states={
                                                          'verified': [('readonly', True)],
                                                          'close': [('readonly', True)],
                                                          'cancelled': [('readonly', True)]
                                                          },
                                                      help="If enabled, 13th-Month Pay will include trial contracts (which has trial end"
                                                      " date specified) during salary computation.")
    slip_ids = fields.One2many('hr.payslip', 'payslip_run_id', string='Payslips', readonly=False,
        states={'verified': [('readonly', True)],
                'close': [('readonly', True)],
                'cancelled': [('readonly', True)]})
    payslips_count = fields.Integer(string='Payslips Count', compute='_compute_payslips_count', groups="to_hr_payroll.group_hr_payroll_user")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Verified'),
        ('close', 'Close'),
        ('cancelled', 'Cancelled'),
    ], string='Status', index=True, readonly=True, copy=False, default='draft', tracking=True)
    date_start = fields.Date(string='Date From', required=True,
                             readonly=False, states={
                                 'verified': [('readonly', True)],
                                 'close': [('readonly', True)],
                                 'cancelled': [('readonly', True)]
                                 },
                             compute='_compute_date_start', store=True, tracking=True)
    date_end = fields.Date(string='Date To', required=True,
                           readonly=False, states={
                               'verified': [('readonly', True)],
                               'close': [('readonly', True)],
                               'cancelled': [('readonly', True)]
                               },
                           compute='_compute_date_end', store=True, tracking=True)
    credit_note = fields.Boolean(string='Credit Note', readonly=False,
        states={'verified': [('readonly', True)],
                'close': [('readonly', True)],
                'cancelled': [('readonly', True)]},
        help="If its checked, indicates that all payslips generated from here are refund payslips.")
    company_id = fields.Many2one('res.company', string='Company', readonly=False, copy=False, required=True,
                                 default=lambda self: self.env.company, states={'verified': [('readonly', True)],
                                                                                'close': [('readonly', True)],
                                                                                'cancelled': [('readonly', True)]})
    salary_cycle_id = fields.Many2one('hr.salary.cycle', string='Salary Cycle', required=True,
                                             compute='_compute_salary_cycle', store=True, readonly=False, tracking=True,
                                             help="Select an appropriate salary cycle to apply if it differs from"
                                             " the one specified in your company's settings.")
    currency_id = fields.Many2one(related='company_id.currency_id')
    payslip_line_ids = fields.One2many('hr.payslip.line', 'payslip_run_id', string='Payslip Lines')
    payslip_lines_count = fields.Integer('Payslip Lines Count', compute='_compute_payslip_lines_count')
    total_net_amount = fields.Monetary(string='Employees\'s Net Income', compute='_compute_total_net_amount', store=True, tracking=True)
    contracts_count = fields.Integer(string='Contracts Count', compute='_compute_contracts_count')
    employees_count = fields.Integer(string='Employees Count', compute='_compute_employees_count')
    company_cost = fields.Monetary(string='Company Cost', compute='_compute_company_cost', store=True, tracking=True,
                                   groups='to_hr_payroll.group_hr_payroll_user')

    @api.model
    def default_get(self, fields_list):
        res = super(HrPayslipRun, self).default_get(fields_list)
        if 'thirteen_month_pay_year' not in res:
            res['thirteen_month_pay_year'] = fields.Date.today().year - 1
        return res

    @api.depends('company_id')
    def _compute_salary_cycle(self):
        default_cycle = self.env.ref('to_hr_payroll.hr_salary_cycle_default', raise_if_not_found=False)
        for r in self:
            r.salary_cycle_id = r.company_id.salary_cycle_id or default_cycle

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name', False):
                vals['name'] = '/'
        records = super(HrPayslipRun, self).create(vals_list)
        records.filtered(lambda r: r.name == '/')._compute_name()
        records._sync_payslips()
        return records

    def write(self, vals):
        res = super(HrPayslipRun, self).write(vals)
        self._sync_payslips()
        return res

    def _get_sync_fields(self):
        return {
            'thirteen_month_pay': 'thirteen_month_pay',
            'thirteen_month_pay_year': 'thirteen_month_pay_year',
            'thirteen_month_pay_include_trial': 'thirteen_month_pay_include_trial',
            }

    def _sync_payslips(self):
        for batch_field, slip_field in self._get_sync_fields().items():
            for r in self:
                for slip in r.slip_ids:
                    if getattr(slip, slip_field) != getattr(r, batch_field):
                        setattr(slip, slip_field, getattr(r, batch_field))

    def action_check_payslip_duplication(self):
        self.slip_ids._check_employee_batch()

    @api.depends('company_id', 'thirteen_month_pay', 'thirteen_month_pay_year')
    def _compute_date_start(self):
        today = fields.Date.today()
        for r in self:
            company = r.company_id or r.env.company
            cycle = company.salary_cycle_id or self.env.ref('to_hr_payroll.hr_salary_cycle_default')
            if r.thirteen_month_pay and r.thirteen_month_pay_year:
                thirteen_month_pay_year = self.env['to.base'].validate_year(r.thirteen_month_pay_year)
                self.env['hr.payslip']._check_thirteen_month_pay_year_valid(thirteen_month_pay_year)
                r.date_start = cycle._get_year_start_date(today.replace(year=thirteen_month_pay_year))
            else:
                r.date_start = cycle._get_month_start_date(today) + relativedelta(months=cycle.start_month_offset)

    @api.depends('company_id', 'thirteen_month_pay', 'thirteen_month_pay_year')
    def _compute_date_end(self):
        today = fields.Date.today()
        for r in self:
            company = r.company_id or r.env.company
            cycle = company.salary_cycle_id or self.env.ref('to_hr_payroll.hr_salary_cycle_default')
            date_start = r.date_start or cycle._get_month_start_date(today) + relativedelta(months=cycle.start_month_offset)
            if r.thirteen_month_pay and r.thirteen_month_pay_year:
                thirteen_month_pay_year = self.env['to.base'].validate_year(r.thirteen_month_pay_year)
                self.env['hr.payslip']._check_thirteen_month_pay_year_valid(thirteen_month_pay_year)
                r.date_end = cycle._get_year_end_date(today.replace(year=thirteen_month_pay_year))
            else:
                r.date_end = date_start + relativedelta(months=1, days=-1)

    @api.depends('slip_ids.company_cost')
    def _compute_company_cost(self):
        for r in self:
            r.company_cost = sum(r.slip_ids.mapped('company_cost'))

    def _compute_contracts_count(self):
        self.flush()
        mapped_data = {}
        if self.ids:
            # read group, by pass ORM for performance
            self.env.cr.execute("""
            SELECT r.id as payslip_run_id, COUNT(DISTINCT(pshc.contract_id)) as contracts_count
            FROM hr_payslip_run AS r
            JOIN hr_payslip AS ps ON ps.payslip_run_id = r.id
            JOIN hr_payslip_hr_contract_rel AS pshc ON pshc.payslip_id = ps.id
            WHERE r.id in %s
            GROUP BY r.id
            """, (tuple(self.ids),))
            contracts_data = self.env.cr.dictfetchall()
            mapped_data = dict([(dict_data['payslip_run_id'], dict_data['contracts_count']) for dict_data in contracts_data])
        for r in self:
            r.contracts_count = mapped_data.get(r.id, 0)

    def _compute_employees_count(self):
        self.flush()
        # read group, by pass ORM for performance
        self.env.cr.execute("""
        SELECT r.id AS payslip_run_id, COUNT(DISTINCT(e.id)) as employees_count
        FROM hr_employee AS e
        JOIN hr_payslip AS ps ON ps.employee_id = e.id
        JOIN hr_payslip_run AS r ON r.id = ps.payslip_run_id
        WHERE r.id in %s
        GROUP BY r.id
        """, (tuple(self.ids),))
        employees_data = self.env.cr.dictfetchall()
        mapped_data = dict([(dict_data['payslip_run_id'], dict_data['employees_count']) for dict_data in employees_data])
        for r in self:
            r.employees_count = mapped_data.get(r.id, 0)

    def _compute_payslips_count(self):
        total_data = self.env['hr.payslip'].read_group([('payslip_run_id', 'in', self.ids)], ['payslip_run_id'], ['payslip_run_id'])
        mapped_data = dict([(dict_data['payslip_run_id'][0], dict_data['payslip_run_id_count']) for dict_data in total_data])
        for r in self:
            r.payslips_count = mapped_data.get(r.id, 0)

    def _compute_payslip_lines_count(self):
        total_data = self.env['hr.payslip.line'].read_group([('payslip_run_id', 'in', self.ids)], ['payslip_run_id'], ['payslip_run_id'])
        mapped_data = dict([(dict_data['payslip_run_id'][0], dict_data['payslip_run_id_count']) for dict_data in total_data])
        for r in self:
            r.payslip_lines_count = mapped_data.get(r.id, 0)

    @api.depends('slip_ids', 'slip_ids.net_salary')
    def _compute_total_net_amount(self):
        for r in self:
            r.total_net_amount = sum(r.slip_ids.mapped('net_salary'))

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        for r in self:
            if r.date_start and r.date_end and r.date_start > r.date_end:
                raise ValidationError(_("The 'Date Start' of the payslip batch '%s' must be earlier than its 'Date End'.") % r.name)

    def action_compute_sheets(self):
        self.mapped('slip_ids').with_context(do_not_recompute_fields=True).compute_sheet()

    def action_verify_payslips(self):
        draft_slips = self.mapped('slip_ids').filtered(lambda ps: ps.state == 'draft')
        if draft_slips:
            draft_slips.with_context(without_compute_sheet=True).action_payslip_verify()
        self.write({'state': 'verified'})

    def action_cancel(self):
        self.mapped('slip_ids').action_payslip_cancel()
        self.write({'state': 'cancelled'})

    def action_payslipbatch_send(self):
        '''
        This function opens a window to compose an email, with the payslip batch template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('to_hr_payroll', 'email_template_payslipbatch')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'hr.payslip.run',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def unlink(self):
        for r in self.filtered(lambda b: b.slip_ids and b.state != 'draft'):
            if r.slip_ids:
                raise UserError(_("You may not be able to delete the Payslip Batch '%s' which contains payslip(s). Please delete the payslip(s) first.") % (r.name,))
        self.slip_ids.unlink()
        return super(HrPayslipRun, self).unlink()

    def _get_payslip_run_name(self, date_end=None):
        if self.thirteen_month_pay and self.thirteen_month_pay_year:
            return _("13th-Month Payslips Batch for the year %s") % self.thirteen_month_pay_year
        else:
            date_end = date_end or self.date_end
            return _('Payslip Batch for %s') % format_date(self.env, date_end, date_format='MMMM-y')

    @api.depends('date_start', 'thirteen_month_pay', 'thirteen_month_pay_year')
    def _compute_name(self):
        for r in self:
            r.name = r._get_payslip_run_name()

    def draft_payslip_run(self):
        self.mapped('slip_ids').action_payslip_draft()
        return self.write({'state': 'draft'})

    def close_payslip_run(self):
        return self.write({'state': 'close'})

    def action_view_contracts(self):
        contracts = self.slip_ids.contract_ids
        action = self.env['ir.actions.act_window']._for_xml_id('hr_contract.action_hr_contract')
        action['context'] = {'search_default_group_by_state': 1}
        action['domain'] = "[('id', 'in', %s)]" % str(contracts.ids)
        return action

    def action_view_employees(self):
        employees = self.slip_ids.employee_id
        action = self.env['ir.actions.act_window']._for_xml_id('hr.open_view_employee_list_my')
        action['context'] = {}
        action['domain'] = "[('id', 'in', %s)]" % str(employees.ids)
        return action

    def action_view_payslips(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_hr_payroll.act_hr_employee_payslip_list')

        # override the context to get rid of the default filtering
        action['context'] = {
            'default_payslip_run_id': self.id,
            'default_date_from': self.date_start,
            'default_date_to': self.date_end,
            'default_credit_note': self.credit_note,
            'default_thirteen_month_pay': self.thirteen_month_pay,
            'default_thirteen_month_pay_year': self.thirteen_month_pay_year,
            'default_thirteen_month_pay_include_trial': self.thirteen_month_pay_include_trial
            }

        # choose the view_mode accordingly
        if self.payslips_count != 1:
            action['domain'] = "[('payslip_run_id', '=', %s)]" % str(self.id)
        elif self.payslips_count == 1:
            res = self.env.ref('to_hr_payroll.view_hr_payslip_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.slip_ids.id
        return action

    def action_view_payslip_lines(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('to_hr_payroll.action_windows_hr_payslip_line')
        # choose the view_mode accordingly
        if self.payslip_lines_count != 1:
            action['domain'] = "[('payslip_run_id', '=', %s)]" % str(self.id)
        elif self.payslip_lines_count == 1:
            res = self.env.ref('to_hr_payroll.view_hr_payslip_line_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = self.slip_ids.id
        return action

    @api.constrains('thirteen_month_pay', 'thirteen_month_pay_year')
    def _check_thirteen_month_pay_year(self):
        for r in self.filtered(lambda rec: rec.thirteen_month_pay):
            thirteen_month_pay_year = self.env['to.base'].validate_year(r.thirteen_month_pay_year)
            self.env['hr.payslip']._check_thirteen_month_pay_year_valid(thirteen_month_pay_year)

    def copy(self, default=None):
        raise UserError(_("Payslip Batches are not allowed to get duplicated."))
