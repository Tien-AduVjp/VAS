# -*- coding: utf-8 -*-

from odoo import fields, models


class EmployeeOvertime(models.Model):
    _inherit = 'hr.employee.overtime'

    matched_timesheet_hours = fields.Float(string='Matched Timesheet', readonly=True)
    unmatched_timesheet_hours = fields.Float(string='Unmatched Timesheet', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause='', where_clause=''):
        fields['timesheet'] = """,
            SUM(otpl.matched_timesheet_hours) AS matched_timesheet_hours,
            SUM(otpl.unmatched_timesheet_hours) AS unmatched_timesheet_hours
            """
        return super(EmployeeOvertime, self)._query(with_clause, fields, groupby, from_clause, where_clause)

