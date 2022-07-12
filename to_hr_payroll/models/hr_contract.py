import logging

from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone

from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError

from .browsable_object import Advantages

_logger = logging.getLogger(__name__)

TAX_POLICY = [
    ('escalation', 'Progressive Tax Table'),
    ('flat_rate', 'Flat Rate')
    ]


class HrContract(models.Model):
    """
    Employee contract based on the visa, work permits
    allows to configure different Salary structure
    """
    _inherit = 'hr.contract'

    # override the field `wage` for new label and help string
    # by default in the module `hr_contract`, this field is considered as gross wage.
    # Howver, our module `to_hr_payroll` considers this as basic wage without any allowance and advantages
    wage = fields.Monetary('Basic Wage', tracking=True, help="Employee's monthly basic wage (without any allowance and advantages).")

    struct_id = fields.Many2one('hr.payroll.structure', tracking=True, string='Salary Structure', domain="[('company_id','=',company_id)]", ondelete='restrict')
    thirteen_month_struct_id = fields.Many2one('hr.payroll.structure', tracking=True, string='13th-Month Salary Structure',
                                                domain="[('company_id','=',company_id)]", ondelete='restrict',
                                                help="If specified, thirteen-month payslips of this contract will use this structure instead of the default Salary Structure above specified.")
    resource_calendar_id = fields.Many2one(required=True, tracking=True, help="Employee's working schedule.")
    advantage_ids = fields.One2many('hr.contract.advantage', 'contract_id', string='Monthly Advantages', auto_join=True)
    gross_salary = fields.Monetary(string='Gross Salary', compute='_compute_gross_sal', store=True, tracking=True)
    payroll_contribution_type_ids = fields.Many2many('hr.payroll.contribution.type', string='Payroll Contribution Types',
                                                     domain="['|', ('company_id','=',False), ('company_id','=',company_id)]",
                                                     help="The types of payroll contribution to be applied to the contract."
                                                     " For example, you could create contribution types such as Employee Social Insurance,"
                                                     " Employee Unemployment Insurance, etc.")
    payroll_contribution_register_ids = fields.Many2many('hr.payroll.contribution.register',
                                                         'hr_contract_payroll_contribution_register_rel', 'contract_id', 'register_id',
                                                         compute='_compute_payroll_contribution_registers', store=True,
                                                         string='Payroll Contribution Registers')
    personal_tax_policy = fields.Selection(TAX_POLICY,
                                           string='Personal Tax Policy', required=True, default='escalation', tracking=True,
                                           help="The taxation policy applied to the net income of the payslips of this contract.\n"
                                           "- Progressive Tax Table: the tax rate varies according to the country's escalation taxation policy"
                                           " which is defined in Configuration > Personal Tax Rules;\n"
                                           "- Flat Rate: No matter how much the income is, a flat rate defined in Configuration"
                                           " > Personal Tax Rules will always  be applied.")
    personal_tax_rule_id = fields.Many2one('personal.tax.rule', string='Tax Rule', domain="[('personal_tax_policy', '=', personal_tax_policy)]",
                                           compute='_get_tax_rule', store=True, readonly=False, tracking=True,
                                           help="The personal income tax rule applied to payslips of this contract")
    payslip_ids = fields.Many2many('hr.payslip', 'hr_payslip_hr_contract_rel', 'contract_id', 'payslip_id',
                                   help="Payslips related to this contract")
    payslips_count = fields.Integer(string='Payslips Count', compute='_compute_payslips_count')
    salary_computation_mode = fields.Selection([
        ('hour_basis', 'Hour Basis'),
        ('day_basis', 'Day Basis')
        ], string='Salary Computation Mode', required=True, tracking=True, default='hour_basis',
        help="How the employee salary would be computed in salary rules, based on either working days or working hours:\n"
        "* Hour Basis: salary would be computed based on working hours;\n"
        "* Day Basis: salary would be computed based on working days;\n")
    salary_attendance_computation_mode = fields.Selection([
        ('timeoff', 'Time-Off Registration'),
        ], string='Salary Attendance Computation Mode', required=True, tracking=True, default='timeoff',
        help="How the employee worked hours would be computed in salary rules, based on either Time-Off registration or"
        " attendance data (depending on the availability of the module `to_hr_payroll_attendance`):\n"
        "* Time-Off Registration: worked hours (and days) and the paid rate will be computed correspondingly based on the"
        " formulas `Duty Working Hours (or Days) - Leave Hours (or Days)` and `(Duty Working Hours (or Days) - Unpaid"
        " Leave Hours (or Days)) / Working Hours (or Days) in Full Month`;\n"
        "* Attendance Entries: worked hours (and days) and the paid rate will be computed using attendance data."
        " This requires module `to_hr_payroll_attendance` to be installed;\n")
    payslips_auto_generation = fields.Boolean(string='Payslips Auto-Generation', compute='_compute_payslips_auto_generation', store=True, readonly=False,
                                              help="If enabled, and allowed by the company's settings, payslips will be generated for this contract accordingly.",
                                              states={'cancel': [('readonly', True)]})

    @api.depends('company_id')
    def _compute_payslips_auto_generation(self):
        for r in self:
            r.payslips_auto_generation = r.company_id.payslips_auto_generation

    @api.depends('wage', 'advantage_ids', 'advantage_ids.amount')
    def _compute_gross_sal(self):
        for r in self:
            r.gross_salary = r.wage + sum(r.advantage_ids.mapped('amount'))

    @api.depends('personal_tax_policy', 'company_id')
    def _get_tax_rule(self):
        # TODO: rename this into _compute_tax_rule in master/14+
        tax_rules = self.env['personal.tax.rule'].search([
            ('country_id', 'in', self.company_id.country_id.ids),
            ('personal_tax_policy', 'in', self.mapped('personal_tax_policy'))
            ])
        for r in self:
            r.personal_tax_rule_id = tax_rules.filtered(
                lambda rule: \
                rule.country_id == r.company_id.country_id \
                and rule.personal_tax_policy == r.personal_tax_policy
                )[:1]

    def generate_payroll_contribution_registers(self):
        for r in self.filtered(lambda c: c.payroll_contribution_type_ids):
            if not r.employee_id:
                raise UserError(_("Please select an employee first!"))
            existing_types = r.mapped('payroll_contribution_register_ids.type_id')
            vals_list = []
            for contribution_type in r.payroll_contribution_type_ids.filtered(lambda t: t.id not in existing_types.ids):
                vals_list.append(contribution_type._prepare_payroll_contribution_register_data(r))
            if vals_list:
                payroll_contribution_register_ids = self.env['hr.payroll.contribution.register'].create(vals_list)
                r.write({
                    'payroll_contribution_register_ids': [(4, reg.id) for reg in payroll_contribution_register_ids]
                    })

    def _get_contribution_advantages(self):
        return self.advantage_ids.filtered(lambda adv: adv.included_in_payroll_contribution_register)

    def _get_payroll_contribution_base(self):
        self.ensure_one()
        return self.wage + sum(self._get_contribution_advantages().mapped('amount'))

    @api.depends('employee_id', 'payroll_contribution_type_ids')
    def _compute_payroll_contribution_registers(self):
        all_registers = self.env['hr.payroll.contribution.register'].search(self._get_payroll_contribution_register_domain())
        for r in self:
            registers = all_registers.filtered(lambda reg: reg.employee_id == r.employee_id and reg.type_id.id in r.payroll_contribution_type_ids.ids)
            r.payroll_contribution_register_ids = [(6, 0, registers.ids)]

    def _compute_payslips_count(self):
        for r in self:
            r.payslips_count = len(r.payslip_ids)

    def _get_payroll_contribution_register_domain(self):
        return [
            ('employee_id', 'in', self.employee_id.ids),
            ('type_id', 'in', self.payroll_contribution_type_ids.ids)
            ]

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by hierarchy (parent=False first,
                 then first level children and so on) and without duplication
        """
        structures = self.mapped('struct_id') if not self._context.get('thirteen_month_pay', False) else self.mapped('thirteen_month_struct_id')
        if not structures:
            return self.env['hr.payroll.structure']
        structure_ids = list(set(structures._get_parent_structure().ids))
        return self.env['hr.payroll.structure'].browse(structure_ids)

    def get_worked_day_lines(self, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in self.filtered(lambda contract: contract.resource_calendar_id):
            
            # get the valid time between contract and payslip period to calculate the work and leave time
            date_start, date_end = contract._qualify_interval(date_from, date_to)
            day_from = datetime.combine(date_start, time.min)
            day_to = datetime.combine(date_end, time.max)

            # compute leave days
            leave_lines = {}
            calendar = contract.resource_calendar_id
            tz = timezone(calendar.tz)
            day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=contract.resource_calendar_id)

            seen = self.env['resource.calendar.leaves']
            for date, __, minor_leaves in day_leave_intervals:
                # Calculate number of work hours of the date that the employee has to work
                work_hours = calendar.get_work_hours_count(
                    tz.localize(datetime.combine(date, time.min)),
                    tz.localize(datetime.combine(date, time.max)),
                    compute_leaves=True,  # take global leaves into account
                    )

                # ignore leaves that are seen and global
                for leave in minor_leaves.filtered(lambda l: l not in seen and l.holiday_id):
                    
                    # divide the valid leave period
                    leave_date_from = leave.date_from
                    leave_date_to = leave.date_to
                    if contract.date_start > leave_date_from.date():
                        leave_date_from = datetime.combine(contract.date_start, time.min)
                    if contract.date_end and contract.date_end < leave_date_to.date():
                        leave_date_to = datetime.combine(contract.date_end, time.max)
                    
                    leave_intervals = contract.employee_id.list_leaves(
                            leave_date_from,
                            leave_date_to,
                            calendar=contract.resource_calendar_id
                        )
                    current_leave_struct = leave_lines.setdefault(leave.holiday_id.holiday_status_id, {
                        'name': leave.holiday_id.holiday_status_id.name or _('Global Leaves'),
                        'sequence': 5,
                        'code': leave.holiday_id.holiday_status_id.code or 'GLOBAL',
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'contract_id': contract.id,
                    })
                    
                    for __, leave_hours, __ in leave_intervals:
                        current_leave_struct['number_of_hours'] += leave_hours
                        if not float_is_zero(work_hours, precision_digits=2):
                            current_leave_struct['number_of_days'] += leave_hours / work_hours
                    seen += leave

            # compute worked days
            work_data = contract.employee_id._get_work_days_data(day_from, day_to, compute_leaves=True, calendar=contract.resource_calendar_id)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leave_lines.values())
        return res

    def _get_inputs(self, date_from, date_to):
        """
        TODO: remove in 14/master
        This is kept for backward compatibility
        @deprecated: to be remove in 14/master
        """
        _logger.warning("The method contract._get_inputs(date_from, date_to) is deprecated."
                     " Please use struct._get_inputs(contract) instead.")
        res = []

        structure_ids = self.get_all_structures()
        rule_ids = structure_ids.get_all_rules()
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
        inputs = self.env['hr.salary.rule'].browse(sorted_rule_ids).mapped('input_ids')

        for contract in self:
            for input in inputs:
                input_data = {
                    'name': input.name,
                    'code': input.code,
                    'contract_id': contract.id,
                }
                res += [input_data]
        return res

    def _prepare_contrib_history_date_breaks(self, date_from=None, date_to=None):
        """
        Breaks the contribution period by months, and according with the periods of contracts.
        """
        ToBase = self.env['to.base']
        date_breaks = []
        last_break = None
        for r in self.sorted('date_start'):
            if date_to < r.date_start or r.date_end and date_from > r.date_end:
                continue
            dt_from, dt_to = r._qualify_interval(date_from, date_to)
            contract_date_breaks = ToBase.period_iter(period_name='monthly', dt_start=dt_from, dt_end=dt_to)
            # If last break point is the connect date between old an new contracts, and it is not
            # the start of month, we should remove that break point because in real, the contribution
            # is still running without any gaps.
            if last_break and last_break == contract_date_breaks[0]:
                contract_date_breaks.pop(0)
                if last_break.day != 1:
                    date_breaks.pop()
            date_breaks += contract_date_breaks
            last_break = date_breaks[-1] + relativedelta(days=1)
        date_breaks = list(set(date_breaks))
        date_breaks.sort()
        return date_breaks

    def _prepare_hr_payslip_contribution_lines_data(self, date_from=None, date_to=None):
        self.employee_id.ensure_one()
        hr_payslip_contribution_line_data = []
        History = self.env['hr.payroll.contribution.history']
        
        domain = [
            ('employee_id', '=', self.employee_id.id),
            ('payroll_contribution_reg_id', 'in', self.payroll_contribution_register_ids.ids),
            ('date_from', '<=', date_to),
            '|', ('date_to', '=', False), ('date_to', '>', date_from)]
        
        for line in History.search(domain):
            last_dt = None
            contrib_from = max(line.date_from, date_from)
            contrib_to = min(line.date_to, date_to) if line.date_to else date_to
            for dt in self._prepare_contrib_history_date_breaks(contrib_from, contrib_to):
                if not last_dt:
                    last_dt = dt
                    continue
                dt_from = max(line.date_from, last_dt)
                dt_to = min(line.date_to, dt) if line.date_to else dt
                new_line_data = line._prepare_hr_payslip_contribution_line_data(self, dt_from, dt_to)
                hr_payslip_contribution_line_data.append((0, 0, new_line_data))
                last_dt = dt + relativedelta(days=1)
        
        return hr_payslip_contribution_line_data

    def _get_applicable_payslip_dates(self, date_from, date_to):
        """
        This method provides applicable date_from and date_to for the payslip and its related
        computation to ensure that the date_from will not be earlier than the corresponding
        contract's start date and the date_to will not be later than the corresponding contract's
        end date
        """
        # TODO: remove me in master/14+
        _logger.warning("The method `contract._get_applicable_payslip_dates(date_from, date_to)` is deprecated."
                     " Please use `contract._qualify_interval(date_from, date_to)` instead.")
        return self._qualify_interval(date_from, date_to)
    
    def _prepare_payslip_working_month_calendar_line_data(self, date_from, date_to):
        self.ensure_one()
        date_from, date_to = self._qualify_interval(date_from, date_to)
        resource_calendar_id = self._context.get('resource_calendar_id', False) or self.resource_calendar_id
        vals = resource_calendar_id._prepare_payslip_working_month_calendar_line_data(date_from, date_to)
        vals['contract_id'] = self.id
        return vals

    def _prepare_payslip_working_month_calendar_line_vals_list(self, date_from, date_to):
        vals_list = []
        self = self.sorted('date_start')
        last_contract = self[-1:]
        for contract in self:
            # prepare pre-contract calendar line data
            if date_from < contract.date_start:
                vals = contract.resource_calendar_id._prepare_payslip_working_month_calendar_line_data(date_from, contract.date_start - relativedelta(days=1))
                vals_list.append(vals)
                date_from = contract.date_start
            # prepare contract calendar line data for the contract period
            vals = contract._prepare_payslip_working_month_calendar_line_data(date_from, date_to)
            vals_list.append(vals)
            # set date_from for the next contract
            if contract.date_end:
                date_from = contract.date_end + relativedelta(days=1)
                # prepare post-contract calendar line data for the the last contract
                if contract == last_contract and date_to > contract.date_end:
                    vals = contract.resource_calendar_id._prepare_payslip_working_month_calendar_line_data(date_from, date_to)
                    vals_list.append(vals)
        return vals_list

    def _prepare_payslip_data(self, date_from, date_to):
        self.ensure_one()
        payslip_run_id = self._context.get('payslip_run_id', False)
        credit_note = self._context.get('credit_note', False)
        thirteen_month_pay = self._context.get('thirteen_month_pay', False)
        thirteen_month_pay_year = self._context.get('thirteen_month_pay_year', False)
        thirteen_month_pay_include_trial = self._context.get('thirteen_month_pay_include_trial', False)
        date_from, date_to = self._qualify_interval(date_from, date_to)
        res = {
            # 'details_by_salary_head':[], TODO put me back
            'name': self.env['hr.payslip'].with_context(
                thirteen_month_pay=thirteen_month_pay,
                thirteen_month_pay_year=thirteen_month_pay_year
                )._get_salary_slip_name(self.employee_id, date_to),
            'contract_id': self.id,
            'struct_id': self.struct_id.id,
            'company_id': self.employee_id.company_id.id,
            'employee_id': self.employee_id.id,
            'payslip_run_id': payslip_run_id,
            'date_from': date_from,
            'date_to': date_to,
            'credit_note': credit_note,
            'thirteen_month_pay': thirteen_month_pay,
            'thirteen_month_pay_year': thirteen_month_pay_year,
            'thirteen_month_pay_include_trial': thirteen_month_pay_include_trial
        }
        return res

    def action_view_payslips(self):
        action = self.env.ref('to_hr_payroll.act_hr_employee_payslip_list')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        result['context'] = {
            'default_employee_id': self.employee_id.id,
            'default_contract_id': self.id,
            'default_company_id': self.company_id.id
            }

        # choose the view_mode accordingly
        if self.payslips_count != 1:
            result['domain'] = "[('contract_id', 'in', %s)]" % str(self.ids)
        elif self.payslips_count == 1:
            res = self.env.ref('to_hr_payroll.view_hr_payslip_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.payslip_ids.id
        return result

    @api.onchange('job_id')
    def _onchange_job_id(self):
        job_id = self.job_id
        if self.job_id:
            self.wage = job_id.wage
            self.struct_id = job_id.struct_id
            self.resource_calendar_id = job_id.resource_calendar_id

    def get_advatages_obj(self):
        """
        Get an Advantages object for usage in salary rule python code
        @return: Advantages object
        @rtype: Advantages
        """
        self.ensure_one()
        advatages_dict = {}
        for advantage in self.advantage_ids:
            advatages_dict[advantage.code] = advantage
        return Advantages(self.employee_id.id, advatages_dict, self.env)

    def unlink(self):
        for r in self:
            if r.payslip_ids:
                raise UserError(_("You cannot delete the contract %s while it is still referred by the payslip %s."
                                  " It is required to delete all the related payslip first. Or, you could close/"
                                  "cancel the contract.")
                                % (r.name, r.payslip_ids[0].name))
        return super(HrContract, self).unlink()

    def _get_trial_period(self):
        """
        Get the trial period of the contract, if applicable
        
        :return: (trial_date_start, trial_date_end) in tuple of datetime.datetime or (None, None)
        :rtype: tuple
        """
        self.ensure_one()
        if self.trial_date_end and self.trial_date_end >= self.date_start:
            trial_date_start = datetime.combine(self.date_start, time.min)
            trial_date_end = datetime.combine(self.trial_date_end, time.max)
            return trial_date_start, trial_date_end
        else:
            return None, None

