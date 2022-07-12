from odoo import api, SUPERUSER_ID
from odoo.addons.viin_hr_payroll_timesheet_wfh import _compute_timesheet_for_pow, _compute_hr_working_month_calendar_lines


def _recompute_timesheet_for_pow(env):
    _compute_timesheet_for_pow(env)


def _recompute_hr_working_month_calendar_lines(env):
    _compute_hr_working_month_calendar_lines(env)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _recompute_timesheet_for_pow(env)
    _recompute_hr_working_month_calendar_lines(env)

