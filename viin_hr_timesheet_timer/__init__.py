# -*- coding: utf-8 -*-
import datetime

from odoo import api, SUPERUSER_ID

from . import models


def pre_init_hook(cr):
    """
    Pre-populate stored computed/related fields to speedup installation
    """
    sql = ""
    # Adding date_start
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_analytic_line' and column_name='date_start';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE account_analytic_line ADD COLUMN date_start double precision DEFAULT NULL;
        """
    # Adding date_end
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_analytic_line' and column_name='date_end';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE account_analytic_line ADD COLUMN date_end double precision DEFAULT NULL;
        """

    if sql:
        cr.execute(sql)


def _fix_missing_start_date_end_date(env):
    """
        Reason for this migration:
            Update the field date_start and field date_end on all the old data.
            that had been created before this module was implemented.
    """
    # Search only for account_analytic_lines as timesheets.
    # A timesheet is always required to have a project and an employee
    # while an account entry doesn't has an employee
    # Note:
    #    There is no need to search after task_id, since
    #    user can log timesheet weather directly on a project or a task.
    timesheet_domain = [
        ('project_id', '!=', False),
        ('employee_id', '!=', False),
        ('date_start', '=', False),
        ('date_end', '=', False),
    ]

    timesheet_lines = env['account.analytic.line'].search(timesheet_domain)

    # time_to_utc = self.env['to.base'].convert_time_to_utc

    dates = {}
    for r in timesheet_lines:
        key = '%d%s' % (r.employee_id.id, r.date)
        if not dates.get(key, False):
            dates[key] = []

            attendances = r.employee_id.resource_calendar_id.attendance_ids.filtered(
                lambda att: att.dayofweek == str(r.date.weekday())
                )
            if attendances:
                # The date can be whatsoever since we only want to get the time on the line below
                attendances_hour_from_in_current_tz = datetime.datetime.combine(
                    r.date,
                    datetime.time(int(attendances[0].hour_from))
                    )
                attendances_hour_from_in_UTC = env['to.base'].convert_time_to_utc(
                    attendances_hour_from_in_current_tz,
                    r.employee_id.resource_calendar_id.tz
                )

                r.time_start = attendances_hour_from_in_UTC.hour
            else:
                r.time_start = 8.0

        else:
            last_timesheet_of_this_day = dates[key][-1]
            r.time_start = last_timesheet_of_this_day.time_start + r.unit_amount

        dates[key].append(r)

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_missing_start_date_end_date(env)
