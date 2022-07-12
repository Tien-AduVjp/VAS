from odoo import models, fields
from odoo.osv import expression


class HrOvertimePlanLine(models.Model):
    _inherit = 'hr.overtime.plan.line'
    
    approval_await_timesheet_ids = fields.Many2many('account.analytic.line', compute='_compute_need_timesheets_approval',
                                                    string='Approval Await Timesheet Entries')
    need_timesheets_approval = fields.Boolean(compute='_compute_need_timesheets_approval')
        
    def _compute_need_timesheets_approval(self):
        all_approval_await_timesheets = self._get_related_approval_await_timesheets()
        for r in self:
            approval_await_timesheets = all_approval_await_timesheets.filtered(lambda ts: ts.employee_id == r.employee_id)
            r.approval_await_timesheet_ids = [(6, 0, approval_await_timesheets.ids)]
            r.need_timesheets_approval = bool(approval_await_timesheets)

    def action_view_approval_await_timesheets(self):
        action = self.env.ref('hr_timesheet.act_hr_timesheet_line')
        result = action.read()[0]
        result['domain'] = "[('id','in', %s)]" % self._get_related_approval_await_timesheets().ids
        result['context'] = {}
        return result
        
    def _get_related_approval_await_timesheets(self):
        return self.env['account.analytic.line'].sudo().search(self._get_related_approval_await_timesheet_domain())

    def _get_related_approval_await_timesheet_domain(self):
        domain = super(HrOvertimePlanLine, self)._get_related_timesheet_domain()
        domain = expression.AND([domain, [('timesheet_state', 'in', ('draft', 'confirm', 'validate1'))]])
        return domain

    def _get_related_timesheet_domain(self):
        domain = super(HrOvertimePlanLine, self)._get_related_timesheet_domain()
        domain = expression.AND([domain, [('timesheet_state', '=', 'validate')]])
        return domain
