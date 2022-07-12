from pytz import timezone

from odoo import api, SUPERUSER_ID


def _fix_days_crossing(env):
    attendances = env['hr.attendance'].search([])
    if attendances:
        attendances._compute_days_crossing()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_days_crossing(env)

