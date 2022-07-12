from odoo import models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_overtime_entries_domain(self):
        domain = super(HrPayslip, self)._get_overtime_entries_domain()
        domain += ['|', ('approval_id', '=', False), ('overtime_plan_id.state', 'in', ('validate', 'done'))]
        return domain

    @api.depends('employee_id.overtime_plan_ids.state')
    def _compute_overtime_plan_line_ids(self):
        super(HrPayslip, self)._compute_overtime_plan_line_ids()
