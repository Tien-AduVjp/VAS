# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_ot_contract_mismatch(env):
    ot_plans = env['hr.overtime.plan'].search([('mismatched_contract_ids', '!=', False)])
    ot_plans.action_resolve_contract_mismatch()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_ot_contract_mismatch(env)

