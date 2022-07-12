from odoo import models, fields, api


class HrWorkingMonthCalendarLine(models.Model):
    _inherit = 'hr.working.month.calendar.line'

    pow_required_hours = fields.Float(string='PoW-Required Time-Off Hours', compute='_compute_pow_required_duration', store=True)
    pow_required_days = fields.Float(string='PoW-Required Time-Off Days', compute='_compute_pow_required_duration', store=True)
    pow_timesheet_ids = fields.Many2many('account.analytic.line', 'working_month_calendar_line_pow_timesheet_rel',
                                         'working_month_calendar_line_id', 'timesheet_id', string='PoW Timesheet',
                                         compute='_compute_pow_timesheet_ids', store=True)
    pow_timesheet_hours = fields.Float(string='PoW Timesheet Hours', compute='_compute_pow_timesheet_duration', compute_sudo=True)
    pow_timesheet_days = fields.Float(string='PoW Timesheet Days', compute='_compute_pow_timesheet_duration', compute_sudo=True)
    missing_pow_hours = fields.Float(string='Missing PoW Hours', compute='_compute_missing_pow_duration', compute_sudo=True)
    missing_pow_days = fields.Float(string='Missing PoW Days', compute='_compute_missing_pow_duration', compute_sudo=True)

    @api.depends(
        'working_month_calendar_id',
        'working_month_calendar_id.payslip_id',
        'working_month_calendar_id.payslip_id.employee_id',
        'leave_ids.holiday_id',
        'leave_ids.holiday_id.pow_timesheet_required',
        'leave_ids.holiday_status_id',
        'date_from', 'date_to')
    def _compute_pow_timesheet_ids(self):
        all_pow_timesheet_lines = self.env['account.analytic.line'].search_read(
            self._get_pow_timesheets_domain(),
            ['date', 'employee_id', 'pow_for_timeoff_id'],
            order='id ASC, date ASC'  # order to give more control on assertion in test script
            )
        # speed up computation for large records in self but all_pow_timesheet_lines is empty
        if not all_pow_timesheet_lines:
            self.write({'pow_timesheet_ids': False})
            return
        # start computation for each record in self
        for r in self:
            pow_timeoff = r.leave_ids.holiday_id.filtered(
                lambda l: not l.holiday_status_id.unpaid and l.pow_timesheet_required
                )
            # filter for the pow timesheet of current record
            pow_timesheet_lines = filter(
                lambda l: r.date_from <= l['date'] <= r.date_to \
                    and l['employee_id'][0] == r.working_month_calendar_id.payslip_id.employee_id.id \
                    and l['pow_for_timeoff_id'][0] in pow_timeoff.ids,
                all_pow_timesheet_lines
                )
            r.pow_timesheet_ids = [(6, 0, [ts['id'] for ts in pow_timesheet_lines])]

    @api.depends(
        'leave_ids',
        'leave_ids.holiday_id.pow_timesheet_required',
        'leave_ids.hours',
        'leave_ids.days',
        'leave_ids.unpaid')
    def _compute_pow_required_duration(self):
        all_ps_leave_intervals = self.env['payslip.leave.interval'].search_read(
            self._get_pow_payslip_leave_intervals_domain() + ['|', ('hours', '>', 0), ('days', '>', 0)],
            ['working_month_calendar_line_id', 'hours', 'days']
            )
        for r in self:
            pow_required_hours = 0.0
            pow_required_days = 0.0
            for leave_interval in all_ps_leave_intervals:
                if leave_interval['working_month_calendar_line_id'][0] == r.id:
                    pow_required_hours += leave_interval['hours']
                    pow_required_days += leave_interval['days']
            r.pow_required_hours = pow_required_hours
            r.pow_required_days = pow_required_days

    @api.depends('pow_timesheet_ids.unit_amount', 'resource_calendar_id')
    def _compute_pow_timesheet_duration(self):

        def  validate_pow_timesheet_duration(given, max_val):
            return max_val if given > max_val else given

        for r in self:
            pow_timesheet_hours = sum(r.pow_timesheet_ids.mapped('unit_amount'))
            pow_timesheet_hours = validate_pow_timesheet_duration(pow_timesheet_hours, r.pow_required_hours)

            pow_timesheet_days = pow_timesheet_hours / r.resource_calendar_id.hours_per_day
            pow_timesheet_days = validate_pow_timesheet_duration(pow_timesheet_days, r.pow_required_days)

            r.pow_timesheet_hours = pow_timesheet_hours
            r.pow_timesheet_days = pow_timesheet_days

    @api.depends('pow_required_hours', 'pow_required_days', 'pow_timesheet_ids.unit_amount', 'resource_calendar_id')
    def _compute_missing_pow_duration(self):
        for r in self:
            r.missing_pow_hours = r.pow_required_hours - r.pow_timesheet_hours
            r.missing_pow_days = r.pow_required_days - r.pow_timesheet_days

    def _get_pow_payslip_leave_intervals_domain(self):
        return [
            ('working_month_calendar_line_id', 'in', self.ids),
            ('holiday_id.pow_timesheet_required', '=', True),
            ('unpaid', '=', False)
            ]

    def _get_pow_timesheets_domain(self):
        hr_leaves = self.leave_ids.holiday_id.filtered(
            lambda timeoff: timeoff.pow_timesheet_required and not timeoff.holiday_status_id.unpaid
            )
        return [
            ('project_id', '!=', False),
            ('employee_id', 'in', self.working_month_calendar_id.payslip_id.employee_id.ids),
            ('pow_for_timeoff_id', 'in', hr_leaves.ids),
            # exclude timesheet that were auto generated for time off
            ('holiday_id', '=', False)
            ]
