from pytz import timezone

from odoo import api, SUPERUSER_ID


def _fix_attendance(env):
    attendances = env['hr.attendance'].search([])
    if attendances:
        attendances._compute_valid_check_in_check_out()
        attendances._compute_late_attendance_hours()
        attendances._compute_early_leave_hours()
        attendances._compute_valid_worked_hours()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_attendance(env)

