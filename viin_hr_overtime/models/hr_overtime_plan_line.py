from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons.base.models.res_partner import _tz_get
from odoo.tools import format_datetime
from odoo.tools.date_utils import relativedelta

from .res_company import OVERTIME_RECOGNITION_MODE


class HrOvertimePlanLine(models.Model):
    _name = 'hr.overtime.plan.line'
    _description = "Overtime Plan Line"
    _rec_name = 'overtime_plan_id'

    # This model is readonly

    overtime_plan_id = fields.Many2one('hr.overtime.plan', string='Overtime Plan', required=True, readonly=True, ondelete='cascade',
                                       help="The overtime plan that generates this plan line.")
    reason_id = fields.Many2one(related='overtime_plan_id.reason_id')
    employee_id = fields.Many2one(related='overtime_plan_id.employee_id', store=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True, readonly=True, groups="hr_contract.group_hr_contract_manager",
                                  help="The employee's affected contract applied to the interval of the Start Date and the End Date.")
    currency_id = fields.Many2one(related='contract_id.currency_id', help="Contract's currency")
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule', required=True, readonly=True)
    tz = fields.Selection(_tz_get, string='Timezone', required=True, readonly=True)
    date_start = fields.Datetime(string='Start Date', required=True, readonly=True)
    date_end = fields.Datetime(string='End Date', required=True, readonly=True)
    hr_overtime_rule_id = fields.Many2one('hr.overtime.rule', string='Overtime Rule', required=True, readonly=True)
    rule_code_id = fields.Many2one('hr.overtime.rule.code', string='Overtime Rule Code', required=True, readonly=True)
    recognition_mode = fields.Selection(OVERTIME_RECOGNITION_MODE, string='Recognition Mode', required=True, readonly=True)
    pay_rate = fields.Float(string='Pay Rate', required=True, default=100.0, readonly=True, group_operator="avg",
                            help="The rate that will be used for overtime pay amount calculation. For example:"
                            " `Actual Overtime Amount = Standard Pay per Hour * Pay Rate * Actual Overtime Hours`")
    global_leave_id = fields.Many2one('resource.calendar.leaves', string='Global/Holiday Leave', readonly=True,
                                      help="A global leave specified on the corresponding Working Schedule that matches this plan line.")
    planned_hours = fields.Float(string='Planned Hours', compute='_compute_planned_hours', store=True,
                                 help="The total hours between the Start Date and the End Date.")
    actual_hours = fields.Float(string='Actual Overtime Hours', compute='_compute_actual_hours', store=True,
                                help="The actual overtime hours recognized by selected Recognition Mode (e.g. By Plan, Attendance, etc)."
                                " If 'By Plan' is selected, the actual overtime hours will be the planned hours. Otherwise, the"
                                " actual overtime hours will be recognized by the affected mode accordingly.")
    standard_hour_pay = fields.Monetary(string='Standard Pay per Hour', readonly=True, group_operator='avg', groups="hr_contract.group_hr_contract_manager",
                                        help="The standard pay amount per hour based on the corresponding contract's wage, or other contract's"
                                        " factors depending on the Overtime Base Mode specified on the corresponding contract.")
    planned_overtime_pay = fields.Monetary(string='Planned Overtime Pay', compute='_compute_planned_overtime_pay', store=True,
                                           groups="hr_contract.group_hr_contract_manager",
                                           help="The planned overtime pay amount (according to the the planned hours) that is calculated"
                                           " as: `Standard Pay per Hour * Pay Rate * Planned Hours`")
    actual_overtime_pay = fields.Monetary(string='Actual Overtime Pay', compute='_compute_actual_overtime_pay', store=True,
                                          groups="hr_contract.group_hr_contract_manager",
                                          help="The actual overtime pay amount (according to the actual overtime hours) that is calculated"
                                          " as: `Standard Pay per Hour * Pay Rate * Actual Overtime Hours`.")
    standard_pay = fields.Monetary(string='Standard Pay', compute='_compute_standard_pay', store=True, groups="hr_contract.group_hr_contract_manager",
                                   help="The actual overtime pay amount (according to the actual overtime hours) that is calculated"
                                   " as: `Standard Pay per Hour * Actual Overtime Hours`. Pay Rate is ignored.")
    extra_pay = fields.Monetary(string='Extra Pay', compute='_compute_extra_pay', groups='hr_contract.group_hr_contract_manager')
    currency_rate = fields.Float("Currency Rate", compute='_compute_currency_rate', compute_sudo=True, store=True,
                                 digits=(12, 6), readonly=True, group_operator='avg')
    has_non_draft_payslips = fields.Boolean(string='Included in Non-Draft Payslip', compute='_compute_has_non_draft_payslips', compute_sudo=True)

    _sql_constraints = [
        ('date_check', "CHECK (date_start < date_end)", "The Start Date must be anterior to the End Date."),
    ]

    def unlink(self):
        if not self._context.get('force_delete', False):
            raise UserError(_("You may not be able to delete an overtime plan line manually. You should handle it from the corresponding overtime plan."))
        return super(HrOvertimePlanLine, self).unlink()

    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        raise UserError(_("Duplicating an overtime plan line is not allowed."))

    @api.depends('date_start', 'date_end')
    def _compute_planned_hours(self):
        for r in self:
            if not r.date_end or not r.date_start:
                r.planned_hours = 0.0
            else:
                r.planned_hours = (r.date_end - r.date_start).total_seconds() / 3600

    @api.depends('contract_id.currency_id', 'date_start')
    def _compute_currency_rate(self):
        for r in self:
            r.currency_rate = r.contract_id.currency_id.with_context(date=r.date_start or fields.Date.now()).rate or 1.0

    @api.depends('recognition_mode', 'planned_hours')
    def _compute_actual_hours(self):
        for r in self:
            if r.recognition_mode == 'none':
                r.actual_hours = r.planned_hours
            else:
                r.actual_hours = 0.0

    @api.depends('standard_hour_pay', 'actual_hours')
    def _compute_standard_pay(self):
        for r in self:
            r.standard_pay = r.standard_hour_pay * r.actual_hours

    @api.depends('planned_hours', 'standard_hour_pay', 'pay_rate')
    def _compute_planned_overtime_pay(self):
        for r in self:
            r.planned_overtime_pay = r.planned_hours * r.standard_hour_pay * r.pay_rate / 100

    @api.depends('actual_hours', 'standard_hour_pay', 'pay_rate')
    def _compute_actual_overtime_pay(self):
        for r in self:
            r.actual_overtime_pay = r.actual_hours * r.standard_hour_pay * r.pay_rate / 100

    def _compute_extra_pay(self):
        for r in self:
            r.extra_pay = r.actual_overtime_pay - r.standard_pay

    def _compute_has_non_draft_payslips(self):
        for r in self:
            r.has_non_draft_payslips = False

    def _get_match_intervals(self, date_start, date_end):
        if date_start < self.date_start:
            date_start = self.date_start
        elif date_start > self.date_end:
            date_start = False

        if date_end > self.date_end:
            date_end = self.date_end
        elif date_end < self.date_start:
            date_end = False

        if not date_start or not date_end:
            return False, False
        return date_start, date_end

    @api.model
    def _get_fields_to_trigger_match_update(self):
        return ['employee_id', 'date_start', 'date_end']

    @api.model
    def _get_cron_recognize_actual_overtime_domain(self):
        seven_days_ago = fields.Datetime.now() - relativedelta(days=90)
        return [
            ('recognition_mode', '!=', 'none'),
            ('overtime_plan_id.date_end', '>', seven_days_ago),
            ('actual_hours', '=', 0),
            ]

    @api.model
    def _cron_recognize_actual_overtime(self):
        lines = self.env['hr.overtime.plan.line'].search(self._get_cron_recognize_actual_overtime_domain())
        lines.mapped('overtime_plan_id')._recognize_actual_overtime()
        return lines

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
