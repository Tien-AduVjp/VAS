from datetime import datetime, date
from pytz import timezone, UTC

from odoo.tests.common import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestResourceCalendar(TestCommon):
    
    def setUp(self):
        super(TestResourceCalendar, self).setUp()
        self.timeoff = self.env['resource.calendar.leaves'].sudo().create({
            'name': self.employee.name,
            'date_from': datetime(2021, 5, 23, 22, 0),  # 00h May 24 local time
            'date_to': datetime(2021, 11, 23, 21, 59, 59, 999999),  # ~00h Nov 24 local time
            'resource_id': self.employee.resource_id.id,
            'calendar_id': self.employee.resource_calendar_id.id,
            'time_type': 'leave',
            })
        
    def test_01__get_leave_intervals_arg_type(self):
        """
        Ensure AssertionError if dates are passed into the employee._get_leave_intervals()
        """
        with self.assertRaises(AssertionError):
            self.employee._get_leave_intervals(date(2021, 7, 1), date(2021, 7, 4))

    def test_02__get_leave_intervals(self):
        """
        This test ensures the given start and end passed into the _qualify_interval() method
        must be in the same type of either date or datetime
        
        """
        start = datetime(2021, 7, 1)
        end = datetime(2021, 7, 4)
        leave_intervals = self.employee._get_leave_intervals(start, end)[self.employee.id]
        self.assertEqual(
            leave_intervals[0],
            (start, end, self.timeoff)
            )
        global_leave_start = timezone(self.employee.resource_calendar_id.tz).localize(datetime(2021, 7, 2)).astimezone(UTC).replace(tzinfo=None)
        global_leave_end = timezone(self.employee.resource_calendar_id.tz).localize(datetime(2021, 7, 3)).astimezone(UTC).replace(tzinfo=None)
        global_leave = self.env['resource.calendar.leaves'].sudo().create({
            'name': 'Global Leave',
            'date_from': global_leave_start,
            'date_to': global_leave_end,
            'resource_id': False,
            'calendar_id': self.employee.resource_calendar_id.id,
            'time_type': 'leave',
            })
        leaves = self.timeoff + global_leave
        leave_intervals = self.employee._get_leave_intervals(start, end)[self.employee.id]
        self.assertEqual(
            leave_intervals[0],
            (start, global_leave_start, leaves)
            )
        self.assertEqual(
            leave_intervals[1],
            (global_leave_end, end, leaves)
            )
