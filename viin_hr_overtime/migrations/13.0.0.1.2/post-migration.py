# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_ot_pay_calculation(env):
    if not env['ir.module.module'].search([('name', '=', 'viin_hr_overtime_payroll'), ('state', 'in', ('installed', 'to upgrade'))]):
        ot_plan_lines = env['hr.overtime.plan.line'].search([])
        for line in ot_plan_lines:
            line.standard_hour_pay = line.contract_id.overtime_base_amount / line.contract_id._get_work_hours_in_month(line.date_start, line.date_end)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_ot_pay_calculation(env)
