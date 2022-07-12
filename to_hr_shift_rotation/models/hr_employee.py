from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'to.base']

    shift_scheduling_line_ids = fields.One2many('shift.scheduling.line', 'employee_id', string='Shift Schedule')

    def create_shift_scheduling_lines(self, to_date):
        ShiftSchedule = self.env['shift.scheduling.line']
        for employee in self:
            last_resource_calendar_id = False
            if to_date:
                check_exist = ShiftSchedule.search([('employee_id', '=', employee.id), ('date_from', '=', to_date)])
                if not check_exist:
                    date_from = to_date
                    date_to = (datetime.strptime(date_from, DF) + relativedelta(days=6)).strftime(DF)
                    last_date_to = (datetime.strptime(date_from, DF) - relativedelta(days=1)).strftime(DF)
                    last_shift_rotation = ShiftSchedule.search([
                        ('employee_id', '=', employee.id), ('date_to', '=', last_date_to)], limit=1)
                    last_resource_calendar_id = last_shift_rotation and last_shift_rotation.resource_calendar_id or False
                else:
                    raise exceptions.ValidationError(_('The shift rotation line for employee %s are overlapped') % employee.name)
            else:
                last_shift_rotation = ShiftSchedule.search([
                    ('employee_id', '=', employee.id)], order='date_to DESC', limit=1)
                if last_shift_rotation:
                    date_from = (datetime.strptime(last_shift_rotation.date_to, DF) + relativedelta(days=1)).strftime(DF)
                    last_resource_calendar_id = last_shift_rotation.resource_calendar_id
                else:
                    next_monday = self.next_weekday(fields.Date.from_string(fields.Date.today()), 0)
                    date_from = next_monday
                    last_resource_calendar_id = False
                date_to = (date_from + relativedelta(days=6)).strftime(DF)

            contract_id = employee.contract_id
            if not contract_id:
                continue
            new_resource_calendar_id = False
            rate = 0
            if contract_id.rule_id.line_ids:
                new_resource_calendar_id, rate = contract_id.rule_id.line_ids.get_resource_calendar_id_and_rate(last_resource_calendar_id)
            if new_resource_calendar_id :
                ShiftSchedule.create({
                    'date_from': date_from,
                    'date_to': date_to,
                    'resource_calendar_id': new_resource_calendar_id.id,
                    'contract_id': contract_id.id,
                    'rate': rate,
                    'employee_id': employee.id
                    })
