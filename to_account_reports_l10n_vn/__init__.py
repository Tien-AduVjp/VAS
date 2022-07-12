# -*- coding: utf-8 -*-
from . import models
from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    sql = ""

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move_line' and column_name='due_duration';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE account_move_line ADD COLUMN due_duration integer DEFAULT NULL;
        UPDATE account_move_line SET due_duration = (date_maturity - date)
        """

    if sql:
        cr.execute(sql)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    vn_template = env.ref('l10n_vn.vn_template', False)
    if vn_template:
        env['account.account.template']._apply_show_both_dr_and_cr_trial_balance()
        env['account.account']._apply_show_both_dr_and_cr_trial_balance()
