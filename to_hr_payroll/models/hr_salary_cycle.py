# -*- coding:utf-8 -*-
from dateutil import rrule  # Recurrence rule

from odoo import models, fields

from odoo.tools import relativedelta


class HrSalaryCycleOffset(models.Model):
    _name = 'hr.salary.cycle'
    _inherit = 'mail.thread'
    _description = 'Salary Cycle'
    
    name = fields.Char(string='Name', required=True, translate=True, tracking=True)
    start_day_offset = fields.Integer(string='Start Day Offset', default=0, required=True, tracking=True,
                                      help="Number of days that deviates from the start date of the standard cycle (e.g. first of month, year, etc)."
                                      "For example,\n"
                                      "* 0 means the 1st day of the cycle (e.g. month, year, etc) will be treated as the first day of the cycle,\n"
                                      "* 1 means the 2nd day of the cycle will be treated as the first day of the cycle, etc.")
    start_month_offset = fields.Integer(string='Start Month Offset', default=0, required=True, tracking=True,
                                        help="Number of months that deviates from the January. You can input either positive or negative value"
                                        " to drive the start month from previous years to the current ones or the ones on the futures.")
    
    _sql_constraints = [
        ('check_start_day_offset',
         "CHECK(start_day_offset >= -28 and start_day_offset < 28)",
         "Start Day Offset must be greater than or equal to -28 and less than 28"),
    ]

    def _get_month_start_date(self, date):
        """
        Get the month start date of the cycle that contains the given date
        """
        self.ensure_one()
        start = fields.Date.start_of(date, 'month') + relativedelta(days=self.start_day_offset)
        if start > date:
            start -= relativedelta(months=1)
        return start
    
    def _get_month_end_date(self, date):
        """
        Get the month end date of the cycle that contains the given date
        """
        self.ensure_one()
        return self._get_month_start_date(date) + relativedelta(months=1, seconds=-1)

    def _get_year_start_date(self, date):
        self.ensure_one()
        start = fields.Date.start_of(date, 'year') + relativedelta(months=self.start_month_offset, days=self.start_day_offset)
        if start > date:
            start -= relativedelta(years=1)
        return start
        
    def _get_year_end_date(self, date):
        self.ensure_one()
        return self._get_year_start_date(date) + relativedelta(years=1, seconds=-1)
        
    def _get_month_start_dates(self, date_start, date_end):
        """
        Get the list of start dates that match the cycle based on the given date_start and date_end
        For example, assume 25 as the start_day_offset,
            * the given 2021-01-26 and 2021-02-25 will produce [datetime.datetime(2021, 1, 26, 0, 0)]
            * the given 2021-01-01 and 2021-01-31 will produce [datetime.datetime(2020, 12, 26, 0, 0), datetime.datetime(2021, 1, 26, 0, 0)]
            * the given 2021-01-26 and 2021-03-03 will produce [datetime.datetime(2021, 1, 26, 0, 0), datetime.datetime(2021, 2, 26, 0, 0)]
            * the given 2021-01-25 and 2021-03-03 will produce [datetime.datetime(2020, 12, 26, 0, 0), datetime.datetime(2021, 1, 26, 0, 0), datetime.datetime(2021, 2, 26, 0, 0)]
        """
        self.ensure_one()
        date_from = self._get_month_start_date(date_start)
        date_to = self._get_month_end_date(date_end)
        return list(rrule.rrule(rrule.MONTHLY, dtstart=date_from, until=date_to))

    def _get_previous_month_cycle_interval(self, date):
        prev_month_date = date - relativedelta(months=1)
        return self._get_month_start_date(prev_month_date), self._get_month_end_date(prev_month_date)

    def _get_date_for_month_year_int(self, date):
        """
        This choose either cycle_date_start or cycle_date_end for the working month calendar month and year
        """
        date = fields.Datetime.to_datetime(date)
        cycle_date_start = self._get_month_start_date(date)
        cycle_date_end = self._get_month_end_date(date)
        month_start_of_cycle_date_end = fields.Date.start_of(cycle_date_end, 'month')
        return cycle_date_end if cycle_date_end - month_start_of_cycle_date_end > month_start_of_cycle_date_end - cycle_date_start else cycle_date_start
