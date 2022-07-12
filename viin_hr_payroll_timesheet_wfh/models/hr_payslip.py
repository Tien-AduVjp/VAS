from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    pow_required_hours = fields.Float(string='PoW-Required Time-Off Hours', compute='_compute_pow_required_hours')
    pow_required_days = fields.Float(string='PoW-Required Time-Off Days', compute='_compute_pow_required_days')
    pow_timesheet_ids = fields.Many2many('account.analytic.line', 'hr_payslip_pow_timesheet_rel',
                                         'hr_payslip_id', 'timesheet_id', string='PoW Timesheet',
                                         compute='_compute_pow_timesheet_ids', compute_sudo=True)
    pow_timesheet_count = fields.Integer(string='PoW Timesheet Count', compute='_compute_pow_timesheet_ids', compute_sudo=True)
    pow_timesheet_hours = fields.Float(string='PoW Timesheet Hours', compute='_compute_pow_timesheet_duration', compute_sudo=True)
    pow_timesheet_days = fields.Float(string='PoW Timesheet Days', compute='_compute_pow_timesheet_duration', compute_sudo=True)
    missing_pow_hours = fields.Float(string='Missing PoW Hours', compute='_compute_pow_timesheet_duration', compute_sudo=True)
    missing_pow_days = fields.Float(string='Missing PoW Days', compute='_compute_pow_timesheet_duration', compute_sudo=True)

    @api.depends('working_month_calendar_ids.line_ids.pow_timesheet_ids')
    def _compute_pow_timesheet_ids(self):
        for r in self:
            r.pow_timesheet_ids = [(6, 0, r.working_month_calendar_ids.line_ids.pow_timesheet_ids.ids)]
            r.pow_timesheet_count = len(r.pow_timesheet_ids)

    @api.depends('working_month_calendar_ids.line_ids.pow_required_hours')
    def _compute_pow_required_hours(self):
        for r in self:
            r.pow_required_hours = sum(r.working_month_calendar_ids.line_ids.mapped('pow_required_hours'))

    @api.depends('working_month_calendar_ids.line_ids.pow_required_days')
    def _compute_pow_required_days(self):
        for r in self:
            r.pow_required_days = sum(r.working_month_calendar_ids.line_ids.mapped('pow_required_days'))

    @api.depends('working_month_calendar_ids.line_ids')
    def _compute_pow_timesheet_duration(self):
        for r in self:
            r.pow_timesheet_hours = sum(r.working_month_calendar_ids.line_ids.mapped('pow_timesheet_hours'))
            r.pow_timesheet_days = sum(r.working_month_calendar_ids.line_ids.mapped('pow_timesheet_days'))
            r.missing_pow_hours = sum(r.working_month_calendar_ids.line_ids.mapped('missing_pow_hours'))
            r.missing_pow_days = sum(r.working_month_calendar_ids.line_ids.mapped('missing_pow_days'))

    def action_load_timesheets(self):
        super(HrPayslip, self).action_load_timesheets()
        self.working_month_calendar_ids.line_ids._compute_pow_timesheet_ids()

    def action_view_pow_timesheet(self):
        action = self.env.ref('hr_timesheet.act_hr_timesheet_line').read()[0]
        action['domain'] = "[('id', 'in', %s)]" % self.pow_timesheet_ids.ids
        return action
