# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _contract_compute_overtime_base_amount(env):
    env['hr.contract'].with_context(active_test=True).search([])._compute_overtime_base_amount()


def _fix_ot_pay_calculation(env):
    ot_plan_lines = env['hr.overtime.plan.line'].search([])
    for line in ot_plan_lines:
        line.standard_hour_pay = line.contract_id.overtime_base_amount / line.contract_id._get_work_hours_in_month(line.date_start, line.date_end)

        
def _fix_ot_holiday(env):
    ot_plans = env['hr.overtime.plan'].search([])
    ot_plans._compute_line_ids()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _contract_compute_overtime_base_amount(env)
    _fix_ot_pay_calculation(env)
    _fix_ot_holiday(env)
