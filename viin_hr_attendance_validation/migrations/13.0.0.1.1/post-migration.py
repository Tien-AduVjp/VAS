from pytz import timezone

from odoo import api, SUPERUSER_ID


def _fix_late_attendance(env):
    attendances = env['hr.attendance'].search([]).filtered(
        lambda r: r.check_in and r.valid_check_in and r.resource_calendar_id
        and r.check_in.astimezone(timezone(r.resource_calendar_id.tz)).date() != r.valid_check_in.astimezone(timezone(r.resource_calendar_id.tz)).date()
        )
    if attendances:
        attendances._compute_late_attendance_hours()


def _fix_early_leave(env):
    attendances = env['hr.attendance'].search([]).filtered(
        lambda r: r.check_out and r.valid_check_out and r.resource_calendar_id
        and r.check_out.astimezone(timezone(r.resource_calendar_id.tz)).date() != r.valid_check_out.astimezone(timezone(r.resource_calendar_id.tz)).date()
        )
    if attendances:
        attendances._compute_early_leave_hours()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_late_attendance(env)
    _fix_early_leave(env)

