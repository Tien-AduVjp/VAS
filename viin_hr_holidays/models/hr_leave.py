from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _compute_date_from_to(self):
        res = super(HrLeave, self)._compute_date_from_to()
        datetime = fields.Datetime.now().replace(second=0)
        date = datetime.date()
        for r in self:
            if r.request_unit_hours:
                r.update({
                    'date_from': datetime,
                    'request_date_from': date,
                    'date_to': datetime,
                    'request_date_to': date,
                })
        return res
    
    @api.constrains('date_from', 'date_to')
    def _check_timeoff_duration(self):
        for r in self:
            duration = (r.date_to - r.date_from).total_seconds() / 60
            if duration < 30:
                raise UserError(_("Time off duration must be greater than or equal to 30 minutes!"))

    def action_adjustment_leave(self):
        self.ensure_one()
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            raise UserError(_("Only Holiday Administrator can adjust approved leaves. Please contact them"))
        action = self.env['ir.actions.act_window']._for_xml_id('viin_hr_holidays.adjustment_leave_view_action')
        action['context'] = {
            'default_leave_id': self.id,
            'default_date_from': self.date_from,
            'default_date_to': self.date_to
            }
        return action

    def _adjust_dates(self, date_from, date_to):
        if date_from > date_to:
            raise UserError(_("Date From must be less than Date To"))
        self.ensure_one()
        if self.holiday_status_id.request_unit != 'day':
            raise UserError(_("Time Off Type with mode calculated by day can adjust"))
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
