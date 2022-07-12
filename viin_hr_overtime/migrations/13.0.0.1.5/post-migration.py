# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_contract_mismatch_ot_plan(env):
    hr_contracts = env['hr.contract'].search([])
    hr_contracts._compute_mismatched_overtime_plans()

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_contract_mismatch_ot_plan(env)
