import math

from calendar import monthrange

from odoo import models, fields, api


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    max_leave_days = fields.Float(string='Max Leave Days', default=0.0,
                                    help='Maximum number of days to leave per Limit Period Unit specified below. Leave this as 0 (zero) to ignore this period limit feature.')
    leave_period_unit = fields.Selection([
        ('month', 'Month'),
        ('quarter', 'Quarter'),
        ('year', 'Year'),
        ], default='month', string='Limit Period Unit', help='The period within which an employee cannot have more leave days'
                                         ' than being specified in the Max Leave Days field')

    _sql_constraints = [
        ('max_leave_days_check',
         'CHECK(max_leave_days >= 0)',
         "Max Leave Days must be greater than or equal to zero (0)"),
    ]

    @api.onchange('allocation_type')
    def onchange_allocation_type(self):
        if self.allocation_type == 'no':
            self.max_leave_days = 0
            self.leave_period_unit = 'month'
        else:
            if self._origin:
                self.max_leave_days = self._origin.max_leave_days
                self.leave_period_unit = self._origin.leave_period_unit

    def _get_datetimes_in_periord(self, datetime):
        self.ensure_one()
        year = datetime.year
        month = datetime.month
        quarter = math.ceil(month / 3.)

        if self.leave_period_unit == 'month':
            start_month = end_month = month
        elif self.leave_period_unit == 'quarter':
            if quarter == 1:
                start_month = 1
            elif quarter == 2:
                start_month = 4
            elif quarter == 3:
                start_month = 7
            else:
                start_month = 10
            end_month = start_month + 2
        else:
            start_month = 1
            end_month = 12

        last_day_in_last_month = "%02d" % (monthrange(year, end_month)[1],)
        start_month = "%02d" % (start_month,)
        end_month = "%02d" % (end_month,)
        date_from = fields.Datetime.to_datetime('%s-%s-01' % (year, start_month))
        date_to = fields.Datetime.to_datetime('%s-%s-%s' % (year, end_month, last_day_in_last_month))
        return date_from, date_to

    def _get_leaves_taken_in_period_domain(self, employee, date_from):
        date_from, date_to = self._get_datetimes_in_periord(date_from)
        return [
            ('employee_id', '=', employee.id),
            ('holiday_type', '=', 'employee'),
            ('holiday_status_id', '=', self.id),
            ('state', 'in', ('confirm', 'validate1', 'validate')),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ]

    def get_leaves_taken_in_period(self, employee, date_from):
        self.ensure_one()
        return self.env['hr.leave'].search(self._get_leaves_taken_in_period_domain(employee, date_from))
