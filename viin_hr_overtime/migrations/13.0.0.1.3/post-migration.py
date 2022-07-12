# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_ot_holiday(env):
    if not env['ir.module.module'].search([('name', '=', 'viin_hr_overtime_payroll'), ('state', 'in', ('installed', 'to upgrade'))]):
        ot_plans = env['hr.overtime.plan'].search([])
        ot_plans._compute_line_ids()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_ot_holiday(env)

