from datetime import datetime, time
from pytz import utc

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import date_utils, format_datetime, relativedelta

from .res_company import OVERTIME_RECOGNITION_MODE


class HrOvertimePlan(models.Model):
    _name = 'hr.overtime.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Overtime Plan"
    _rec_name = 'employee_id'
    _check_company_auto = True

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env.user.employee_id

    employee_id = fields.Many2one('hr.employee', string='Employee', default=_default_employee, domain=lambda self: self._get_employee_domain(),
                                  required=True, tracking=True,
                                  check_company=True)
    reason_id = fields.Many2one('hr.overtime.reason', string='Reason', required=True, tracking=True)
    # these date and time fields are for better UI and UX
    date = fields.Date(string='Date', required=True, default=fields.Date.today, help="The date on which the overtime work happens.")
    time_start = fields.Float(string='Start Time', default=0.0, required=True,
                              help="The time on the date specified in the Date at which the overtime work starts.")
    time_end = fields.Float(string='End Time', default=0.01, required=True,
                            help="The time on the date specified in the Date at which the overtime work ends.")

    date_start = fields.Datetime(string='Start Date', compute='_compute_date_start', required=True, store=True, readonly=False, tracking=True,
                                 help="The date and time at which the overtime work starts.")
    date_end = fields.Datetime(string='End Date', compute='_compute_date_end', required=True, store=True, readonly=False, tracking=True,
                               help="The date and time at which the overtime work ends.")
    recognition_mode = fields.Selection(OVERTIME_RECOGNITION_MODE, string='Force Recognition Mode', compute='_compute_recognition_mode', store=True, tracking=True,
                                        readonly=False, help="This indicates mode to recognize actual overtime against the plan which could be either"
                                        " By Plan or Attendance or Timesheet. Bridging modules will be required to have full"
                                        " options accordingly.\n"
                                        "Note: If not specified, the setting from the corresponding contract or company will be taken into account.")
    can_recognize = fields.Boolean(string='Can Recognize', compute='_compute_can_recognize',
                                   help="Technical field to indicate if this plan can get actual overtime recognized when it contains"
                                   " a line having overtime work to be measured with either attendance or timesheet.")
    contract_ids = fields.Many2many('hr.contract', 'hr_overtime_plan_contract_rel', 'overtime_plan_id', 'contract_id',
                                    string='Contracts', compute='_compute_contract_ids', store=True, groups="hr_contract.group_hr_contract_manager",
                                    help="The related employee contracts that match the Start Date and the End Date.")
    line_ids = fields.One2many('hr.overtime.plan.line', 'overtime_plan_id', string='Plan Lines',
                               compute='_compute_line_ids', store=True, auto_join=True,
                               help="Store the detail plan lines that generated by this plan according to the affected contracts"
                               " and the predefined overtime rules")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, required=True, tracking=True)
    currency_id = fields.Many2one(related='company_id.currency_id')
    no_contract_warning_text = fields.Char(string='No Contract Warning Text', compute='_compute_no_contract_warning_text', compute_sudo=True)
    planned_hours = fields.Float(string='Planned Hours', compute='_compute_planned_hours', store=True,
                                 help="Total planned hours for overtime registration")
    actual_hours = fields.Float(string='Actual Overtime Hours', compute='_compute_actual_hours', store=True,
                                help="The actual overtime hours recognized by selected Recognition Mode (e.g. By Plan, Attendance, etc)."
                                " If 'By Plan' is selected, the actual overtime hours will be the planned hours. Otherwise, the"
                                " actual overtime hours will be recognized by the affected mode accordingly.")
    planned_overtime_pay = fields.Monetary(string='Planned Overtime Pay', compute='_compute_planned_overtime_pay', store=True,
                                           groups="hr_contract.group_hr_contract_manager",
                                           help="The planned overtime cost that is computed automatically based on the planned overtime hours.")
    actual_overtime_pay = fields.Monetary(string='Actual Overtime Pay', compute='_compute_actual_overtime_pay', store=True,
                                          groups="hr_contract.group_hr_contract_manager",
                                          help="The actual overtime cost that is computed automatically based on the actual recognized"
                                          " overtime hours.")
    has_non_draft_payslips = fields.Boolean(string='Included in Non-Draft Payslip', compute='_compute_has_non_draft_payslips', compute_sudo=True,
                                            help="This indicates if there is a non-draft payslip reffering to this plan.")
    readonly = fields.Boolean(string='Readonly', compute='_compute_read_only', compute_sudo=True, help="Technical field to compute readonly state for the views")
    mismatched_contract_ids = fields.Many2many('hr.contract', 'hr_contract_overtime_plan_mismatch_rel', 'plan_id', 'contract_id',
                                                    string='Mismatched Contracts', readonly=True,
                                                    help="This technical field stores contracts that mismatch this plan.")

    _sql_constraints = [
        ('times_check', "CHECK (time_start < time_end)", "The Start Time must be anterior to the End Time."),
        ('time_start_check', "CHECK (time_start >= 0 and time_start < 24)", "The Start Time must be greater than or equal to 0 and less than 24."),
        ('time_start_check', "CHECK (time_end > 0 and time_end <= 24)", "The End Time must be greater than 0 and less than or equal to 24."),
        ('date_check', "CHECK (date_start < date_end)", "The Start Date must be anterior to the End Date."),
    ]

    def unlink(self):
        self.line_ids.with_context(force_delete=True).unlink()
        return super(HrOvertimePlan, self).unlink()

    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        raise UserError(_("Duplicating an overtime plan is not allowed."))

    @api.model
    def _get_employee_domain(self):
        if not self.env.user.has_group('viin_hr_overtime.group_overtime_team_approval'):
            domain = [('id', '=', self.env.context.get('default_employee_id') or self.env.user.employee_id.id)]
        elif not self.env.user.has_group('viin_hr_overtime.group_overtime_officer'):
            domain = [('id', 'in', self.env.user.employee_id.subordinate_ids.ids + [self.env.user.employee_id.id])]
        else:
            domain = []
        return domain

    @api.depends('reason_id')
    def _compute_recognition_mode(self):
        for r in self:
            r.recognition_mode = r.reason_id.recognition_mode

    @api.depends('date', 'time_start')
    def _compute_date_start(self):
        float_hours_to_time = self.env['to.base'].float_hours_to_time
        for r in self:
            if not r.date:
                r.date_start = fields.Datetime.now()
            else:
                if r.time_start < 0:
                    r.time_start = 0
                if r.time_start > 24:
                    r.time_start = 24
                if r.time_start == 24:
                    date_start = datetime.combine(r.date + relativedelta(days=1), time.min)
                else:
                    date_start = datetime.combine(r.date, float_hours_to_time(r.time_start))
                utc = self.env['to.base'].convert_time_to_utc(
                    date_start,
                    tz_name=self.env.user.tz if self.env.user.tz else 'UTC',
                    naive=True
                    )
                r.date_start = utc
    
    @api.depends('date', 'time_end')
    def _compute_date_end(self):
        float_hours_to_time = self.env['to.base'].float_hours_to_time
        for r in self:
            if not r.date:
                r.date_end = fields.Datetime.now()
            else:
                if r.time_end < 0:
                    r.time_end = 0.01
                if r.time_end > 24:
                    r.time_end = 24
                if r.time_end == 24:
                    date_end = datetime.combine(r.date + relativedelta(days=1), time.min)
                else:
                    date_end = datetime.combine(r.date, float_hours_to_time(r.time_end))
                utc = self.env['to.base'].convert_time_to_utc(
                    date_end,
                    tz_name=self.env.user.tz if self.env.user.tz else 'UTC',
                    naive=True
                    )
                r.date_end = utc

    @api.depends('contract_ids')
    def _compute_no_contract_warning_text(self):
        for r in self:
            no_contract_warning_text = False
            if not r.contract_ids and r.employee_id and r.date_start and r.date_end:
                no_contract_warning_text = _("No valid contracts (that are either running or expired)"
                                             " found for the given overtime period, causing this plan become useless!")
            r.no_contract_warning_text = no_contract_warning_text

    @api.depends('employee_id', 'date_start', 'date_end')
    def _compute_contract_ids(self):
        next_1000_years = fields.Date.today() + date_utils.relativedelta(years=1000)
        for r in self:
            if not r.date_start or not r.date_end or not r.employee_id:
                contracts = False
            else:
                contracts = r.employee_id.contract_ids.filtered(
                    lambda c: \
                    datetime.combine(c.date_end or next_1000_years, time.max) > r.date_start \
                    and datetime.combine(c.date_start, time.min) < r.date_end \
                    and c.state in ('open', 'close')
                    ).sorted(lambda c: (c.date_start, c.date_end or next_1000_years))
            r.contract_ids = contracts and contracts.ids or False
    
    @api.depends('date_start', 'date_end', 'contract_ids')
    def _compute_line_ids(self):
        for r in self:
            # TODO: find a way to avoid remove all before adding
            cmd = [(3, line.id) for line in r.line_ids]
            if r.date_start and r.date_end and r.date_start < r.date_end and r.contract_ids:
                cmd += [(0, 0, vals) for vals in r._prepare_line_vals()]
            r.with_context(force_delete=True).line_ids = cmd

    @api.depends('line_ids.planned_hours')
    def _compute_planned_hours(self):
        for r in self:
            r.planned_hours = sum(r.line_ids.mapped('planned_hours'))
    
    @api.depends('recognition_mode', 'line_ids.actual_hours')
    def _compute_actual_hours(self):
        for r in self:
            r.actual_hours = sum(r.line_ids.mapped('actual_hours'))

    @api.depends('line_ids.planned_overtime_pay')
    def _compute_planned_overtime_pay(self):
        for r in self:
            r.planned_overtime_pay = sum(r.line_ids.mapped('planned_overtime_pay'))
    
    @api.depends('line_ids.actual_overtime_pay')
    def _compute_actual_overtime_pay(self):
        for r in self:
            r.actual_overtime_pay = sum(r.line_ids.mapped('actual_overtime_pay'))

    def _compute_can_recognize(self):
        for r in self:
            r.can_recognize = any(line.recognition_mode != 'none' for line in r.line_ids)

    def _compute_has_non_draft_payslips(self):
        for r in self:
            if any(line.has_non_draft_payslips for line in r.line_ids):
                r.has_non_draft_payslips = True
            else:
                r.has_non_draft_payslips = False

    def _compute_read_only(self):
        for r in self:
            r.readonly = r.has_non_draft_payslips
    
    @api.model
    def _get_fields_to_trigger_match_update(self):
        return ['employee_id', 'date_start', 'date_end']
    
    def write(self, vals):
        contracts = self.sudo().contract_ids if any(f in vals for f in self._get_fields_to_trigger_match_update()) else False
        res = super(HrOvertimePlan, self).write(vals)
        if contracts:
            contracts |= self.employee_id.sudo().contract_ids
            contracts._compute_mismatched_overtime_plans()
        return res

    @api.model_create_multi
    @api.returns('self', lambda value:value.id)
    def create(self, vals_list):
        for vals in vals_list:
            # auto compute required computed fields if their value is not passed in vals
            # this avoid import failure when users do not give value for these computed fields
            if any(not vals.get(f, False) for f in self._get_compute_required_fields()):
                plan = self.env['hr.overtime.plan'].new(vals)
                for f in self._get_compute_required_fields():
                    if not vals.get(f, False):
                        vals[f] = plan._fields[f].convert_to_write(plan[f], plan)
        return super(HrOvertimePlan, self).create(vals_list)

    @api.model
    def _get_compute_required_fields(self):
        """
        The required computed fields for the method `create` to compute automatically
        when creating records without passing value for these fields. For example,
        users don't need to give date_start and date_end while they already give value
        for date and time_start and time_end
        """
        return ['date_start', 'date_end']

    def _get_overlap_domain(self):
        self.ensure_one()
        return [
            ('id', '!=', self.id),
            ('date_start', '<', self.date_end),
            ('date_end', '>', self.date_start),
            ('employee_id', '=', self.employee_id.id),
            ]

    @api.constrains('employee_id', 'date_start', 'date_end')
    def _check_overlap(self):
        for r in self:
            overlap = self.env['hr.overtime.plan'].search(r._get_overlap_domain(), limit=1)
            if overlap:
                raise UserError(_("The overtime plan `%s` overlaps an existing one which is `%s`")
                                % (r.display_name, overlap.display_name))

    def _prepare_line_vals(self):
        vals_list = []
        for r in self:
            for contract in r.contract_ids:
                vals_list += contract._prepare_overtime_plan_line_vals(r)
        return vals_list

    def action_recompute_plan_lines(self):
        # sudo is acquired because team approval may not have access to employee contracts
        self.sudo()._compute_contract_ids()
        self.sudo()._compute_line_ids()

    def _recognize_actual_overtime(self):
        pass

    def action_recognize_actual_overtime(self):
        return self._recognize_actual_overtime()

    def action_resolve_contract_mismatch(self):
        # sudo is acquired because the HR user may not have access right to records that he has no access right
        self.sudo()._compute_contract_ids()
        self.sudo()._compute_line_ids()

    def name_get(self):
        result = []
        for r in self:
            result.append(
                (r.id, '%s - [From %s to %s]' % (
                    r.employee_id.name,
                    format_datetime(r.env, r.date_start, dt_format='short'),
                    format_datetime(r.env, r.date_end, dt_format='short')
                    )
                )
            )
        return result
