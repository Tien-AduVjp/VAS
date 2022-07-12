from odoo import models, fields

class TimesheetCostUpdate(models.TransientModel):
    _name = 'timesheet.cost.update'
    _description  = 'Update timesheet cost of Payslip'

    def _default_payslip(self):
        return self.env['hr.payslip'].browse(self._context.get('active_ids'))

    payslip_ids = fields.Many2many('hr.payslip', default=_default_payslip)


    def update_timesheet_cost(self):
        for r in self:
            r.payslip_ids.with_context(update_employee_timesheet_cost=True)._compute_timesheet_cost()
