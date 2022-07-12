from odoo import fields, models


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    overtime_plan_line_ids = fields.Many2many('hr.overtime.plan.line', string='Overtime Plan Lines',
                                                       compute='_compute_overtime_plan_line_ids')
    overtime_plan_lines_count = fields.Integer(string='Overtime Entries Count', compute='_compute_overtime_plan_lines_count')

    def _compute_overtime_plan_line_ids(self):
        for r in self:
            r.overtime_plan_line_ids = r.slip_ids.overtime_plan_line_ids

    def _compute_overtime_plan_lines_count(self):
        for r in self:
            r.overtime_plan_lines_count = len(r.overtime_plan_line_ids)

    def _recognize_actual_overtime(self):
        self.slip_ids._recognize_actual_overtime()

    def action_compute_overtime_entries(self):
        self.slip_ids.action_compute_overtime_plan_line_ids()

    def action_view_overtime_plan_lines(self):
        action = self.env.ref('viin_hr_overtime.action_hr_overtime_plan_line')
        result = action.read()[0]

        # override the context to get rid of the default filtering
        result['context'] = {'search_default_grp_rule_code':1}
        result['domain'] = "[('payslip_ids','in',%s)]" % str(self.slip_ids.ids)
        return result
