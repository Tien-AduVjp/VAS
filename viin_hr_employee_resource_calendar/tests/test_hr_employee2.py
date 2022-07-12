from datetime import datetime, date, time
from dateutil import rrule
from unittest.mock import patch
from pytz import timezone, UTC

from odoo.tests.common import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestHrContracts(TestCommon):
    """
    This is for testing the method employee._get_work_intervals(self, date_start, date_end, naive_datetime=False, global_leaves=True, employee_leaves=True)
    """

    def patch_datetime_now(self, now):
        return patch('odoo.fields.Datetime.now', return_value=now)

    def patch_date_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.today', return_value=today)

    def _create_contract_35h(self):
        return self.env['hr.contract'].create({
            'name': 'Contract',
            'employee_id': self.employee.id,
            'state': 'open',
            'kanban_state': 'normal',
            'wage': 1,
            'date_start': date(2021, 6, 2),
            'date_end': date(2021, 6, 16),
            'resource_calendar_id': self.env.ref('resource.resource_calendar_std_35h').id
            })

    def _create_contracts(self):
        contract_35h = self._create_contract_35h()
        contract1_40h = self.env['hr.contract'].create({
            'name': 'Contract',
            'employee_id': self.employee.id,
            'state': 'open',
            'kanban_state': 'normal',
            'wage': 1,
            'date_start': date(2021, 6, 17),
            'date_end': date(2021, 7, 4),
            'resource_calendar_id': self.env.ref('resource.resource_calendar_std').id
            })
        contract2_40h = self.env['hr.contract'].create({
            'name': 'Contract',
            'employee_id': self.employee.id,
            'state': 'open',
            'kanban_state': 'normal',
            'wage': 1,
            'date_start': date(2021, 8, 1),
            'date_end': False,
            'resource_calendar_id': self.env.ref('resource.resource_calendar_std').id
            })
        return contract_35h, contract1_40h, contract2_40h

    def test_01__get_work_intervals_raise(self):
        with self.assertRaises(AssertionError):
            self.employee._get_work_intervals(datetime(2021, 7, 1), date(2021, 7, 4))
        with self.assertRaises(AssertionError):
            self.employee._get_work_intervals(date(2021, 7, 1), datetime(2021, 7, 4))
        with self.assertRaises(AssertionError):
            self.employee._get_work_intervals(date(2021, 7, 9), date(2021, 7, 4))

    def test_02__get_work_intervals_before_contract(self):
        contract = self._create_contract_35h()
        intervals = self.employee._get_work_intervals(datetime(2021, 5, 25), datetime(2021, 6, 2))[self.employee.id]
        self.assertEqual(len(intervals), 12)
        localize = timezone(contract.resource_calendar_id.tz).localize
        # Tuesday
        self.assertTupleEqual(
            (intervals[0][0], intervals[0][1]),
            (localize(datetime(2021, 5, 25, 8, 0)), localize(datetime(2021, 5, 25, 12, 0)))
            )
        self.assertTupleEqual(
            (intervals[1][0], intervals[1][1]),
            (localize(datetime(2021, 5, 25, 13, 0)), localize(datetime(2021, 5, 25, 16, 0)))
            )
        # Wednesday
        self.assertTupleEqual(
            (intervals[2][0], intervals[2][1]),
            (localize(datetime(2021, 5, 26, 8, 0)), localize(datetime(2021, 5, 26, 12, 0)))
            )
        self.assertTupleEqual(
            (intervals[3][0], intervals[3][1]),
            (localize(datetime(2021, 5, 26, 13, 0)), localize(datetime(2021, 5, 26, 16, 0)))
            )
        # Thursday
        self.assertTupleEqual(
            (intervals[4][0], intervals[4][1]),
            (localize(datetime(2021, 5, 27, 8, 0)), localize(datetime(2021, 5, 27, 12, 0)))
            )
        self.assertTupleEqual(
            (intervals[5][0], intervals[5][1]),
            (localize(datetime(2021, 5, 27, 13, 0)), localize(datetime(2021, 5, 27, 16, 0)))
            )
        # Friday
        self.assertTupleEqual(
            (intervals[6][0], intervals[6][1]),
            (localize(datetime(2021, 5, 28, 8, 0)), localize(datetime(2021, 5, 28, 12, 0)))
            )
        self.assertTupleEqual(
            (intervals[7][0], intervals[7][1]),
            (localize(datetime(2021, 5, 28, 13, 0)), localize(datetime(2021, 5, 28, 16, 0)))
            )
        # Monday
        self.assertTupleEqual(
            (intervals[8][0], intervals[8][1]),
            (localize(datetime(2021, 5, 31, 8, 0)), localize(datetime(2021, 5, 31, 12, 0)))
            )
        self.assertTupleEqual(
            (intervals[9][0], intervals[9][1]),
            (localize(datetime(2021, 5, 31, 13, 0)), localize(datetime(2021, 5, 31, 16, 0)))
            )
        # Tuesday
        self.assertTupleEqual(
            (intervals[10][0], intervals[10][1]),
            (localize(datetime(2021, 6, 1, 8, 0)), localize(datetime(2021, 6, 1, 12, 0)))
            )
        self.assertTupleEqual(
            (intervals[11][0], intervals[11][1]),
            (localize(datetime(2021, 6, 1, 13, 0)), localize(datetime(2021, 6, 1, 16, 0)))
            )

    def test_03__get_work_intervals_calendars(self):
        self._create_contracts()
        intervals = self.employee._get_work_intervals(datetime(2021, 6, 1), datetime(2021, 9, 1))[self.employee.id]
        self.assertEqual(len(intervals), 132)
        for dt in rrule.rrule(rrule.DAILY, dtstart=datetime(2021, 6, 1), until=datetime(2021, 9, 1)):
            if dt == datetime(2021, 9, 1):
                continue
            to_test = filter(
                lambda k: \
                k[0].astimezone(UTC).replace(tzinfo=None) >= datetime.combine(dt.date(), time.min)
                and k[1].astimezone(UTC).replace(tzinfo=None) <= datetime.combine(dt.date(), time.max)
                , intervals)
            to_test_count = len(list(to_test))
            if dt.weekday() in (5, 6):
                self.assertTrue(to_test_count == 0)
            else:
                self.assertTrue(to_test_count > 0)
            for interval in to_test:
                end = interval[1].astimezone(UTC).replace(tzinfo=None)
                if end <= datetime(2021, 6, 2):
                    self.assertEqual(interval[2].calendar_id, self.env.ref('resource.resource_calendar_std'))
                elif end <= datetime(2021, 6, 17):
                    self.assertEqual(interval[2].calendar_id, self.env.ref('resource.resource_calendar_std_35h'))
                else:
                    self.assertEqual(interval[2].calendar_id, self.env.ref('resource.resource_calendar_std'))
