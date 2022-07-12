# -*- coding: utf-8 -*-

from odoo import fields, models


class EmployeeOvertime(models.Model):
    _inherit = 'hr.employee.overtime'

    matched_attendance_hours = fields.Float(string='Matched Attendance', readonly=True)
    unmatched_attendance_hours = fields.Float(string='Unmatched Attendance', readonly=True)
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause='', where_clause=''):
        fields['attendance'] = """,
            SUM(otpl.matched_attendance_hours) AS matched_attendance_hours,
            SUM(otpl.unmatched_attendance_hours) AS unmatched_attendance_hours
            """
        return super(EmployeeOvertime, self)._query(with_clause, fields, groupby, from_clause, where_clause)

