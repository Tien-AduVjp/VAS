from odoo import models, fields, api


class HrWorkingMonthCalendar(models.Model):
    _inherit = 'hr.working.month.calendar'

    pow_required_hours = fields.Float(string='PoW-Required Time-Off Hours', compute='_compute_pow_required_hours')
    pow_required_days = fields.Float(string='PoW-Required Time-Off Days', compute='_compute_pow_required_days')
    pow_timesheet_ids = fields.Many2many('account.analytic.line', 'working_month_calendar_pow_timesheet_rel',
                                         'working_month_calendar_id', 'timesheet_id', string='PoW Timesheet',
                                         compute='_compute_pow_timesheet_ids', compute_sudo=True)
    pow_timesheet_hours = fields.Float(string='PoW Timesheet Hours', compute='_compute_pow_timesheet_duration', compute_sudo=True)
    pow_timesheet_days = fields.Float(string='PoW Timesheet Days', compute='_compute_pow_timesheet_duration', compute_sudo=True)
    missing_pow_hours = fields.Float(string='Missing PoW Hours', compute='_compute_pow_timesheet_duration', compute_sudo=True)
    missing_pow_days = fields.Float(string='Missing PoW Days', compute='_compute_pow_timesheet_duration', compute_sudo=True)

    @api.depends('line_ids.pow_timesheet_ids')
    def _compute_pow_timesheet_ids(self):
        for r in self:
            r.pow_timesheet_ids = [(6, 0, r.line_ids.pow_timesheet_ids.ids)]

    @api.depends('line_ids.pow_required_hours')
    def _compute_pow_required_hours(self):
        for r in self:
            r.pow_required_hours = sum(r.line_ids.mapped('pow_required_hours'))

    @api.depends('line_ids.pow_required_days')
    def _compute_pow_required_days(self):
        for r in self:
            r.pow_required_days = sum(r.line_ids.mapped('pow_required_days'))

    def _compute_pow_timesheet_duration(self):
        for r in self:
            r.pow_timesheet_hours = sum(r.line_ids.mapped('pow_timesheet_hours'))
            r.pow_timesheet_days = sum(r.line_ids.mapped('pow_timesheet_days'))
            r.missing_pow_hours = sum(r.line_ids.mapped('missing_pow_hours'))
            r.missing_pow_days = sum(r.line_ids.mapped('missing_pow_days'))
