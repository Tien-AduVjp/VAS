from odoo import fields, models


class EmployeeOvertime(models.Model):
    _inherit = 'hr.employee.overtime'

    approval_id = fields.Many2one('approval.request', string='Approval Request', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'To Approve'),
        ('validate', 'Approved'),
        ('done', 'Done'),
        ('refuse', 'Refused'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause='', where_clause=''):
        fields['approval_request'] = """,
            otp.approval_id AS approval_id,
            CASE WHEN otp.approval_id IS NOT NULL THEN otp.state
                ELSE 'done'
                END AS state
            """
        from_clause += """
        LEFT JOIN approval_request AS req ON req.id = otp.approval_id
        LEFT JOIN approval_request_type AS req_type ON req_type.id = req.approval_type_id
        """
        groupby += """,
        req.id
        """
        return super(EmployeeOvertime, self)._query(with_clause, fields, groupby, from_clause, where_clause)
