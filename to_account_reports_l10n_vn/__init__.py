from odoo import SUPERUSER_ID, api
from . import models
from . import reports
from . import wizards
from . import controllers

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

def _update_show_both_dr_and_cr_trial_balance(env):
    vn_template = env.ref('l10n_vn.vn_template', False)
    vn_template_c133 = env.ref('l10n_vn_c133.vn_template_c133', False)
    if vn_template or vn_template_c133:
        env['account.account.template']._apply_show_both_dr_and_cr_trial_balance()
        env['account.account']._apply_show_both_dr_and_cr_trial_balance()

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_show_both_dr_and_cr_trial_balance(env)
