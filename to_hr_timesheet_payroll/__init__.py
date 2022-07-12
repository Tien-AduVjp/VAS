from . import models
from . import wizard

from odoo import api, SUPERUSER_ID, _


####### POST_INIT_HOOK #######
def _generate_timesheet_salary_rules(env):
    companies = env['res.company'].search([])
    companies._generate_timesheet_salary_rules()


def _update_employee_timesheet_cost(env):
    all_payslips = env['hr.payslip'].search([('state', 'in', ('verify', 'done')), ('thirteen_month_pay', '=', False)], order='date_to asc')
    all_timesheet_lines = env['account.analytic.line'].search([
        ('project_id', '!=', False),
        ('employee_id', '!=', False),
        ('amount', '=', 0.0)])
    payslip_timesheet_hour_costs = all_payslips._calculate_payslip_timesheet_hour_cost()

    for employee in all_payslips.with_context(active_test=False).mapped('employee_id'):
        # - all the timesheet that were logged before the date_to of the very first payslip of the employee
        # will be costed as that payslip cost
        # - all the timesheet that were logged after the date_from of the very last payslip of the employee
        # will be costed as that payslip cost
        # - the remaining will be costed as the corresponding payslip cost
        payslips = all_payslips.filtered(lambda ps: ps.employee_id == employee)
        payslips_count = len(payslips)
        for idx, payslip in enumerate(payslips):
            payslip._update_employee_timesheet_cost()
            if idx == 0:
                timesheet_lines = all_timesheet_lines.filtered(
                    lambda l: l.date <= payslip.date_to and l.employee_id == employee)
            elif idx < payslips_count - 1:
                timesheet_lines = all_timesheet_lines.filtered(
                    lambda l: l.date >= payslip.date_from and l.date <= payslip.date_to and l.employee_id == employee)
            else:
                timesheet_lines = all_timesheet_lines.filtered(
                    lambda l: l.date >= payslip.date_from and l.employee_id == employee)

            for line in timesheet_lines.with_context(ignore_payslip_state_check=True):
                line.write({
                    'amount':-1 * payslip_timesheet_hour_costs.get(payslip, 0.0) * line.unit_amount
                    })


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_timesheet_salary_rules(env)
    _update_employee_timesheet_cost(env)
