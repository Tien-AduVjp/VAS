from datetime import datetime, timedelta

from odoo import models, fields, api, exceptions, _


class ShifScheduleWizard(models.TransientModel):
    _name = 'shift.schedule.wizard'
    _inherit = 'to.base'
    _description = 'Shift Schedule Wizard'

    @api.model
    def _get_all_employee_ids(self):
        all_employees = self.env['hr.employee'].search([('contract_id', '!=', False)])
        if all_employees:
            return all_employees.ids
        else:
            return []

    @api.model
    def _get_current_year(self):
        return fields.Datetime.from_string(fields.Datetime.now()).year

    employee_ids = fields.Many2many('hr.employee', string='Employees', default=_get_all_employee_ids, domain=[('contract_id', '!=', False)],
                                    help='Select Employees to create Working Shift Schedules', required=True)
    week_of_the_year = fields.Integer(string='Week Number', required=True)
    year = fields.Integer(string='Year', default=_get_current_year, required=True)
    to_date = fields.Date(string='To Date', compute='_compute_to_date')
    load_employee = fields.Selection([
        ('load_all', 'All Employees'),
        ('clear_all', 'Clear All')], default='load_all', copy=False, string='Mass Load/Clear',
         store=False, help='Utility fields to allow massive load/clear of employees')

    @api.onchange('load_employee')
    def onchange_load_employee(self):
        if self.load_employee == 'load_all':
            all_employees = self.env['hr.employee'].search([('contract_id', '!=', False)])
            if all_employees:
                self.employee_ids = all_employees

        elif self.load_employee == 'clear_all':
            self.employee_ids = False

    @api.depends('week_of_the_year', 'year')
    def _compute_to_date(self):
        for r in self:
            date = datetime(year=r.year, month=1, day=1)
            first_monday = self.next_weekday(date, 0)
            days_ahead = (self.week_of_the_year - 1) * 7
            self.to_date = first_monday + timedelta(days_ahead)

    '''Check , employee nào chưa có hợp đồng thì thông báo ra ngoài.'''
    def create_shift_scheduling_lines(self):
        self.ensure_one()

        for r in self.employee_ids.ids:
            employee = self.env['hr.contract'].search([('employee_id', '=', r)]).ids
            if not employee:
                employees_name = self.env['hr.employee'].search([('id', '=', r)])
                raise exceptions.ValidationError(_('Employee %s does not have a contract') % employees_name.name)

        if self.employee_ids:
            self.employee_ids.create_shift_scheduling_lines(self.to_date)

    @api.model
    def process_scheduler_create_shift_rotation(self):
        all_employees = self.env['hr.employee'].search([('contract_id', '!=', False)])
        if all_employees:
            to_date = False
            all_employees.create_shift_scheduling_lines(to_date)
