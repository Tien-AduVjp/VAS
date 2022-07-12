# -*- coding: utf-8 -*-

from . import models
from . import report
from . import wizard
from odoo import api, SUPERUSER_ID, _


def _update_hr_overtime_reason_project(env):
    hr_overtime_reason_project = env.ref('viin_hr_overtime.hr_overtime_reason_project', raise_if_not_found=False)
    if hr_overtime_reason_project:
        hr_overtime_reason_project.write({'project_required': True})


def _match_timesheet(env):
    plans = env['hr.overtime.plan'].search([])
    plans._match_timesheet_entries()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_hr_overtime_reason_project(env)
    _match_timesheet(env)
    
def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([('overtime_recognition_mode', 'like', 'timesheet')])
    if companies:
        companies.write({'overtime_recognition_mode': 'none'})
