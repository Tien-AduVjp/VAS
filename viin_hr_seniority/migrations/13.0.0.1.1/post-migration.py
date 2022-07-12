# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _recompute_fields(env):
    employees = env['hr.employee'].with_context(active_test=False).search([])
    employees._compute_first_contract_date()
    employees._compute_first_non_trial_contract_date()
    employees._compute_termination_date()


def _drop_cols(cr):
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='hr_contract' and column_name='final_date_end';
    """)
    if cr.fetchone():
        cr.execute("ALTER TABLE hr_contract DROP COLUMN final_date_end;")


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _recompute_fields(env)
    _drop_cols(cr)

