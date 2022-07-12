# -*- coding: utf-8 -*-

from . import models
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.company'].search([]).write({
        'overtime_recognition_mode': 'attendance_or_timesheet'
    })
    env['hr.contract'].with_context(active_test=False).search([('overtime_recognition_mode', '=', 'attendance')]).write({
        'overtime_recognition_mode': 'attendance_or_timesheet'
    })

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([('overtime_recognition_mode', 'in', ['attendance_or_timesheet', 'attendance_and_timesheet'])])
    if companies:
        companies.write({'overtime_recognition_mode': 'none'})
