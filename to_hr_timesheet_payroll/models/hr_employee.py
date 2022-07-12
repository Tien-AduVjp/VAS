from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    timesheet_cost = fields.Monetary(tracking=True)

    def _get_timesheets_domain(self, date_from, date_to, include_leaves=True):
        return [
            ('project_id', '!=', False),
            ('employee_id', 'in', self.ids),
            ('date', '>=', date_from),
            ('date', '<=', date_to)
            ]

    def _update_timesheet_cost_from_payslips(self):
        """
        This method will get the latest payslip timesheet cost and fill into employee's timesheet_cost
        """
        payslips = self.env['hr.payslip']
        for r in self:
            payslips |= r._get_last_payslip()
        payslips._update_employee_timesheet_cost()

    def action_update_timesheet_cost_from_payslips(self):
        self._update_timesheet_cost_from_payslips()
