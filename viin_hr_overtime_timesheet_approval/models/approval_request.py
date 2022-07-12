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
        result = self.env['ir.actions.act_window']._for_xml_id('hr_timesheet.timesheet_action_all')
        result['domain'] = "[('id','in', %s)]" % self.overtime_plan_line_ids._get_related_approval_await_timesheets().ids
        result['context'] = {}
        result['view_id'] = self.env.ref('hr_timesheet.timesheet_view_tree_user').id
        return result
