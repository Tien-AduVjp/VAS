from datetime import datetime, time
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import format_date
from odoo.tools.safe_eval import wrap_module
from odoo.exceptions import UserError, ValidationError

from .browsable_object import BrowsableObject, Payslips
from .hr_contract import TAX_POLICY


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_to DESC, id DESC'
    _description = 'Pay Slip'
    _mail_post_access = 'read'

    thirteen_month_pay = fields.Boolean(string='13th-Month Pay', readonly=False, states={'verify': [('readonly', True)],
                                                                                         'done': [('readonly', True)],
                                                                                         'cancel': [('readonly', True)]}, tracking=True,
                                            help="If checked, this payslip will be considered as 13th-Month Payslip")
    thirteen_month_pay_year = fields.Integer('13th-Month Pay Year', readonly=False, states={'verify': [('readonly', True)],
                                                                                            'done': [('readonly', True)],
                                                                                            'cancel': [('readonly', True)]},
                                             help="The year for thirteen month pay calculation")
    thirteen_month_pay_include_trial = fields.Boolean(string='13th-Month Pay Incl. Trial',
                                                      readonly=False, states={
                                                          'verify': [('readonly', True)],
                                                          'done': [('readonly', True)],
                                                          'cancel': [('readonly', True)]
                                                          },
                                                      help="If enabled, 13th-Month Pay will include trial contracts (which has trial end"
                                                      " date specified) during salary computation.")
    struct_id = fields.Many2one('hr.payroll.structure', string='Structure', domain="[('company_id','=',company_id)]",
        readonly=False, states={'verify': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        tracking=True, compute='_compute_struct', store=True,
        help='Defines the rules that have to be applied to this payslip, accordingly '
             'to the contract chosen. If you let empty the field contract, this field isn\'t '
             'mandatory anymore and thus the rules applied will be all the rules set on the '
             'structure of all contracts of the employee valid for the chosen period')
    name = fields.Char(string='Payslip Name',
                       readonly=False, states={'verify': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                       compute='_compute_name', store=True, tracking=True)
    number = fields.Char(string='Reference', readonly=False, copy=False,
        states={'verify': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]}, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, readonly=False,
        states={'verify': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]}, tracking=True)
    date_from = fields.Date(string='Date From', readonly=False, states={'verify': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                            required=True, compute='_compute_date_from', store=True, copy=True, tracking=True)
    date_to = fields.Date(string='Date To', readonly=False, states={'verify': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                          required=True, compute='_compute_date_to', store=True, copy=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('cancel', 'Rejected'),
    ], string='Status', index=True, readonly=False, copy=False, default='draft', tracking=True,
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When user cancel payslip the status is \'Rejected\'.""")
    line_ids = fields.One2many('hr.payslip.line', 'slip_id', string='Payslip Lines', readonly=True,
        states={'verify': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company', readonly=False, states={'verify': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                                 copy=True, required=True,
                                 compute='_compute_company', store=True)
    salary_cycle_id = fields.Many2one('hr.salary.cycle', string='Salary Cycle', required=True,
                                             compute='_compute_salary_cycle', store=True, readonly=False, tracking=True,
                                             help="Select an appropriate salary cycle to apply if it differs from"
                                             " the one specified in your company's settings.")
    worked_days_line_ids = fields.One2many('hr.payslip.worked_days', 'payslip_id',
        string='Payslip Worked Days', copy=False, compute='_compute_worked_days_line_ids', store=True)
    input_line_ids = fields.One2many('hr.payslip.input', 'payslip_id', string='Payslip Inputs',
        readonly=False, states={'verify': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        compute='_compute_input_line_ids', store=True)
    paid = fields.Boolean(string='Made Payment Order ? ', readonly=False, copy=False,
        states={'verify': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]})
    note = fields.Text(string='Internal Note', readonly=False, states={'verify': [('readonly', True)],
                                                                       'done': [('readonly', True)],
                                                                       'cancel': [('readonly', True)]})

    # TODO: remove contract_id in master/15 since we already have contract_ids
    contract_id = fields.Many2one('hr.contract', string='Contract', compute='_compute_contract', store=True, required=True,
        readonly=False, states={'verify': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        copy=True, tracking=True,
        help="The latest contract that is applicable to the payslip period.")
    contract_ids = fields.Many2many('hr.contract', 'hr_payslip_hr_contract_rel', 'payslip_id', 'contract_id',
                                    string='Contracts', compute='_compute_contracts', store=True, copy=False,
                                    help="Technical fields to store all the contracts that are applicable to the payslip period.")
    contracts_count = fields.Integer(string='Contracts Count', compute='_compute_contracts_count')
    salary_computation_mode = fields.Selection(related='contract_id.salary_computation_mode', compute_sudo=True)
    department_id = fields.Many2one(related='contract_id.department_id', store=True)
    job_id = fields.Many2one(related='contract_id.job_id', store=True)

    details_by_salary_rule_category = fields.One2many('hr.payslip.line',
        compute='_compute_details_by_salary_rule_category', string='Details by Salary Rule Category')
    cost_line_ids = fields.One2many('hr.payslip.line',
        compute='_compute_cost_lines', string='Cost Lines', help="The lines whose amount is at company cost")
    credit_note = fields.Boolean(string='Credit Note', readonly=False,
        states={'verify': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]},
        help="Indicates this payslip has a refund of another")
    payslip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Batches', readonly=False, copy=True,
                                     states={'verify': [('readonly', True)],
                                             'done': [('readonly', True)],
                                             'cancel': [('readonly', True)]}, index=True, tracking=True)
    payslip_lines_count = fields.Integer(compute='_compute_payslip_lines_count', string="Payslip Computation Details")
    currency_id = fields.Many2one(related='contract_id.currency_id', store=True, copy=True)
    basic_wage = fields.Monetary(string='Basic Wage', compute='_compute_basic', store=True, tracking=True)
    gross_salary = fields.Monetary(string='Gross Salary', compute='_compute_gross_salary', store=True, tracking=True)
    company_cost = fields.Monetary(string='Company Cost', compute='_compute_company_cost', store=True, tracking=True,
                                   groups='to_hr_payroll.group_hr_payroll_user')
    personal_tax_base = fields.Monetary(string='Personal Income Tax Base', compute='_compute_personal_tax_base', store=True, tracking=True)
    net_salary = fields.Monetary(string='Net Salary', compute='_compute_net', store=True, tracking=True)
    date_confirmed = fields.Date(string='Date Confirmed', copy=False, tracking=True)
    refund_for_payslip_id = fields.Many2one('hr.payslip', string='Refund for', copy=False, help="The original payslip for"
                                            " which this payslip refunds")
    refund_ids = fields.One2many('hr.payslip', 'refund_for_payslip_id', string='Refunds', copy=False, help="The payslips"
                                 " that are the refunds for this payslip")
    refunds_count = fields.Integer(string='Refunds Count', compute='_compute_refunds_count')
    hr_payslip_contribution_line_ids = fields.One2many('hr.payslip.contribution.line', 'payslip_id',
                                                          string='Contribution History Lines', compute='_compute_hr_payslip_contribution_line_ids',
                                                          store=True, copy=False)

    working_month_calendar_ids = fields.One2many('hr.working.month.calendar', 'payslip_id', string='Working Month Calendar',
                                                 compute='_compute_working_month_calendars', store=True)
    working_month_calendar_lines_count = fields.Integer(string='Working Month Calendar Lines Count', compute='_compute_working_month_calendar_lines_count', compute_sudo=True)
    calendar_working_hours = fields.Float(string='Calendar Working Hours', compute='_compute_calendar_working_hours', store=True,
                                       help="Total Working Hours (excl. global leaves) for the FULL months crossing the paylip according"
                                       " to the corresponding working schedule.")
    calendar_working_days = fields.Float(string='Calendar Working Days', compute='_compute_calendar_working_days', store=True,
                                      help="Total Working Days (excl. global leaves) for the FULL months crossing the paylip according"
                                      " to the corresponding working schedule.")

    duty_working_hours = fields.Float(string='Duty Working Hours', compute='_compute_duty_working_hours', store=True,
                                      help="Total Working Hours on duty according to the payslip period and the employee working schedule.")
    duty_working_days = fields.Float(string='Duty Working Days', compute='_compute_duty_working_days', store=True,
                                     help="Total Working Days on duty according to the payslip period and the employee working schedule.")
    leave_days = fields.Float(string='Total Leave Days', compute='_compute_leave_days_hours',
                              help="Total leave days excluding global leaves")
    leave_hours = fields.Float(string='Total Leave Hours', compute='_compute_leave_days_hours',
                               help="Total leave hours excluding global leaves")
    unpaid_leave_days = fields.Float(string='Unpaid Leave Days', compute='_compute_unpaid_leave_days_hours')
    unpaid_leave_hours = fields.Float(string='Unpaid Leave Hours', compute='_compute_unpaid_leave_days_hours')
    worked_days = fields.Float(string='Worked Days', compute='_compute_worked_days_hours')
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_days_hours')

    # Tax fields
    personal_tax_policy = fields.Selection(TAX_POLICY, string='Personal Income Tax Policy', compute='_compute_personal_tax_policy', store=True, tracking=True)
    personal_tax_rule_id = fields.Many2one('personal.tax.rule', string='Tax Rule', compute='_compute_personal_tax_policy', store=True, tracking=True)
    personal_tax_base_deduction = fields.Monetary(string='Personal Deduction', compute='_get_dependent_deduction', store=True, tracking=True)
    dependent_deduction = fields.Monetary(string='Dependent Deduction', compute='_get_dependent_deduction', store=True, tracking=True)
    payslip_personal_income_tax_ids = fields.One2many('payslip.personal.income.tax', 'slip_id', string='Personal Income Tax Details')

    # email template
    employee_partner_id = fields.Many2one('res.partner', string='Employee Contact', compute='_compute_employee_partner_id')
    employee_lang = fields.Char(string='Employee Language', compute='_compute_employee_lang')

    @api.model
    def default_get(self, fields_list):
        result = super(HrPayslip, self).default_get(fields_list)
        today = fields.Date.today()
        cycle = self.env.company.salary_cycle_id or self.env.ref('to_hr_payroll.hr_salary_cycle_default')
        if result.get('date_from', False):
            default_date_from = fields.Date.to_date(result.get('date_from', False))
        else:
            default_date_from = cycle._get_month_start_date(today) + relativedelta(months=cycle.start_month_offset)
        if result.get('date_to', False):
            default_date_to = fields.Date.to_date(result.get('date_to', False))
        else:
            default_date_to = default_date_from + relativedelta(months=+1, days=-1)
        result.update({
            'date_from': default_date_from,
            'date_to': default_date_to
            })
        if 'thirteen_month_pay_year' not in result:
            result['thirteen_month_pay_year'] = fields.Date.today().year - 1
        return result

    @api.depends('employee_id')
    def _compute_company(self):
        for r in self:
            company_id = r.employee_id.company_id.id or r._context.get('default_company_id', r.env.company.id)
            r.company_id = company_id

    @api.depends('contract_id')
    def _compute_personal_tax_policy(self):
        for r in self:
            r.personal_tax_policy = r.contract_id.personal_tax_policy
            r.personal_tax_rule_id = r.contract_id.personal_tax_rule_id

    @api.depends('personal_tax_rule_id', 'employee_id')
    def _get_dependent_deduction(self):
        for r in self:
            if r.personal_tax_rule_id.apply_tax_base_deduction:
                r.dependent_deduction = r.personal_tax_rule_id.dependent_tax_base_ded * r.employee_id.total_dependant
                r.personal_tax_base_deduction = r.personal_tax_rule_id.personal_tax_base_ded
            else:
                r.dependent_deduction = 0.0
                r.personal_tax_base_deduction = 0.0

    @api.depends('working_month_calendar_ids.month_working_hours')
    def _compute_calendar_working_hours(self):
        for r in self:
            r.calendar_working_hours = sum(r.working_month_calendar_ids.mapped('month_working_hours'))

    @api.depends('working_month_calendar_ids.month_working_days')
    def _compute_calendar_working_days(self):
        for r in self:
            r.calendar_working_days = sum(r.working_month_calendar_ids.mapped('month_working_days'))

    @api.depends('working_month_calendar_ids.duty_working_hours')
    def _compute_duty_working_hours(self):
        for r in self:
            r.duty_working_hours = sum(r.working_month_calendar_ids.mapped('duty_working_hours'))

    @api.depends('working_month_calendar_ids.duty_working_days')
    def _compute_duty_working_days(self):
        for r in self:
            r.duty_working_days = sum(r.working_month_calendar_ids.mapped('duty_working_days'))

    @api.depends('working_month_calendar_ids.leave_days', 'working_month_calendar_ids.leave_hours')
    def _compute_leave_days_hours(self):
        for r in self:
            r.leave_days = sum(r.working_month_calendar_ids.mapped('leave_days'))
            r.leave_hours = sum(r.working_month_calendar_ids.mapped('leave_hours'))

    @api.depends('working_month_calendar_ids.unpaid_leave_days', 'working_month_calendar_ids.unpaid_leave_hours')
    def _compute_unpaid_leave_days_hours(self):
        for r in self:
            r.unpaid_leave_days = sum(r.working_month_calendar_ids.mapped('unpaid_leave_days'))
            r.unpaid_leave_hours = sum(r.working_month_calendar_ids.mapped('unpaid_leave_hours'))

    def _compute_worked_days_hours(self):
        for r in self:
            r.worked_days = r.duty_working_days - r.leave_days
            r.worked_hours = r.duty_working_hours - r.leave_hours

    @api.depends('company_id')
    def _compute_salary_cycle(self):
        default_cycle = self.env.ref('to_hr_payroll.hr_salary_cycle_default', raise_if_not_found=False)
        for r in self:
            r.salary_cycle_id = r.company_id.salary_cycle_id or default_cycle

    @api.depends('contract_ids', 'thirteen_month_pay', 'thirteen_month_pay_year', 'salary_cycle_id')
    def _compute_date_from(self):
        validate_year = self.env['to.base'].validate_year
        today = fields.Date.today()
        for r in self:
            cycle = r._get_salary_cycle()
            date_from = r.date_from or cycle._get_month_start_date(today)
            if r.thirteen_month_pay and r.thirteen_month_pay_year:
                thirteen_month_pay_year = validate_year(r.thirteen_month_pay_year)
                r._check_thirteen_month_pay_year_valid(thirteen_month_pay_year)
                date_from = cycle._get_year_start_date(date_from.replace(year=thirteen_month_pay_year))
            else:
                if r.contract_ids:
                    date_from, _ = r.contract_ids._qualify_interval(date_from, today)
            r.date_from = date_from

    @api.depends('contract_ids', 'date_from', 'thirteen_month_pay', 'thirteen_month_pay_year', 'salary_cycle_id')
    def _compute_date_to(self):
        validate_year = self.env['to.base'].validate_year
        today = fields.Date.today()
        for r in self:
            cycle = r._get_salary_cycle()
            dt_from = r.date_from and fields.Date.to_date(r.date_from) or cycle._get_month_start_date(today)
            if r._context.get('default_date_to', False):
                date_to = fields.Date.to_date(r._context.get('default_date_to', False))
            else:
                if r.thirteen_month_pay and r.thirteen_month_pay_year:
                    date_to = dt_from + relativedelta(years=1, days=-1)
                else:
                    date_to = dt_from + relativedelta(months=+1, days=-1)
            if r.contract_id:
                if r.thirteen_month_pay and r.thirteen_month_pay_year:
                    thirteen_month_pay_year = validate_year(r.thirteen_month_pay_year)
                    r._check_thirteen_month_pay_year_valid(thirteen_month_pay_year)
                    date_to = cycle._get_year_end_date(dt_from.replace(year=thirteen_month_pay_year))
                else:
                    _, date_to = r.contract_ids._qualify_interval(dt_from, date_to)
            r.date_to = date_to
        self._compute_contract()

    @api.depends('employee_id', 'date_from', 'date_to', 'thirteen_month_pay_include_trial')
    def _compute_contracts(self):
        for r in self:
            if not r.employee_id or not r.date_from or not r.date_to:
                r.contract_ids = False
            else:
                r.contract_ids = r._get_contracts()

    @api.depends('contract_ids')
    def _compute_contracts_count(self):
        self.flush()
        mapped_data = {}
        if self.ids:
            # read group, by pass ORM for performance
            self.env.cr.execute("""
            SELECT r.id as payslip_id, COUNT(DISTINCT(pshc.contract_id)) as contracts_count
            FROM hr_payslip AS r
            LEFT JOIN hr_payslip_hr_contract_rel AS pshc ON pshc.payslip_id = r.id
            WHERE r.id in %s
            GROUP BY r.id
            """, (tuple(self.ids),))
            contracts_data = self.env.cr.dictfetchall()
            mapped_data = dict([(dict_data['payslip_id'], dict_data['contracts_count']) for dict_data in contracts_data])
        for r in self:
            r.contracts_count = mapped_data.get(r.id, 0)

    @api.depends('contract_ids')
    def _compute_contract(self):
        for r in self:
            contracts = r._get_contracts()
            if not contracts:
                r.contract_id = False
            else:
                r.contract_id = contracts[-1] if contracts else False

    @api.model
    def _include_trial_contracts(self, thirteen_month_pay=False, thirteen_month_pay_include_trial=False):
        if thirteen_month_pay and not thirteen_month_pay_include_trial:
            include_trial_contracts = False
        else:
            include_trial_contracts = True
        return include_trial_contracts

    def _get_contracts(self):
        self.ensure_one()
        contracts = self.employee_id.with_context(
            include_trial_contracts=self._include_trial_contracts(self.thirteen_month_pay, self.thirteen_month_pay_include_trial)
            )._get_contracts(self.date_from, self.date_to, states=['open', 'close'])
        if contracts:
            contracts = contracts.sorted('date_start')
        return contracts

    @api.depends('refund_ids')
    def _compute_refunds_count(self):
        for r in self:
            r.refunds_count = len(r.refund_ids)

    @api.depends('line_ids.total', 'company_id')
    def _compute_basic(self):
        for r in self:
            basic_code = r.company_id.basic_wage_rule_categ_id and r.company_id.basic_wage_rule_categ_id.code or 'BASIC'
            r.basic_wage = r._get_salary_line_total(basic_code)

    @api.depends('line_ids.total', 'company_id')
    def _compute_personal_tax_base(self):
        for r in self:
            personal_tax_base_code = r.company_id.tax_base_rule_categ_id and r.company_id.tax_base_rule_categ_id.code or 'TAXBASE'
            r.personal_tax_base = r._get_salary_line_total(personal_tax_base_code)

    @api.depends('line_ids.total', 'company_id')
    def _compute_gross_salary(self):
        for r in self:
            gross_code = r.company_id.gross_salary_rule_categ_id and r.company_id.gross_salary_rule_categ_id.code or 'GROSS'
            r.gross_salary = r._get_salary_line_total(gross_code)

    def _get_cost_lines(self):
        self.ensure_one()
        return self.mapped('line_ids').filtered(lambda line: line.salary_rule_id.category_id.paid_by_company)

    @api.depends('line_ids.salary_rule_id.category_id.paid_by_company', 'line_ids.total')
    def _compute_company_cost(self):
        for r in self:
            r.company_cost = sum(r._get_cost_lines().mapped('total'))

    @api.depends('line_ids.total', 'company_id')
    def _compute_net(self):
        for r in self:
            net_code = r.company_id.net_income_salary_rule_categ_id and r.company_id.net_income_salary_rule_categ_id.code or 'NET'
            r.net_salary = r._get_salary_line_total(net_code)

    def _get_salary_line_total(self, code):
        lines = self.line_ids.filtered(lambda line: line.code == code)
        return lines and sum([line.total for line in lines]) or 0.0

    def _compute_details_by_salary_rule_category(self):
        for payslip in self:
            payslip.details_by_salary_rule_category = payslip.mapped('line_ids').filtered(lambda line: line.category_id)

    def _compute_cost_lines(self):
        for r in self:
            r.cost_line_ids = r._get_cost_lines()

    def _compute_payslip_lines_count(self):
        for payslip in self:
            payslip.payslip_lines_count = len(payslip.line_ids)

    def _compute_working_month_calendar_lines_count(self):
        for r in self:
            r.working_month_calendar_lines_count = len(r.working_month_calendar_ids.line_ids)

    @api.constrains('date_from', 'date_to', 'contract_id')
    def _check_dates(self):
        for r in self:
            if r.date_from and r.date_to and r.date_from > r.date_to:
                raise ValidationError(_("The 'Date From' of the payslip '%s' must be earlier than its 'Date To'.") % r.name)

    @api.constrains('employee_id', 'payslip_run_id')
    def _check_employee_batch(self):
        for r in self.filtered(lambda slip: slip.employee_id and slip.payslip_run_id):
            if r.payslip_run_id.thirteen_month_pay:
                overlap_slips = r.payslip_run_id.slip_ids.filtered(
                    lambda slip: \
                        slip != r \
                        and slip.employee_id == r.employee_id \
                        )
            else:
                overlap_slips = r.payslip_run_id.slip_ids.filtered(
                    lambda slip: \
                        slip != r \
                        and slip.employee_id == r.employee_id \
                        and slip.date_from < r.date_to \
                        and slip.date_to > r.date_from
                        )
            if overlap_slips:
                raise UserError(_("There are more than 1 payslip for the employee '%s' in the payslip batch '%s'"
                                  " that overlaps the current one, which is not allowed.")
                                % (r.employee_id.display_name, r.payslip_run_id.display_name))

    @api.constrains('thirteen_month_pay', 'thirteen_month_pay_year')
    def _check_thirteen_month_pay_year(self):
        for r in self.filtered(lambda rec: rec.thirteen_month_pay):
            thirteen_month_pay_year = self.env['to.base'].validate_year(r.thirteen_month_pay_year)
            r._check_thirteen_month_pay_year_valid(thirteen_month_pay_year)

    def _check_thirteen_month_pay_year_valid(self, thirteen_month_pay_year):
        if thirteen_month_pay_year < 1970 or thirteen_month_pay_year >= 9999:
            raise UserError(_("The year must be between 1970 and 9998"))

    def _get_reported_timeoff(self):
        return self.mapped('working_month_calendar_ids.line_ids.leave_ids.holiday_id')

    def _set_timeoff_payslip_status(self):
        """
        Mark all the related time off records as Reported in payslips
        """
        timeoff_records = self._get_reported_timeoff().filtered(lambda h: not h.payslip_status)
        if timeoff_records:
            timeoff_records.write({
                'payslip_status': True
                })

    def _unset_timeoff_payslip_status(self):
        """
        Mark all the related time off records that are Reported in payslips as Not Reported in payslips
        """
        timeoff_records = self._get_reported_timeoff().filtered(lambda h: h.payslip_status)
        if timeoff_records:
            timeoff_records.write({
                'payslip_status': False
                })

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        rec = super(HrPayslip, self).copy(default)
        for l in self.input_line_ids:
            l.copy({'payslip_id': rec.id})
        for l in self.line_ids:
            l.copy({'slip_id': rec.id})
        return rec

    def action_payslip_verify(self):
        if not self.env.context.get('without_compute_sheet'):
            self.compute_sheet()
        for r in self:
            if r.state != 'draft':
                raise UserError(_("You may not be able to confirm the payslip '%s' while its status is not Draft.") % (r.name,))
        self._set_timeoff_payslip_status()
        return self.write({
            'state': 'verify',
            'date_confirmed':fields.Date.today(),
            })

    def action_payslip_done(self):
        for r in self:
            if r.state != 'verify':
                raise UserError(_("You cannot mark the payslip '%s' as done while it is not in Waiting state") % r.name)
        return self.write({'state': 'done'})

    def action_payslip_cancel(self):
        self._unset_timeoff_payslip_status()
        return self.write({'state': 'cancel'})

    def action_payslip_draft(self):
        for r in self:
            if r.state != 'cancel':
                raise UserError(_("You must cancel the payslip '%s' before you can set it to Draft.") % (r.name,))
        return self.write({'state': 'draft'})

    def refund_sheet(self):
        for payslip in self:
            copied_payslip = payslip.copy({
                'credit_note': not payslip.credit_note,
                'name': _('Refund: ') + payslip.name,
                'refund_for_payslip_id':payslip.id
                })
            number = copied_payslip.number or self.env['ir.sequence'].with_company(copied_payslip.company_id).next_by_code('salary.slip')
            copied_payslip.write({'number': number})
            copied_payslip.with_context(without_compute_sheet=True).action_payslip_verify()
        formview_ref = self.env.ref('to_hr_payroll.view_hr_payslip_form', False)
        treeview_ref = self.env.ref('to_hr_payroll.view_hr_payslip_tree', False)
        return {
            'name': _("Refund Payslip"),
            'view_mode': 'tree, form',
            'view_id': False,
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
            'views': [
                (treeview_ref and treeview_ref.id or False, 'tree'),
                (formview_ref and formview_ref.id or False, 'form')
                ],
            'context': {}
        }

    def check_done(self):
        return True

    def unlink(self):
        if any(self.filtered(lambda payslip: payslip.state not in ('draft', 'cancel'))):
            raise UserError(_('You cannot delete a payslip which is not draft or cancelled!'))
        return super(HrPayslip, self).unlink()

    def _prepare_working_month_calendar_lines_data(self, date):
        self.ensure_one()
        data = []
        cycle = self._get_salary_cycle()
        date_from = cycle._get_month_start_date(date).date()
        date_to = cycle._get_month_end_date(date).date()
        res_intervals = self.employee_id._get_resource_calendar_intervals(date_from, date_to)[self.employee_id]
        for contract, res_datas in res_intervals.items():
            for start, end, res_calendar in res_datas:
                if contract:
                    data.append(contract.with_context(resource_calendar_id=res_calendar)._prepare_payslip_working_month_calendar_line_data(start, end))
                else:
                    data.append(res_calendar._prepare_payslip_working_month_calendar_line_data(start, end))
        return data

    def _prepare_working_month_calendar_data(self, date):
        self.ensure_one()
        lines_vals_list = self._prepare_working_month_calendar_lines_data(date)
        cycle = self._get_salary_cycle()
        month_year_int = cycle._get_date_for_month_year_int(date)
        return {
            'month_int': month_year_int.month,
            'year_int': month_year_int.year,
            'salary_cycle_id': cycle.id,
            'payslip_id': self.id,
            'line_ids': [(0, 0, vals) for vals in lines_vals_list],
            }

    @api.depends('contract_id', 'contract_ids', 'employee_id', 'date_from', 'date_to')
    def _compute_working_month_calendars(self):
        for r in self:
            # unlink existing records
            vals_list = [(3, l.id) for l in r.working_month_calendar_ids]

            if r.contract_ids and r.employee_id and r.date_from and r.date_to:
                cycle = r._get_salary_cycle()
                for dt in cycle._get_month_start_dates(r.date_from, r.date_to):
                    vals = r._prepare_working_month_calendar_data(dt)
                    vals_list.append((0, 0, vals))
            r.working_month_calendar_ids = vals_list

    def _recompute_fields(self):
        self._compute_worked_days_line_ids()
        self._compute_working_month_calendars()
        self._compute_hr_payslip_contribution_line_ids()
        self._compute_input_line_ids()

    def compute_sheet(self):
        self.flush()
        if not self.ids:
            return
        if not self._context.get('do_not_recompute_fields', False):
            self._recompute_fields()

        for r in self:
            if r.state != 'draft':
                raise UserError(_("You must not compute payslip %s while its state is not Draft.") % r.display_name)

        # delete old payslip lines and old personal income taxes
        ids = tuple(self.ids)
        query = """
            DELETE FROM hr_payslip_line WHERE slip_id IN %s;
            DELETE FROM payslip_personal_income_tax WHERE slip_id IN %s;
            """
        self.env.cr.execute(query, (ids, ids,))
        self.invalidate_cache(['line_ids', 'payslip_personal_income_tax_ids'])

        lines_vals_list = []
        query = ""
        self.read(['id', 'state', 'display_name', 'company_id', 'number', 'personal_tax_rule_id'])

        for payslip in self:
            if not payslip.number:
                number = self.env['ir.sequence'].with_company(payslip.company_id).next_by_code('salary.slip')
                query += """UPDATE hr_payslip SET number='%s' WHERE id=%s;""" % (number, payslip.id)

            for line in payslip._get_payslip_lines():
                line.update({'slip_id': payslip.id})
                lines_vals_list.append(line)
        if query:
            self.env.cr.execute(query)
            self.invalidate_cache(['number'])
        self.env['hr.payslip.line'].create(lines_vals_list)
        self.invalidate_cache(['line_ids'])

        # compute personal tax breaks table
        # IMPORTANT: since the the tax breaks table relies on salary rules computation,
        # the code below must be executed after salary rules computation
        taxes_vals_list = []
        for r in self.filtered(lambda r: r.personal_tax_rule_id):
            for vals in r.personal_tax_rule_id._prepare_payslip_personal_income_tax_data(r):
                vals.update({'slip_id': r.id})
                taxes_vals_list.append(vals)
        if taxes_vals_list:
            self.env['payslip.personal.income.tax'].create(taxes_vals_list)
            self.invalidate_cache(['payslip_personal_income_tax_ids'])

        return True

    def _get_salary_cycle(self):
        self.ensure_one()
        return self.salary_cycle_id or self.company_id.salary_cycle_id or self.env.ref('to_hr_payroll.hr_salary_cycle_default')

    def _get_payslips_for_13thmonth(self):
        self.ensure_one()
        if self.employee_id and self.thirteen_month_pay and self.thirteen_month_pay_year > 1970:
            payslips = self.employee_id._get_payslips_of_year(self.thirteen_month_pay_year).filtered(lambda p: not p.thirteen_month_pay)
        else:
            payslips = self
        if not self.thirteen_month_pay_include_trial:
            payslips = payslips.filtered(lambda p: \
                              not p.contract_id.trial_date_end \
                              or (p.contract_id.trial_date_end and p.date_from >= p.contract_id.trial_date_end))
        return payslips

    def _prepare_baselocaldict(self, rules_dict):
        self.ensure_one()
        employee = self.employee_id
        # to be available in salary rule python code
        import datetime
        import dateutil
        return {
            'datetime': wrap_module(datetime, ['date', 'datetime', 'time', 'timedelta', 'timezone', 'tzinfo', 'MAXYEAR', 'MINYEAR']),
            'dateutil': wrap_module(dateutil, {
                mod: getattr(dateutil, mod).__all__
                for mod in ['parser', 'relativedelta', 'rrule', 'tz']}),
            'fields': wrap_module(fields, []),
            'env': self.env,
            'categories': BrowsableObject(employee.id, {}, self.env),
            'rules': BrowsableObject(employee.id, rules_dict, self.env),
            'payslip': Payslips(employee.id, self, self.env),
            'payslips_for_13thmonth': self._get_payslips_for_13thmonth(),
            'working_month_calendar_lines': self.working_month_calendar_ids.line_ids,
            'worked_days': self.worked_days_line_ids.get_workedday_obj(),
            'advantages': self.contract_id.get_advatages_obj(),
            'timeoff': self.working_month_calendar_ids.line_ids.leave_ids,
            'contributions': self.hr_payslip_contribution_line_ids.get_contributionline_obj(),
            'inputs': self.input_line_ids.get_inputline_obj(),
            'hasattr': hasattr,
            'getattr': getattr,
            }

    def _prepare_localdict(self, rules_dict):
        return dict(self._prepare_baselocaldict(rules_dict), employee=self.contract_id.employee_id, contract=self.contract_id)

    def _get_payslip_lines(self):
        self.ensure_one()
        # get the ids of the structures on the contracts and their parent id as well
        if self.struct_id:
            structures = self.struct_id._get_parent_structure()
        else:
            structures = self.contract_id.get_all_structures()
        # get the rules of the structure and thier children
        rule_ids = structures.mapped('rule_ids').sorted(key='sequence', reverse=False)

        # IMPORTANT: we keep a dict with the result because a value can be overwritten by another rule with the same code
        rules_dict = {}
        localdict = self._prepare_localdict(rules_dict)
        return rule_ids._prepare_payslip_lines_data(localdict, self.contract_id, rules_dict)

    @api.depends('thirteen_month_pay', 'thirteen_month_pay_year', 'date_from')
    def _compute_name(self):
        for r in self:
            r.name = r._get_salary_slip_name()

    def _get_salary_slip_name(self, employee=None, date_to=None):
        employee = employee or self.employee_id
        employee_name = employee and employee.name or _("Unknown")
        thirteen_month_pay = self._context.get('thirteen_month_pay', False) or self.thirteen_month_pay
        thirteen_month_pay_year = self._context.get('thirteen_month_pay_year', False) or self.thirteen_month_pay_year
        if thirteen_month_pay and thirteen_month_pay_year:
            return _("13th-Month Salary of %s for the year %s") % (employee_name, str(thirteen_month_pay_year))
        else:
            date_to = date_to or self.date_to
            return _('Salary Slip of %s for %s') % (employee_name, format_date(self.env, date_to, date_format='MMMM-y'))

    def sorted_by_dates(self, reverse=False):
        """
        This method sorts payslips in self by their date_from and date_to
        """
        return self.sorted(lambda r: (
            datetime.timestamp(datetime.combine(r.date_from, time.min)),
            datetime.timestamp(datetime.combine(r.date_to, time.max))
            ), reverse=reverse)

    def _get_dates(self, reverse=False):
        dates = []
        for payslip in self:
            if payslip.date_from not in dates:
                dates.append(payslip.date_from)
            if payslip.date_to not in dates:
                dates.append(payslip.date_to)
        dates.sort(reverse=reverse)
        return dates

    @api.depends('contract_id', 'thirteen_month_pay')
    def _compute_struct(self):
        for r in self:
            struct = r.contract_id.struct_id if r.contract_id.struct_id else False
            if r.thirteen_month_pay and r.contract_id.thirteen_month_struct_id:
                struct = r.contract_id.thirteen_month_struct_id
            r.struct_id = struct

    @api.depends('contract_ids', 'date_from', 'date_to')
    def _compute_worked_days_line_ids(self):
        for r in self:
            command = []
            if not r.employee_id or not r.date_from or not r.date_to:
                command += [(5, 0, 0)]
            else:
                worked_days_line_vals = r.contract_ids.get_worked_day_lines(r.date_from, r.date_to)
                command += [(5, 0, 0)]
                for line in worked_days_line_vals:
                    command.append((0, 0, line))
            r.worked_days_line_ids = command

    @api.depends('contract_id', 'struct_id')
    def _compute_input_line_ids(self):
        for r in self:
            command = []
            existing_input_lines = r._origin.input_line_ids if r._origin else r.input_line_ids
            # we always keep manual input lines that are not generated by salary rules
            to_keep = existing_input_lines.filtered(lambda l: not l.salary_rule_id)

            if r.contract_id and r.struct_id:
                to_check = existing_input_lines - to_keep
                input_line_vals_list = r.struct_id._get_inputs(r.contract_id)
                for vals in input_line_vals_list:
                    # we also keep input lines that match the lines generated by salary rules
                    existings = to_check.filtered(
                        lambda existing: \
                            vals.get('salary_rule_id', 0) == existing.salary_rule_id.id \
                            and vals.get('code', False) == existing.code
                            )
                    if existings:
                        to_keep |= existings
                    else:
                        command.append((0, 0, vals))
            # add to-keep lines to the command
            command = [(4, line.id) for line in to_keep] + command
            # remove to remove lines
            command = [(3, line.id) for line in (existing_input_lines - to_keep)] + command
            r.input_line_ids = command

    @api.depends('date_from', 'date_to', 'contract_ids')
    def _compute_hr_payslip_contribution_line_ids(self):
        for r in self:
            command = [(3, line.id) for line in r.hr_payslip_contribution_line_ids]
            if r.contract_ids and r.date_from and r.date_to:
                command += r.contract_ids._prepare_hr_payslip_contribution_lines_data(r.date_from, r.date_to)

            r.hr_payslip_contribution_line_ids = command

    def _compute_employee_partner_id(self):
        for r in self:
            r.employee_partner_id = r.employee_id.user_id.partner_id or r.employee_id.sudo().address_home_id

    def _compute_employee_lang(self):
        for r in self:
            r.employee_lang = r.employee_partner_id.lang or self.env.lang

    def action_view_refunds(self):
        '''
        This function returns an action that display existing refund payslips of the given payslips.
        When only one found, show the refund immediately.
        '''
        action = self.env['ir.actions.act_window']._for_xml_id('to_hr_payroll.action_view_hr_payslip_form')

        refund_ids = self.mapped('refund_ids')

        # choose the view_mode accordingly
        if len(refund_ids) != 1:
            action['domain'] = "[('refund_for_payslip_id', 'in', %s)]" % str(self.ids)
        elif len(refund_ids) == 1:
            res = self.env.ref('to_hr_payroll.view_hr_payslip_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = refund_ids.id
        return action

    def action_view_hr_working_month_calendar_lines(self):
        action = self.env['ir.actions.act_window']._for_xml_id('to_hr_payroll.act_hr_working_month_calendar_line_view_list')
        action['context'] = {}
        action['domain'] = "[('working_month_calendar_id.payslip_id','in',%s)]" % str(self.ids)
        return action

    def action_payslip_send(self):
        template = self.env.ref('to_hr_payroll.email_template_payslip', raise_if_not_found=False)
        if template:
            for r in self:
                r.with_context(force_send=True).sudo().message_post_with_template(
                    template.id,
                    composition_mode='comment',
                    # email_layout_xmlid="mail.mail_notification_paynow"
                    )

    def action_payslip_send_wizard(self):
        '''
        This function opens a window to compose an email, with the payslip batch template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template = self.env.ref('to_hr_payroll.email_template_payslip', raise_if_not_found=False)
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'hr.payslip',
            'default_res_id': self.ids[0],
            'default_use_template': template and template.id or False,
            'default_template_id': template and template.id or False,
            'default_composition_mode': 'comment',
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
