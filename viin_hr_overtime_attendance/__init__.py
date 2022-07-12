# -*- coding: utf-8 -*-

from . import models
from . import report
from odoo import api, SUPERUSER_ID, _


def _match_attendances(env):
    plans = env['hr.overtime.plan'].search([])
    plans._match_attendances()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _match_attendances(env)
    
def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([('overtime_recognition_mode', 'like', 'attendance')])
    if companies:
        companies.write({'overtime_recognition_mode': 'none'})
