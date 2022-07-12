from datetime import datetime, time
from odoo import fields, models, api
from odoo.tools.float_utils import float_round

from .browsable_object import PayslipContributionLine


class HrPayslipContributionLine(models.Model):
    _name = 'hr.payslip.contribution.line'
    _description = "Payslip Contribution Line"
    _order = 'date_from asc'

    #####################################################################################################
    # every field of this model is accessible in salary rule Python code as contributions.CODE.field_name
    #####################################################################################################

    payroll_contrib_history_id = fields.Many2one('hr.payroll.contribution.history', string='Payroll Contribution History',
                                                                  required=True, readonly=True, ondelete='cascade')
    type_id = fields.Many2one(related='payroll_contrib_history_id.type_id', store=True)
    code = fields.Char(related='type_id.code', store=True)
    payslip_id = fields.Many2one('hr.payslip', string='Payslip', required=True, ondelete='cascade')
    date_from = fields.Date(string='Date From', required=True, readonly=True)
    date_to = fields.Date(string='Date To', required=True, readonly=True)
    currency_id = fields.Many2one(related='payslip_id.currency_id', store=True)
    contribution_base = fields.Monetary(compute='_compute_contribution_base', store=True)
    employee_contrib_rate = fields.Float(related='payroll_contrib_history_id.employee_contrib_rate', store=True)
    employee_contribution = fields.Monetary(compute='_compute_employee_contribution', store=True)
    company_contrib_rate = fields.Float(related='payroll_contrib_history_id.company_contrib_rate', store=True)
    company_contribution = fields.Monetary(compute='_compute_company_contribution', store=True)
    state = fields.Selection(related='payroll_contrib_history_id.state', store=True)
    computation_block = fields.Selection([
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ], string='Computation Block', compute='_compute_computation_block', store=True)
    days_in_months = fields.Selection([('fixed', 'Fixed as 28 days'), ('flexible', 'Flexible')], string='Days in Month', default='fixed',
                                      compute='_compute_days_in_months', store=True,
                                      help="During payslip contributions computation,\n"
                                      "- Fixed as 28 days: every month will be considered to have 28 days in total\n"
                                      "- Flexible: the number of days depends on the actual month, which varies from 28 to 31.")
    unpaid_days = fields.Float('Total Unpaid Days', compute='_compute_unpaid_days', store=True,
                               help="Total unpaid days according to the full month period.")

    @api.depends('payroll_contrib_history_id.payroll_contribution_reg_id')
    def _compute_computation_block(self):
        for r in self:
            r.computation_block = r.payroll_contrib_history_id.payroll_contribution_reg_id.computation_block

    @api.depends('payroll_contrib_history_id.payroll_contribution_reg_id')
    def _compute_days_in_months(self):
        for r in self:
            r.days_in_months = r.payroll_contrib_history_id.payroll_contribution_reg_id.days_in_months

    @api.depends('currency_id', 'date_to',
                 'payslip_id.company_id',
                 'payroll_contrib_history_id.currency_id',
                 'payroll_contrib_history_id.contribution_base')
    def _compute_contribution_base(self):
        for r in self:
            # when loading new payslip, the payslip's company_id may empty
            company = r.payslip_id.company_id or self.env.company
            to_currency = r.payslip_id.currency_id or company.currency_id
            date_to = r.date_to or fields.Date.today()
            r.contribution_base = r.payroll_contrib_history_id.currency_id._convert(
                r.payroll_contrib_history_id.contribution_base,
                to_currency,
                company,
                date_to
                )

    def _get_total_work_days_in_month(self):
        """ Get total work days in full month """
        date_from = datetime.combine(fields.Date.start_of(self.date_from, 'month'), time.min)
        date_to = datetime.combine(fields.Date.end_of(self.date_to, 'month'), time.max)
        days_in_month = 0
        employee = self.payslip_id.employee_id
        if employee:
            res_intervals = employee._get_resource_calendar_intervals(date_from, date_to)[employee]
            for contract, res_datas in res_intervals.items():
                for start, end, res_calendar in res_datas:
                    calendar_data = res_calendar.get_work_duration_data(start, end)
                    days_in_month += calendar_data['days']
        return days_in_month

    def _get_total_paid_days(self):
        """ Get total paid days in the period of current contribution line """
        date_from = datetime.combine(self.date_from, time.min)
        date_to = datetime.combine(self.date_to, time.max)
        paid_days = 0
        employee = self.payslip_id.employee_id
        if employee:
            res_intervals = employee._get_resource_calendar_intervals(date_from, date_to)[employee]
            for contract, res_datas in res_intervals.items():
                if not contract:
                    continue
                paid_days += self._get_paid_days(contract, res_datas)
        return paid_days

    def _get_paid_days(self, contract, res_calendar_datas):
        paid_days = 0
        if contract.salary_attendance_computation_mode == 'timeoff':
            for start, end, res_calendar in res_calendar_datas:
                calendar_data = res_calendar.get_work_duration_data(start, end)
                paid_days += calendar_data['days']
                paid_days -= self._get_leave_days(start.date(), end.date())['unpaid']
        return paid_days

    def _get_leave_days(self, date_from, date_to):
        leave_intervals = self.payslip_id.working_month_calendar_ids.line_ids.leave_ids
        leave_data = {
            'paid': 0.0,
            'unpaid': 0.0,
        }
        for interval in leave_intervals:
            if date_from <= interval.date <= date_to:
                if interval.unpaid:
                    leave_data['unpaid'] += interval.days
                else:
                    leave_data['paid'] += interval.days
        return leave_data

    @api.depends('date_from', 'date_to', 'payslip_id')
    def _compute_unpaid_days(self):
        for r in self:
            if r.payslip_id:
                calendar_working_days = r._get_total_work_days_in_month()
                paid_days = r._get_total_paid_days()
                r.unpaid_days = calendar_working_days - paid_days
            else:
                r.unpaid_days = 0

    def _get_duration(self):
        """
        return duration in days
        """
        if self.date_from and self.date_to:
            total_days = (self.date_to - self.date_from).days + 1
            if self.days_in_months == 'fixed' and total_days > 28:
                return 28
            else:
                return total_days
        else:
            return 0.0

    def _get_days_in_month(self):
        if self.days_in_months == 'fixed':
            return 28
        else:
            date_from = self.date_from or fields.Date.today()
            salary_cycle = self.payslip_id.salary_cycle_id
            if salary_cycle:
                date_from = salary_cycle._get_date_for_month_year_int(date_from)
            return self.env['to.base'].get_days_of_month_from_date(date_from)

    def _calculate_contribution(self, rate):
        self.ensure_one()
        days_in_months = self._get_days_in_month()
        duration = self._get_duration()
        contribution = 0
        if self.computation_block == 'day':
            contribution = (self.contribution_base * rate / 100.0) * duration / days_in_months
        elif self.computation_block == 'week':
            weeks = round(duration / 7)
            contribution = (self.contribution_base * rate / 100.0) * weeks / round(days_in_months / 7)
        else:
            contrib_register = self.payroll_contrib_history_id.payroll_contribution_reg_id
            if contrib_register.computation_method == 'half_up':
                months = float_round(duration / days_in_months, precision_digits=0, rounding_method='HALF-UP')
                contribution = (self.contribution_base * rate / 100.0) * months
            elif contrib_register.computation_method == 'max_unpaid_days':
                if self.unpaid_days < contrib_register.max_unpaid_days:
                    contribution = (self.contribution_base * rate / 100.0)
        return contribution

    def _calculate_company_contribution(self):
        self.ensure_one()
        return self._calculate_contribution(self.company_contrib_rate)

    def _calculate_employe_contribution(self):
        self.ensure_one()
        return self._calculate_contribution(self.employee_contrib_rate)

    @api.depends('date_to', 'date_from', 'contribution_base', 'employee_contrib_rate', 'payroll_contrib_history_id')
    def _compute_employee_contribution(self):
        for r in self:
            r.employee_contribution = r._calculate_employe_contribution()

    @api.depends('date_to', 'date_from', 'contribution_base', 'company_contrib_rate', 'payroll_contrib_history_id')
    def _compute_company_contribution(self):
        for r in self:
            r.company_contribution = r._calculate_company_contribution()

    def get_contributionline_obj(self):
        """
        Get a PayslipContributionLine object for usage in salary rule python code
        :return: PayslipContributionLine object
        :rtype: PayslipContributionLine
        """
        contribution_lines_dict = {}
        valid_lines = self.filtered(lambda l: l.state in ('confirmed', 'resumed'))
        for code in valid_lines.mapped('code'):
            contribution_lines_dict[code] = valid_lines.filtered(lambda l: l.code == code)
        return PayslipContributionLine(self.payslip_id.employee_id.id, contribution_lines_dict, self.env)
