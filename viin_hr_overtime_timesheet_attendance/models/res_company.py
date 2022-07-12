from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    overtime_recognition_mode = fields.Selection(selection_add=[
        ('attendance_or_timesheet', 'Attendance or Timesheet'),
        ('attendance_and_timesheet', 'Attendance and Timesheet')
        ], ondelete={'attendance_or_timesheet':'set default', 'attendance_and_timesheet':'set default'},
        help="This indicates mode to recognize actual overtime against the plan:\n"
        "* By Plan: No recognition will be required. All the planned overtime duration will be considered as actual;\n"
        "* Attendance: Actual overtime will be calculated based on attendance entries that match the planned overtime;\n"
        "* Timesheet: Actual overtime will be calculated based on recorded timesheet entries that match the planned overtime;\n"
        "* Attendance or Timesheet: Actual overtime will be calculated based on EITHER attendance entries OR recorded timesheet"
        " entries that match the planned overtime. Attendance takes the priority;\n"
        "* Attendance and Timesheet: Actual overtime will be calculated based on BOTH attendance entries AND recorded timesheet"
        " entries that match the planned overtime.")
