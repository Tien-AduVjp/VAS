from odoo import models, fields


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    approval_await_timesheet_ids = fields.Many2many('account.analytic.line', compute='_compute_need_timesheets_approval',
                                                    string='Approval Await Timesheet Entries')
    need_timesheets_approval = fields.Boolean(compute='_compute_need_timesheets_approval')
    
    def _compute_need_timesheets_approval(self):
        for r in self:
            r.approval_await_timesheet_ids = [(6, 0, r.mapped('overtime_plan_line_ids.approval_await_timesheet_ids').ids)]
            r.need_timesheets_approval = any(line.need_timesheets_approval for line in r.overtime_plan_line_ids)
            
    def action_view_approval_await_timesheets(self):
        action = self.env.ref('hr_timesheet.act_hr_timesheet_line')
        result = action.read()[0]
        result['domain'] = "[('id','in', %s)]" % self.overtime_plan_line_ids._get_related_approval_await_timesheets().ids
        result['context'] = {}
        return result
