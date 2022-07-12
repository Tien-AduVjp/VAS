# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_payslip_ot(env):
    env['hr.payslip'].search([])._compute_overtime_plan_line_ids()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_payslip_ot(env)
