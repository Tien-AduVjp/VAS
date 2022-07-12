from odoo import models, fields, api


class HrOvertimePlan(models.Model):
    _inherit = 'hr.overtime.plan'

    approval_await_timesheet_ids = fields.Many2many('account.analytic.line', compute='_compute_need_timesheets_approval',
                                                    string='Approval Await Timesheet Entries')
    need_timesheets_approval = fields.Boolean(compute='_compute_need_timesheets_approval')

    def _compute_need_timesheets_approval(self):
        for r in self:
            r.approval_await_timesheet_ids = [(6, 0, r.line_ids.approval_await_timesheet_ids.ids)]
            r.need_timesheets_approval = any(line.need_timesheets_approval for line in r.line_ids)

    def action_view_approval_await_timesheets(self):
        action = self.env['ir.actions.act_window']._for_xml_id('hr_timesheet.act_hr_timesheet_line')
        action['domain'] = "[('id','in', %s)]" % self.line_ids._get_related_approval_await_timesheets().ids
        action['context'] = {}
        return action
