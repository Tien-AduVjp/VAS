from odoo import models, fields, api


class HrOvertimePlanLine(models.Model):
    _inherit = 'hr.overtime.plan.line'
    
    recognition_mode = fields.Selection(selection_add=[
        ('attendance_or_timesheet', 'Attendance or Timesheet'),
        ('attendance_and_timesheet', 'Attendance and Timesheet')
        ], help="This indicates mode to recognize actual overtime against the plan:\n"
        "* By Plan: No recognition will be required. All the planned overtime duration will be considered as actual;\n"
        "* Attendance: Actual overtime will be calculated based on attendance entries that match the planned overtime;\n"
        "* Timesheet: Actual overtime will be calculated based on recorded timesheet entries that match the planned overtime;\n"
        "* Attendance or Timesheet: Actual overtime will be calculated based on EITHER attendance entries OR recorded timesheet"
        " entries that match the planned overtime. Attendance takes the priority;\n"
        "* Attendance and Timesheet: Actual overtime will be calculated based on BOTH attendance entries AND recorded timesheet"
        " entries that match the planned overtime.")

    def _get_attendance_timesheet_match_intevals(self):
        res = {}
        for r in self:
            res.setdefault(r, [])
            for attendance_match in r.attendance_match_ids:
                for timesheet_match in r.timesheet_match_ids:
                    start, end = attendance_match._get_matched_interval(timesheet_match.date_start, timesheet_match.date_end)
                    if start and end:
                        res[r].append([start, end])
            if not res[r]:
                del res[r]
        return res

    @api.depends('attendance_match_ids', 'matched_attendance_hours', 'timesheet_match_ids', 'matched_timesheet_hours')
    def _compute_actual_hours(self):
        super(HrOvertimePlanLine, self)._compute_actual_hours()
        for r in self.filtered(lambda rec: rec.recognition_mode == 'attendance_or_timesheet'):
            if r.matched_attendance_hours:
                r.actual_hours = r.matched_attendance_hours
            elif r.matched_timesheet_hours:
                r.actual_hours = r.matched_timesheet_hours
        matched_intervals = self.filtered(lambda rec: rec.recognition_mode == 'attendance_and_timesheet')._get_attendance_timesheet_match_intevals()
        for r, intervals in matched_intervals.items():
            r.actual_hours = sum([(end - start).total_seconds() / 3600 for start, end in intervals])

    def _compute_need_timesheets_approval(self):
        super(HrOvertimePlanLine, self)._compute_need_timesheets_approval()
        for r in self.filtered(lambda l: l.recognition_mode not in ('timesheet', 'attendance_or_timesheet', 'attendance_and_timesheet')):
            r.need_timesheets_approval = False
        
