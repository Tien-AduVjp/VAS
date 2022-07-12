from datetime import datetime, time

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_date, format_datetime, format_duration


class HrTimesheet(models.Model):
    _inherit = 'account.analytic.line'

    pow_for_timeoff_id = fields.Many2one('hr.leave', string='PoW for Time-off',
                                         domain="[('employee_id','=',employee_id),('pow_timesheet_required','=',True),('state','=','validate'),('date_from','<=',date),('date_to','>=',date)]",
                                         compute='_compute_pow_for_timeoff_id', store=True, readonly=False,
                                         help="The Time-Off that requires proof of work timesheet records")

    @api.depends('employee_id', 'date', 'project_id', 'unit_amount', 'holiday_id')
    def _compute_pow_for_timeoff_id(self):
        timesheet_lines = self.filtered(
            lambda l: \
            # timesheet records
            l.employee_id and l.project_id \
            # not timesheet generated for time off upon time of validation
            and not l.holiday_id  #
            )
        # set `pow_for_timeoff_id` False for non-timesheet records
        non_ts = self - timesheet_lines
        if non_ts:
            non_ts.pow_for_timeoff_id = False

        if not timesheet_lines:
            return

        # 1. Sort the timesheet_lines by id asc and date asc so that we could give highest priority to one
        #    that were created prior to the others.
        #    for example, there were 4 timesheet entries of the same days as below
        #    | id |       name       |    date    | hours |
        #    | 3  |       Entry 3    | 2022-02-12 |   2   |
        #    | 6  |       Entry 6    | 2022-02-12 |   5   |
        #    | 1  |       Entry 1    | 2022-02-12 |   3   |
        #    | 4  |       Entry 4    | 2022-02-12 |   5   |
        #    total time off of that day was 7 hours and we prefer to take the ones(1,3,4)
        #    (after ordering) instead of the ones(3,6,4) (before ordering)
        # 2. Also, in UI operation, id could be an instance of newId then sorted may raise TypeError like
        #    TypeError: '<' not supported between instances of 'NewId' and 'NewId'
        #    test for that during sorted is required
        timesheet_lines = timesheet_lines.sorted(
            lambda l: (
                l.date,
                l.id if not isinstance(l.id, models.NewId) else (l.id.origin or 0)
                )
            )

        # start computing pow_for_timeoff_id for timesheet_lines
        pow_timeoffs = self.env['hr.leave'].search(timesheet_lines._get_pow_timeoff_domain())
        if not pow_timeoffs:
            timesheet_lines.pow_for_timeoff_id = False
            return

        # get the related pow timesheet so that we can calculate total timesheet for a single timeoff later for validation
        # for example, a time off of a full day says 8 hours leave, total timesheet hours must not be greater than 8
        related_timesheet_line_vals_list = self.env['account.analytic.line'].search_read(
            timesheet_lines._get_related_pow_timesheet_domain(additional_timeoffs=pow_timeoffs),
            ['employee_id', 'date', 'unit_amount', 'pow_for_timeoff_id']
            )
        all_timeoff_intervals = pow_timeoffs._get_intervals(naive=True)
        for employee in timesheet_lines.mapped('employee_id'):
            # group timesheet lines by employee
            employee_ts_to_check = timesheet_lines.filtered(lambda l: l.employee_id.id == employee.id)
            for ts_date in employee_ts_to_check.mapped('date'):
                ts_lines = employee_ts_to_check.filtered(lambda l: l.date == ts_date)
                timeoff_intervals = all_timeoff_intervals.get(employee.id, [])
                timeoff_intervals = list(
                    filter(
                        lambda interval: interval[0].date() == ts_date == interval[1].date(),
                        timeoff_intervals
                        )
                    )
                if not timeoff_intervals:
                    ts_lines.pow_for_timeoff_id = False
                    continue
                timeoffs = {}
                for __, __, hours, res_calendar_leaves in timeoff_intervals:
                    # I'm not sure if any situation where res_calendar_leaves having more than one record
                    # so, it's better to put a test here so that we could have chance to debug later
                    if len(res_calendar_leaves) > 1:
                        raise ValidationError(_("This could be a programming error when there is more"
                                                " than one resource.calendar.leaves in res_calendar_leaves"))
                    timeoffs.setdefault(res_calendar_leaves, 0.0)
                    timeoffs[res_calendar_leaves] += hours
                assigned = self.env['account.analytic.line']
                for res_calendar_leaves, timeoff_hours in timeoffs.items():
                    # find the previously recorded hours from the other related
                    # timesheet records which are not in self
                    recorded_hours = sum([
                        ts_vals['unit_amount']
                        for ts_vals in filter(
                            lambda v: v['date'] == ts_date \
                            and v['pow_for_timeoff_id'][0] == res_calendar_leaves.holiday_id.id \
                            and v['employee_id'][0] == employee.id,
                            related_timesheet_line_vals_list
                            )
                        ])
                    enough = False
                    for ts_line in ts_lines:
                        hours_to_record = recorded_hours + ts_line.unit_amount
                        if hours_to_record <= timeoff_hours:
                            ts_line.pow_for_timeoff_id = res_calendar_leaves.holiday_id.id
                            if hours_to_record == timeoff_hours:
                                enough = True
                            recorded_hours += ts_line.unit_amount
                            assigned |= ts_line
                        elif not enough and recorded_hours < timeoff_hours:
                                ts_line.pow_for_timeoff_id = res_calendar_leaves.holiday_id.id
                                enough = True
                                recorded_hours += ts_line.unit_amount
                                assigned |= ts_line
                        if enough:
                            break
                    ts_lines -= assigned
                (ts_lines - assigned).pow_for_timeoff_id = False

    @api.constrains('pow_for_timeoff_id', 'date', 'employee_id', 'project_id', 'unit_amount', 'holiday_id')
    def _check_pow_for_timeoff(self):
        for r in self:
            if r.employee_id and r.project_id and r.pow_for_timeoff_id:
                if r.holiday_id:
                    raise UserError(_("The timesheet entry `%s` was generated for the time-off `%s` during time-off validation and will"
                                      " not be able to be considered as proof of work")
                                      % (r.display_name, r.holiday_id.display_name))

                if r.pow_for_timeoff_id.date_from and r.pow_for_timeoff_id.date_to and r.date:
                    time_off_date_from = r.pow_for_timeoff_id.date_from.date()
                    time_off_date_to = r.pow_for_timeoff_id.date_to.date()
                    if not time_off_date_from <= r.date <= time_off_date_to:
                        raise UserError(_("You may not be able to assign the timesheet entry `%s` as a proof of work for the Time-Off `%s`"
                                          " since its date `%s` is not valid for the time-off which is from `%s` to `%s`.")
                                          % (
                                              r.display_name,
                                              r.pow_for_timeoff_id.display_name,
                                              format_date(r.env, r.date),
                                              format_datetime(r.env, r.pow_for_timeoff_id.date_from),
                                              format_datetime(r.env, r.pow_for_timeoff_id.date_to),
                                              )
                                          )

    @api.constrains('pow_for_timeoff_id', 'date', 'unit_amount', 'employee_id', 'project_id', 'holiday_id')
    def _check_pow_duration_for_timeoff(self):
        to_check = self.filtered(
            lambda r: r.employee_id \
            and r.project_id \
            and r.pow_for_timeoff_id \
            and r.pow_for_timeoff_id.state == 'validate' \
            and r.pow_for_timeoff_id.date_from \
            and r.pow_for_timeoff_id.date_to \
            and r.date
            )
        if not to_check:
            return
        # find the related timesheet lines and union with the current ones
        to_check |= self.env['account.analytic.line'].search(to_check._get_related_pow_timesheet_domain())
        # sort the timesheet_lines by id asc and date asc so that we could give highest priority to one
        # that were created prior to the others.
        # for example, there were 4 timesheet entries of the same days as below
        # | id |       name       |    date    | hours |
        # | 3  |       Entry 3    | 2022-02-12 |   2   |
        # | 6  |       Entry 6    | 2022-02-12 |   5   |
        # | 1  |       Entry 1    | 2022-02-12 |   3   |
        # | 4  |       Entry 4    | 2022-02-12 |   5   |
        # total time off of that day was 7 hours and we prefer to take the ones(1,3,4)
        # (after ordering) instead of the ones(3,6,4) (before ordering)
        to_check = to_check.sorted(lambda l: (l.date, l.id))
        # sudo is required as _get_intervals may access something that normal employee user may not have enough access rights
        all_timeoff_intervals = to_check.pow_for_timeoff_id.sudo()._get_intervals(naive=True)
        if not bool(all_timeoff_intervals):
            return
        for timeoff in to_check.pow_for_timeoff_id:
            timeoff_ts_lines = to_check.filtered(lambda l: l.pow_for_timeoff_id.id == timeoff.id)
            for ts_date in timeoff_ts_lines.mapped('date'):
                timeoff_intervals = list(
                    filter(
                        lambda interval: interval[0].date() == ts_date == interval[1].date(),
                        all_timeoff_intervals.get(timeoff.employee_id.id, [])
                        )
                    )
                if not timeoff_intervals:
                    continue
                timeoff_hours = sum([hours for __, __, hours, __ in timeoff_intervals])
                ts_lines = timeoff_ts_lines.filtered(lambda l: l.date == ts_date)
                checked_hours = 0.0
                enough = False  # allow to record one more timesheet that over total timeoff hours
                for ts_line in ts_lines:
                    checked_hours += ts_line.unit_amount
                    if checked_hours <= timeoff_hours:
                        continue
                    else:
                        if not enough and checked_hours - ts_line.unit_amount < timeoff_hours:
                            enough = True
                            continue
                        raise UserError(_("You may not be able to assign the timesheet record `%s` as proof of work for the Time-Off `%s`"
                                          " as it would make total PoW timesheet hours greater than the corresponding time-off duration of"
                                          " the day (%s time-off hours on %s). In other words, if the current timesheet hours is greater"
                                          " than or equal to the total time-off hours of the day, no more PoW timesheet of the same day"
                                          " is allowed.")
                                          % (
                                              ts_line.display_name,
                                              timeoff.display_name,
                                              format_duration(timeoff_hours),
                                              format_date(self.env, ts_line.date),
                                              )
                                          )

    def _get_related_pow_timesheet_domain(self, additional_timeoffs=None):
        timeoffs = self.pow_for_timeoff_id
        if isinstance(additional_timeoffs, self.env['hr.leave'].__class__):
            timeoffs |= additional_timeoffs
        return [
            ('id', 'not in', (self | timeoffs.timesheet_ids).ids),
            ('employee_id', 'in', self.employee_id.ids),
            ('project_id', '!=', False),
            ('holiday_id', '=', False),
            ('pow_for_timeoff_id', 'in', timeoffs.ids),
            ('date', 'in', self.mapped('date')),
            ]

    def _get_pow_timeoff_domain(self):
        today = fields.Date.today()
        date_from = fields.Datetime.start_of(datetime.combine(min(self.mapped('date') or [today]), time.min), 'day')
        date_to = fields.Datetime.end_of(datetime.combine(max(self.mapped('date') or [today]), time.max), 'day')
        return [
            ('employee_id', 'in', self.employee_id.ids),
            ('pow_timesheet_required', '=', True),
            ('holiday_status_id.unpaid', '=', False),
            ('state', '=', 'validate'),
            ('date_from', '<', date_to),
            ('date_to', '>', date_from),
            ]
