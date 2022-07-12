# -*- coding: utf-8 -*-

from odoo import fields, models


class EmployeeOvertime(models.Model):
    _inherit = 'hr.employee.overtime'

    payslip_ref = fields.Char(string='Payslip Ref.', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause='', where_clause=''):
        with_clause = """
        payslip_info AS (
            SELECT rel.plan_line_id, array_to_string(array_agg(DISTINCT slip.name), ', ') AS names
            FROM hr_payslip AS slip
            JOIN overtime_plan_line_hr_payslip_rel AS rel ON rel.payslip_id = slip.id
            GROUP BY rel.plan_line_id
            )
        """

        fields['payslip_ref'] = """,
            slip.names AS payslip_ref
            """
        from_clause += """
        LEFT JOIN payslip_info AS slip ON slip.plan_line_id = otpl.id
        """
        groupby += """,
        slip.names
        """
        return super(EmployeeOvertime, self)._query(with_clause, fields, groupby, from_clause, where_clause)

