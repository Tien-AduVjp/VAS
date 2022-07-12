# -*- coding:utf-8 -*-
from pytz import timezone

from odoo import models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'
    
    def _overtime_interval_batch(self, ot_start, ot_end):
        # convert the given naive UTC ot_start and ot_end to naive local datetime
        tz = self.tz or self._context.get('tz')
        local_ot_start = ot_start.astimezone(tz=timezone(tz))
        local_ot_end = ot_end.astimezone(tz=timezone(tz))
        # genepay_rate intervals broken by midnight (00:00:00)
        # for example datetime(2021-02-02 20:00:00) ~ datetime(2021-02-03 20:00:00) will produce
        # [datetime(2021-02-02 20:00:00), datetime(2021-02-03 00:00:00), datetime(2021-02-03 20:00:00)]
        daily_breaks_midnight = self.env['to.base'].break_timerange_for_midnight(
            local_ot_start.replace(tzinfo=None),
            local_ot_end.replace(tzinfo=None)
            )
        
        # breaking daily_breaks_midnight into overtime intervals respecting global leaves
        ot_intervals = []
        last_seen = False
        for dt in daily_breaks_midnight:
            if not last_seen:
                last_seen = dt
                continue
            global_leaves = self._leave_intervals_batch(last_seen.replace(tzinfo=timezone(tz)), dt.replace(tzinfo=timezone(tz)))[False]
            global_leaves = [(start.replace(tzinfo=None), stop.replace(tzinfo=None), calendar_leave) for start, stop, calendar_leave in global_leaves]
            if not global_leaves:
                ot_intervals.append((last_seen, dt, False))
            else:
                start = last_seen
                for leave_start, leave_end, calendar_leave in global_leaves:
                    if start < leave_start:
                        ot_intervals.append((start, leave_start, False))
                    ot_intervals.append((leave_start, leave_end, calendar_leave))
                    start = leave_end
                if leave_end < dt:
                    ot_intervals.append((leave_end, dt, False))
            last_seen = dt
        return ot_intervals

    def _get_overtime_rule_domain(self, ot_date_start, ot_date_end, global_leave, company):
        time_to_float_hour = self.env['to.base'].time_to_float_hour
        ot_start_weekday = ot_date_start.date().weekday()
        ot_start_time_float = time_to_float_hour(ot_date_start.time())
        ot_end_weekday = ot_date_end.date().weekday()
        ot_end_time_float = time_to_float_hour(ot_date_end.time())

        if global_leave and global_leave.holiday:
            domain = [('holiday', '=', True)]
        else:
            domain = [('holiday', '=', False)]

        if ot_start_time_float == 0.0 and ot_end_time_float == 0.0:
            domain += [('weekday', '=', ot_start_weekday)]
        elif ot_start_time_float == 0.0:
            domain += [
                ('weekday', '=', ot_end_weekday),
                ('hour_from', '<', ot_end_time_float),
            ]
        elif ot_end_time_float == 0.0:
            domain += [
                ('weekday', '=', ot_start_weekday),
                ('hour_to', '>', ot_start_time_float),
            ]
        else:
            domain += [
                ('weekday', '=', ot_start_weekday),
                ('hour_to', '>', ot_start_time_float),
                ('hour_from', '<', ot_end_time_float),
            ]
        domain += ['|', ('company_id', '=', False), ('company_id', '=', company.id)]
        return domain

    def _match_overtime_rules(self, ot_start, ot_end, company):
        """
        This finds overtime rules that match the given the ot_start and the ot_end
        Then genepay_rates and dictionary of {interval1: rule1, interval2: rule2, etc}
        
        @param ot_start: datetime naive datetime in UTC for overtime start
        @param ot_end: datetime naive datetime in UTC for overtime end

        @return: dictionary of {(start1, end1): rule1, (start2, end2): rule2, etc}
        @rtype: dict
        """
        self.ensure_one()

        # breaking daily_breaks_midnight into overtime intervals respecting global leaves
        ot_intervals = self._overtime_interval_batch(ot_start, ot_end)

        # match intervals with overtime rules
        res = {}
        convert_time_to_utc = self.env['to.base'].convert_time_to_utc
        tz = self.tz or self._context.get('tz')
        for ot_date_start, ot_date_end, global_leave in ot_intervals:
            domain = self._get_overtime_rule_domain(ot_date_start, ot_date_end, global_leave, company)
            rules = self.env['hr.overtime.rule'].search(domain)
            for rule in rules:
                start, end = rule._get_overtime_interval(ot_date_start, ot_date_end)
                # convert back to naive UTC
                utc_start = convert_time_to_utc(start, tz_name=tz, naive=True)
                utc_end = convert_time_to_utc(end, tz_name=tz, naive=True)
                # update result for return later
                res[(utc_start, utc_end, global_leave)] = rule
        return res
