# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # recompute amount_residual
    aml_ids = env['account.move.line'].search([('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), ('amount_residual', '=', 0.0)])
    if aml_ids:
        aml_ids._amount_residual()

