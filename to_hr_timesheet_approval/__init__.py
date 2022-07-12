# -*- coding: utf-8 -*-

from . import models
from . import wizard
from odoo import api, SUPERUSER_ID


def _generate_timesheet_approval_types(env):
    companies = env['res.company'].search([])
    companies._generate_approval_request_type()

    
def _auto_approve_none_timesheet_analytic_lines(env):
    timesheets = env['account.analytic.line'].sudo().search([
        ('employee_id', '!=', False),
        ('project_id', '!=', False),
        ('holiday_id', '=', False)
        ])
    none_timesheets = env['account.analytic.line'].sudo().search([('id', 'not in', timesheets.ids)])
    if none_timesheets:
        none_timesheets.write({'timesheet_state': 'validate'})


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_timesheet_approval_types(env)
    _auto_approve_none_timesheet_analytic_lines(env)
