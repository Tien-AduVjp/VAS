from odoo import models, fields, api, _


class HrWorkingMonthCalendar(models.Model):
    _name = 'hr.working.month.calendar'
    _description = "Working Month Calendar"
    _rec_name = 'month'

    month = fields.Char(string='Month', compute='_compute_month_str')
    month_int = fields.Integer(string='Month of Year', required=True, readonly=True, help="The month of the year which is 1~12")
    year_int = fields.Integer(string='Year', required=True, readonly=True)

    # TODO: remove salary_cycle_id in master/15, because it is not needed
    # avoid causing error related to o2m compute field
    salary_cycle_id = fields.Many2one('hr.salary.cycle', string='Salary Cycle', readonly=True)

    month_working_hours = fields.Float(string='Calendar Working Hours in Month', compute='_compute_month_working_hours', store=True,
                                       help="Total Working Hours (excl. global leaves) in the FULL month according to the"
                                       " corresponding calendars no matter what the start and end dates of the payslip are")
    month_working_days = fields.Float(string='Calendar Working Days in Month', compute='_compute_month_working_days', store=True,
                                      help="Total Working Days (excl. global leaves) in the FULL month according to"
                                      " the corresponding calendars no matter what the start and end dates of the payslip are")

    duty_working_hours = fields.Float(string='Duty Working Hours', compute='_compute_duty_working_hours', store=True, help="Total Working"
                                           " Hours of the month where the start and end dates of the payslip are taken into account")
    duty_working_days = fields.Float(string='Duty Working Days', compute='_compute_duty_working_days', store=True, help="Total Working"
                                          " Days of the month where the start and end dates of the payslip are taken into account")
    hours_rate = fields.Float(string='Hours Rate', compute='_compute_hours_rate', store=True,
                              help="The rate between duty working hours and calendar working hours in month")

    days_rate = fields.Float(string='Days Rate', compute='_compute_days_rate', store=True,
                              help="The rate between duty working days and calendar working days in month")

    line_ids = fields.One2many('hr.working.month.calendar.line', 'working_month_calendar_id', string='Working Month Calendar Line', readonly=True)
    contract_ids = fields.Many2many('hr.contract', string='Contracts', compute='_compute_contract_ids', compute_sudo=True)
    resource_calendar_ids = fields.Many2many('resource.calendar', string='Working Schedules', compute='_compute_resource_calendar_ids', compute_sudo=True)
    payslip_id = fields.Many2one('hr.payslip', string='Payslip', required=True, readonly=True, ondelete='cascade', auto_join=True)
    leave_days = fields.Float(string='Total Leave Days', compute='_compute_leave_days_hours',
                              help="Total leave days excluding global leaves")
    leave_hours = fields.Float(string='Total Leave Hours', compute='_compute_leave_days_hours',
                               help="Total leave hours excluding global leaves")
    unpaid_leave_days = fields.Float(string='Unpaid Leave Days', compute='_compute_unpaid_leave_days_hours')
    unpaid_leave_hours = fields.Float(string='Unpaid Leave Hours', compute='_compute_unpaid_leave_days_hours')
    worked_days = fields.Float(string='Worked Days', compute='_compute_worked_days_hours')
    worked_hours = fields.Float(string='Worked Hours', compute='_compute_worked_days_hours')
    paid_rate = fields.Float(string='Paid Rate', compute='_compute_paid_rate',
                             compute_sudo=True,
                             help="The rate which is computed by the following formula:\n"
                             "* If contract is on day rate basis: (Duty Working Days - Unpaid Leave Days) / Working Days in Full Month;\n"
                             "* If contract is on hour rate basis: (Duty Working Hours - Unpaid Leave Hours) / Working Hours in Full Month")

    _sql_constraints = [
        ('month_int_check', 'CHECK(month_int > 0 and month_int <= 12)', 'Month of Year must be 1~12!'),
        ('year_int_check', 'CHECK(year_int > 0)', 'Year must be greater than zero!'),
    ]

    def _compute_paid_rate(self):
        for r in self:
            if r.payslip_id.contract_id.salary_computation_mode == 'day_basis':
                if r.month_working_days == 0.0:
                    r.paid_rate = 0.0
                else:
                    r.paid_rate = (r.duty_working_days - r.unpaid_leave_days) / r.month_working_days
            else:
                if r.month_working_hours == 0.0:
                    r.paid_rate = 0.0
                else:
                    r.paid_rate = (r.duty_working_hours - r.unpaid_leave_hours) / r.month_working_hours

    @api.depends('duty_working_hours', 'month_working_hours')
    def _compute_hours_rate(self):
        for r in self:
            if r.month_working_hours != 0.0:
                r.hours_rate = r.duty_working_hours / r.month_working_hours
            else:
                r.hours_rate = 0.0

    @api.depends('duty_working_days', 'month_working_days')
    def _compute_days_rate(self):
        for r in self:
            if r.month_working_days != 0.0:
                r.days_rate = r.duty_working_days / r.month_working_days
            else:
                r.days_rate = 0.0

    @api.depends('line_ids.contract_id')
    def _compute_contract_ids(self):
        for r in self:
            r.contract_ids = r.line_ids.contract_id

    @api.depends('line_ids.resource_calendar_id')
    def _compute_resource_calendar_ids(self):
        for r in self:
            r.resource_calendar_ids = r.line_ids.resource_calendar_id

    @api.depends('line_ids.calendar_working_hours')
    def _compute_month_working_hours(self):
        for r in self:
            r.month_working_hours = sum(r.line_ids.mapped('calendar_working_hours'))

    @api.depends('line_ids.calendar_working_days')
    def _compute_month_working_days(self):
        for r in self:
            r.month_working_days = sum(r.line_ids.mapped('calendar_working_days'))

    @api.depends('line_ids.duty_working_hours')
    def _compute_duty_working_hours(self):
        for r in self:
            r.duty_working_hours = sum(r.line_ids.mapped('duty_working_hours'))

    @api.depends('line_ids.duty_working_days')
    def _compute_duty_working_days(self):
        for r in self:
            r.duty_working_days = sum(r.line_ids.mapped('duty_working_days'))

    @api.depends('month_int', 'year_int')
    def _compute_month_str(self):

        def get_month_str(month_int):
            month_map = {
                1: _("January"),
                2: _("February"),
                3: _("March"),
                4: _("April"),
                5: _("May"),
                6: _("June"),
                7: _("July"),
                8: _("August"),
                9: _("September"),
                10: _("October"),
                11: _("November"),
                12: _("December"),
                }
            return month_map[month_int]

        for r in self:
            if not r.month_int or not r.year_int:
                r.month = False
            else:
                r.month = "%s %s" % (get_month_str(r.month_int), r.year_int)

    def _compute_leave_days_hours(self):
        for r in self:
            r.leave_days = sum(r.line_ids.mapped('leave_days'))
            r.leave_hours = sum(r.line_ids.mapped('leave_hours'))

    def _compute_unpaid_leave_days_hours(self):
        for r in self:
            r.unpaid_leave_days = sum(r.line_ids.mapped('unpaid_leave_days'))
            r.unpaid_leave_hours = sum(r.line_ids.mapped('unpaid_leave_hours'))

    def _compute_worked_days_hours(self):
        for r in self:
            r.worked_days = sum(r.line_ids.mapped('worked_days'))
            r.worked_hours = sum(r.line_ids.mapped('worked_hours'))
