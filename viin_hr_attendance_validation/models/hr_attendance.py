# -*- coding: utf-8 -*-
from pytz import timezone, utc
from datetime import datetime

from odoo import models, fields, api, registry, _
from odoo.exceptions import AccessDenied
from odoo.tools import relativedelta


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Schedule', compute='_compute_valid_check_in_check_out', store=True,
                                           help="The working schedule that matches the duration of this attendance entry, which is computed automatically.")
    valid_check_in = fields.Datetime(string='Valid Check-in', compute='_compute_valid_check_in_check_out', store=True,
                                     help="The valid time of checking-in according to the corresponding working schedule.")
    valid_check_out = fields.Datetime(string='Valid Check-out', compute='_compute_valid_check_in_check_out', store=True,
                                      help="The valid time of checking-out according to the corresponding working schedule.")

    late_attendance_hours = fields.Float(string='Late Coming Hours', compute='_compute_late_attendance_hours', store=True,
                                         help="The total late attendance hours counting from the Valid Check-in time to the actual check-in time.")
    early_leave_hours = fields.Float(string='Early Leave Hours', compute='_compute_early_leave_hours', store=True,
                                     help="The total early leave hours counting from the actual check-out time to the Valid Check-out.")

    valid_worked_hours = fields.Float(string='Valid Attendance Hours', compute='_compute_valid_worked_hours', store=True,
                                      help="The actual attendance hours that match the corresponding working schedule. Early coming and late leave will"
                                      " be ignored.")
    
    auto_checkout = fields.Boolean(string='Auto Check-out', readonly=True)
    manual_checkout_by_user_id = fields.Many2one('res.users', string='Manual Checkout Modification By', readonly=True,
                                                 help="This field stores the user who filled/modified the check out time"
                                                 " of the current attendance entry")
    days_crossing = fields.Boolean(string='Days Crossing', compute='_compute_days_crossing', store=True,
                                   help="This indicates if the entry has check-in and check hours in different days (at emplpyee's local time).")

    def write(self, vals):
        if 'check_out' in vals and not self._context.get('not_manual_check_out_modification', False):
            vals['manual_checkout_by_user_id'] = self.env.uid
        return super(HrAttendance, self).write(vals)

    @api.depends('employee_id', 'check_in', 'check_out')
    def _compute_valid_check_in_check_out(self):
        """
        Note:
            1. contract change triggering could be used with depending on 'employee_id.contract_ids', 'employee_id.contract_ids.state',
                                                             'employee_id.contract_ids.date_start',
                                                             'employee_id.contract_ids.date_end'
            However, it also triggers recompute all the attendance of the employee which will bring bad UX.
            Therefore, `hr.contract` must be extended to trigger contract changes for affected hr.attendance records only
            
            2. automatic time-off change triggering could be used with depending on 'employee_id.resource_id.calendar_id.leave_ids'
            However, it also triggers recompute all the attendance of the employee which will bring bad UX.
            Therefore, `resource.calendar.leaves` must be extended to trigger time-off changes
        """
        now = fields.Datetime.now()
        self = self.sorted(lambda rec: (rec.check_in, rec.check_out or datetime(3000, 1, 1)))
        work_intervals = self.employee_id._get_work_intervals(
            (self[:1].check_in or now) - relativedelta(days=7),
            (self[-1:].check_out or now) + relativedelta(days=7),
            naive_datetime=False,
            global_leaves=True, # if global leaves specified, respect it
            employee_leaves=True, # if time-off available, respect it
            global_attendances_only=False # ensure both normal/global attendance and abnormal attendance are taken into account 
            )
        for r in self:
            res_calendars = self.env['resource.calendar']
            r.valid_check_in = False
            r.valid_check_out = False
            r.resource_calendar_id = False
            if not r.check_in or not r.employee_id:
                continue
            
            # compute valid check-in
            for start, end, cal_attendance in sorted(work_intervals[r.employee_id.id], key=lambda interval: interval[0], reverse=False):
                cal_timezone = timezone(cal_attendance.calendar_id.tz)
                start = cal_timezone.localize(start.replace(tzinfo=None))
                end = cal_timezone.localize(end.replace(tzinfo=None))
                tz_check_in = r.check_in.astimezone(cal_timezone)
                tz_check_out = r.check_out.astimezone(cal_timezone) if r.check_out else False
                if r.valid_check_in:
                    break
                if (tz_check_in >= start and tz_check_in < end) \
                    or (tz_check_in == start and (not tz_check_out or tz_check_out > start)) \
                    or tz_check_in <= start:
                    r.valid_check_in = start.astimezone(utc).replace(tzinfo=None)
                    res_calendars |= cal_attendance.calendar_id
            # compute valid check-out
            for start, end, cal_attendance in sorted(work_intervals[r.employee_id.id], key=lambda interval: interval[0], reverse=True):
                if r.valid_check_out:
                    break
                cal_timezone = timezone(cal_attendance.calendar_id.tz)
                start = cal_timezone.localize(start.replace(tzinfo=None))
                end = cal_timezone.localize(end.replace(tzinfo=None))
                tz_check_in = r.check_in.astimezone(cal_timezone)
                tz_check_out = r.check_out.astimezone(cal_timezone) if r.check_out else False
                if (tz_check_out and ((tz_check_out > start and tz_check_out <= end) or (tz_check_out > end and tz_check_in < end))) \
                    or (r.valid_check_in and r.valid_check_in.astimezone(cal_timezone) == start):
                    r.valid_check_out = end.astimezone(utc).replace(tzinfo=None)
                    res_calendars |= cal_attendance.calendar_id
            # assign resource calendar
            r.resource_calendar_id = res_calendars[:1]

    @api.depends('resource_calendar_id', 'check_in', 'check_out')
    def _compute_days_crossing(self):
        if not self.ids:
            return
        self.env.cr.execute(
            """
            SELECT r.id,
                CASE WHEN r.check_in iS NOT NULL AND r.check_out IS NOT NULL AND r.resource_calendar_id IS NOT NULL
                    THEN CASE WHEN DATE(r.check_in at time zone 'utc' at time zone res_cal.tz) != DATE(r.check_out at time zone 'utc' at time zone res_cal.tz)
                        THEN True
                        ELSE False
                        END
                    ELSE False
                END AS days_crossing
            FROM hr_attendance AS r
            LEFT JOIN resource_calendar AS res_cal ON res_cal.id = r.resource_calendar_id
            WHERE r.id IN %s
            """,
            (tuple(self.ids),)
            )
        rows = self.env.cr.fetchall()
        mapped_data = dict(rows)
        for r in self:
            r.days_crossing = mapped_data.get(r.id, False)

    @api.depends('resource_calendar_id', 'check_in', 'valid_check_in', 'valid_worked_hours')
    def _compute_late_attendance_hours(self):
        for r in self:
            r.late_attendance_hours = 0.0
            if r.check_in and r.valid_check_in and r.resource_calendar_id and r.valid_worked_hours:
                diff = (r.check_in - r.valid_check_in).total_seconds()
                if diff > 0:
                    r.late_attendance_hours = diff / 3600.0

    @api.depends('resource_calendar_id', 'check_out', 'valid_check_out', 'valid_worked_hours')
    def _compute_early_leave_hours(self):
        for r in self:
            r.early_leave_hours = 0.0
            if r.check_out and r.valid_check_out and r.resource_calendar_id and r.valid_worked_hours:
                diff = (r.valid_check_out - r.check_out).total_seconds()
                if diff > 0:
                    r.early_leave_hours = diff / 3600.0

    @api.depends('resource_calendar_id', 'check_in', 'check_out',)
    def _compute_valid_worked_hours(self):
        for r in self:
            if not r.check_in or not r.check_out or not r.resource_calendar_id:
                r.valid_worked_hours = 0.0
            else:
                r.valid_worked_hours = r.resource_calendar_id.get_work_hours_count(r.check_in, r.check_out)

    def action_compute_valid_check_in_check_out(self):
        self._compute_valid_check_in_check_out()

    @api.model
    def _prepare_auto_checkout_candidates_domain(self):
        dt = fields.Datetime.now() - relativedelta(hours=self._context.get('auto_checkout_delay_hours', 0))
        return [
            ('check_out', '=', False),
            ('valid_check_out', '!=', False),
            ('valid_check_out', '<=', dt),
            ]

    def _filterred_auto_checkout_candidates(self):
        return self.filtered_domain(self._prepare_auto_checkout_candidates_domain()).sorted('check_in')

    def _auto_checkout(self):
        if not self.env.user.has_group('hr_attendance.group_hr_attendance_user'):
            raise AccessDenied(_("Only users who are granted for '%s' can do auto-checkout action.")
                            % self.env.ref('hr_attendance.group_hr_attendance_user').display_name)
        for r in self._filterred_auto_checkout_candidates():
            r.check_out = r.valid_check_out
            r.auto_checkout = True

    def action_auto_checkout(self):
        self._auto_checkout()

    @api.model
    def _cron_auto_checkout(self):
        attendances = self.env['hr.attendance'].search([('check_out', '=', False)])
        attendances._compute_valid_check_in_check_out()
        attendances = attendances.with_context(auto_checkout_delay_hours=10)._filterred_auto_checkout_candidates()
        for attendance in attendances:
            cr = registry(self._cr.dbname).cursor()
            attendance = attendance.with_env(attendance.env(cr=cr))
            try:
                attendance._auto_checkout()
                cr.commit()
            except Exception as e:
                cr.rollback()
            finally:
                cr.close()
