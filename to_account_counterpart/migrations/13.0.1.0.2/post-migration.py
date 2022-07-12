# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID
from odoo.tools import float_compare


def _fix_max_countered_amt(env):
    """
    Due to new changes in Odoo 13's draft/cancel flow, some moves got wrong countered amount.
    This method search existing account move line counterparts that have such wrong data and fix them
    """
    all_ml_counterparts = env['account.move.line.ctp'].search([])
    to_fix = all_ml_counterparts.filtered(lambda r: float_compare(
        abs(r.countered_amt),
        min([abs(r.dr_aml_id.balance), abs(r.cr_aml_id.balance)]),
        precision_rounding=r.company_currency_id.rounding or 0.01
        ) == 1
    )
    moves = to_fix.mapped('move_id')
    if moves:
        moves.action_delete_counterpart()
        moves.action_smart_create_counterpart()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    _fix_max_countered_amt(env)

