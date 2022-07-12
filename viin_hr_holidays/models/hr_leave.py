from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'
     
    @api.onchange('request_unit_hours')
    def _onchange_request_unit_hours(self):
        res = super(HrLeave, self)._onchange_request_unit_hours()
        date = fields.Datetime.now().replace(second=0)
        self.update({'date_from': date, 'date_to': date})
        return res
    
    def action_adjustment_leave(self):
        self.ensure_one()
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            raise UserError(_("Only Holiday Administrator can adjust approved leaves. Please contact them"))
        action = self.env.ref('viin_hr_holidays.adjustment_leave_view_action')
        result = action.read()[0]
        result['context'] = {
            'default_leave_id': self.id,
            'default_date_from': self.date_from,
            'default_date_to': self.date_to
            }
        return result
    
    def _adjust_dates(self, date_from, date_to):
        if date_from > date_to:
            raise UserError(_("Date From must be less than Date To"))
        self.ensure_one()
        if self.holiday_status_id.request_unit != 'day':
            raise UserError(_("Leave Type with mode calculated by day can adjust"))
        duration = self.employee_id.resource_calendar_id.get_work_duration_data(date_from, date_to, compute_leaves=False)
        self.with_context(leave_skip_state_check=True).write({
            'date_from': date_from,
            'date_to': date_to,
            'number_of_days': duration.get('days', 0)
        })
        rs_leaves = self.env['resource.calendar.leaves'].search([('holiday_id', '=', self.id)])
        rs_leaves.write({
            'date_from': date_from,
            'date_to': date_to,
        })
