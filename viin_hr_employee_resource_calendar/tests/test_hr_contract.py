from datetime import datetime, date
from pytz import UTC

from odoo import fields, _
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestHrContracts(TestCommon):

    def test_01_qualify_interval_dates_type(self):
        """
        This test ensures the given start and end passed into the _qualify_interval() method
        must be in the same type of either date or datetime
        """
        start = datetime.strptime('2021-07-10', '%Y-%m-%d').date()
        end = datetime.strptime('2021-07-31', '%Y-%m-%d').date()
        contract = self.create_contract('open', 'normal', start, end)
        with self.assertRaises(
            ValidationError,
            msg=_("The given start and end passed into the method `_qualify_interval(start, end)`"
                  " must be in the same type. This could be a programming error...")
            ):
            contract._qualify_interval(datetime(2001, 10, 12, 0, 0, 0), date(2001, 10, 16))
        with self.assertRaises(
            ValidationError,
            msg=_("The given start and end passed into the method `_qualify_interval(start, end)`"
                  " must be in the same type. This could be a programming error...")
            ):
            contract._qualify_interval(date(2001, 10, 12), datetime(2001, 10, 16, 0, 0, 0))

    def test_02_qualify_interval_return_type(self):
        """
        This test ensures the return type must be the same as the given type passed into the
        _qualify_interval() method
        """
        start = datetime.strptime('2021-07-10', '%Y-%m-%d').date()
        end = datetime.strptime('2021-07-31', '%Y-%m-%d').date()
        contract = self.create_contract('open', 'normal', start, end)

        start, end = contract._qualify_interval(datetime(2001, 10, 12, 0, 0, 0), datetime(2001, 10, 16, 0, 0, 0))
        self.assertTrue(isinstance(start, datetime) and isinstance(end, datetime))

        start, end = contract._qualify_interval(date(2001, 10, 12), date(2001, 10, 16))
        self.assertTrue(isinstance(start, date) and isinstance(end, date) and not isinstance(start, datetime) and not isinstance(end, datetime))

    def test_03_qualify_interval_dates(self):
        start = datetime.strptime('2021-07-10', '%Y-%m-%d').date()
        end = datetime.strptime('2021-07-31', '%Y-%m-%d').date()
        contract = self.create_contract('open', 'normal', start, end)

        # TEST DATE
        # before contract
        self.assertEqual(
            contract._qualify_interval(date(2001, 10, 12), date(2001, 10, 16)),
            (date(2021, 7, 10), date(2021, 7, 10))
            )
        # after contract
        self.assertEqual(
            contract._qualify_interval(date(2022, 10, 12), date(2022, 10, 16)),
            (date(2021, 7, 31), date(2021, 7, 31))
            )
        # overlap forward contract
        self.assertEqual(
            contract._qualify_interval(date(2021, 7, 30), date(2021, 8, 31)),
            (date(2021, 7, 30), date(2021, 7, 31))
            )
        self.assertEqual(
            contract._qualify_interval(date(2021, 7, 30), date(2021, 7, 31)),
            (date(2021, 7, 30), date(2021, 7, 31))
            )
        # overlap backward contract
        self.assertEqual(
            contract._qualify_interval(date(2021, 7, 9), date(2021, 7, 12)),
            (date(2021, 7, 10), date(2021, 7, 12))
            )
        self.assertEqual(
            contract._qualify_interval(date(2021, 7, 10), date(2021, 7, 12)),
            (date(2021, 7, 10), date(2021, 7, 12))
            )

        # fully cover the contract
        self.assertEqual(
            contract._qualify_interval(date(2021, 6, 9), date(2021, 8, 12)),
            (date(2021, 7, 10), date(2021, 7, 31))
            )

    def test_04_qualify_interval_datetimes(self):
        start = datetime.strptime('2021-07-10', '%Y-%m-%d').date()
        end = datetime.strptime('2021-07-31', '%Y-%m-%d').date()
        contract = self.create_contract('open', 'normal', start, end)

        # TEST DATETIME
        # before contract
        self.assertEqual(
            contract._qualify_interval(datetime(2001, 10, 12), datetime(2001, 10, 16)),
            (datetime(2021, 7, 10, 0, 0, 0), datetime(2021, 7, 10, 0, 0, 0))
            )
        # after contract
        self.assertEqual(
            contract._qualify_interval(datetime(2022, 10, 12), datetime(2022, 10, 16)),
            (datetime(2021, 7, 31, 23, 59, 59, 999999), datetime(2021, 7, 31, 23, 59, 59, 999999))
            )
        # overlap forward contract
        self.assertEqual(
            contract._qualify_interval(datetime(2021, 7, 30), datetime(2021, 8, 31)),
            (datetime(2021, 7, 30, 0, 0, 0), datetime(2021, 7, 31, 23, 59, 59, 999999))
            )
        self.assertEqual(
            contract._qualify_interval(datetime(2021, 7, 30), datetime(2021, 7, 31)),
            (datetime(2021, 7, 30, 0, 0, 0), datetime(2021, 7, 31, 0, 0, 0))
            )
        self.assertEqual(
            contract._qualify_interval(datetime(2021, 7, 30), datetime(2021, 7, 31, 23, 59, 59)),
            (datetime(2021, 7, 30, 0, 0, 0), datetime(2021, 7, 31, 23, 59, 59))
            )
        # overlap backward contract
        self.assertEqual(
            contract._qualify_interval(datetime(2021, 7, 9), datetime(2021, 7, 12)),
            (datetime(2021, 7, 10, 0, 0, 0), datetime(2021, 7, 12, 0, 0, 0))
            )
        self.assertEqual(
            contract._qualify_interval(datetime(2021, 7, 10), datetime(2021, 7, 12)),
            (datetime(2021, 7, 10, 0, 0, 0), datetime(2021, 7, 12, 0, 0, 0))
            )

        # fully cover the contract
        self.assertEqual(
            contract._qualify_interval(datetime(2021, 6, 9), datetime(2021, 8, 12)),
            (datetime(2021, 7, 10, 0, 0, 0), datetime(2021, 7, 31, 23, 59, 59, 999999))
            )

    def test_11_get_resource_calendar_intervals_dates(self):
        start = datetime.strptime('2021-07-10', '%Y-%m-%d').date()
        end = datetime.strptime('2021-07-16', '%Y-%m-%d').date()
        contract = self.create_contract('open', 'normal', start, end)

        today = date(2021, 10, 1)

        self.assertEqual(
            contract._get_resource_calendar_intervals(),
            [(end if today > end else today, end if today > end else today, self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(date(2021, 7, 9), date(2021, 7, 10)),
            [(start, start, self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(date(2021, 7, 9), date(2021, 7, 11)),
            [(start, date(2021, 7, 11), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(date(2021, 7, 11), date(2021, 7, 15)),
            [(date(2021, 7, 11), date(2021, 7, 15), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(date(2021, 7, 15), date(2021, 7, 20)),
            [(date(2021, 7, 15), end, self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(date(2021, 7, 16), date(2021, 7, 20)),
            [(end, end, self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(date(2021, 7, 17), date(2021, 7, 20)),
            [(end, end, self.env.ref('resource.resource_calendar_std'))]
            )

    def test_12_get_resource_calendar_intervals_datetimes(self):
        start = datetime.strptime('2021-07-10', '%Y-%m-%d').date()
        end = datetime.strptime('2021-07-16', '%Y-%m-%d').date()
        contract = self.create_contract('open', 'normal', start, end)

        self.assertEqual(
            contract._get_resource_calendar_intervals(datetime(2021, 7, 9), datetime(2021, 7, 10)),
            [(datetime(2021, 7, 10), datetime(2021, 7, 10), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(datetime(2021, 7, 9), datetime(2021, 7, 11)),
            [(datetime(2021, 7, 10), datetime(2021, 7, 11), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(datetime(2021, 7, 11), datetime(2021, 7, 15)),
            [(datetime(2021, 7, 11), datetime(2021, 7, 15), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(datetime(2021, 7, 15), datetime(2021, 7, 20)),
            [(datetime(2021, 7, 15), datetime(2021, 7, 16, 23, 59, 59, 999999), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(datetime(2021, 7, 16), datetime(2021, 7, 20)),
            [(datetime(2021, 7, 16), datetime(2021, 7, 16, 23, 59, 59, 999999), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            contract._get_resource_calendar_intervals(datetime(2021, 7, 17), datetime(2021, 7, 20)),
            [(datetime(2021, 7, 16, 23, 59, 59, 999999), datetime(2021, 7, 16, 23, 59, 59, 999999), self.env.ref('resource.resource_calendar_std'))]
            )

    def test_21_get_resource_calendar_map(self):
        start1 = datetime.strptime('2021-07-10', '%Y-%m-%d').date()
        end1 = datetime.strptime('2021-07-16', '%Y-%m-%d').date()
        contracts = self.create_contract('open', 'normal', start1, end1)

        start2 = datetime.strptime('2021-07-20', '%Y-%m-%d').date()
        end2 = datetime.strptime('2021-08-03', '%Y-%m-%d').date()
        contracts |= self.create_contract('open', 'normal', start2, end2)

        today = date(2021, 10, 1)
        res_cal_map = contracts._get_resource_calendar_map()
        self.assertEqual(
            res_cal_map[contracts[0]],
            [(end1 if today > end1 else today, end1 if today > end1 else today, self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            res_cal_map[contracts[1]],
            [(end2 if today > end2 else today, end2 if today > end2 else today, self.env.ref('resource.resource_calendar_std'))]
            )

        res_cal_map = contracts._get_resource_calendar_map(date(2021, 6, 7), date(2021, 9, 9))
        self.assertEqual(
            res_cal_map[contracts[0]],
            [(date(2021, 7, 10), date(2021, 7, 16), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            res_cal_map[contracts[1]],
            [(date(2021, 7, 20), date(2021, 8, 3), self.env.ref('resource.resource_calendar_std'))]
            )

        res_cal_map = contracts._get_resource_calendar_map(datetime(2021, 6, 7), datetime(2021, 9, 9))
        self.assertEqual(
            res_cal_map[contracts[0]],
            [(datetime(2021, 7, 10, 0, 0, 0), datetime(2021, 7, 16, 23, 59, 59, 999999), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            res_cal_map[contracts[1]],
            [(datetime(2021, 7, 20, 0, 0, 0), datetime(2021, 8, 3, 23, 59, 59, 999999), self.env.ref('resource.resource_calendar_std'))]
            )

        contracts |= self.create_contract('open', 'normal', date(2021, 7, 17), date(2021, 7, 19))
        res_cal_map = contracts._get_resource_calendar_map(datetime(2021, 6, 7), datetime(2021, 9, 9))
        self.assertEqual(
            res_cal_map[contracts[0]],
            [(datetime(2021, 7, 10, 0, 0, 0), datetime(2021, 7, 16, 23, 59, 59, 999999), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            res_cal_map[contracts[1]],
            [(datetime(2021, 7, 20, 0, 0, 0), datetime(2021, 8, 3, 23, 59, 59, 999999), self.env.ref('resource.resource_calendar_std'))]
            )
        self.assertEqual(
            res_cal_map[contracts[2]],
            [(datetime(2021, 7, 17, 0, 0, 0), datetime(2021, 7, 19, 23, 59, 59, 999999), self.env.ref('resource.resource_calendar_std'))]
            )

    def test_31_get_unavailable_intervals_given_types(self):
        start1 = datetime.strptime('2021-07-9', '%Y-%m-%d').date()
        end1 = datetime.strptime('2021-07-16', '%Y-%m-%d').date()
        contracts = self.create_contract('open', 'normal', start1, end1)

        start2 = datetime.strptime('2021-07-20', '%Y-%m-%d').date()
        end2 = datetime.strptime('2021-08-03', '%Y-%m-%d').date()
        contracts |= self.create_contract('open', 'normal', start2, end2)

        with self.assertRaises(
            ValidationError,
            msg=_("The given start must be `datetime` type but got `%s` (%s)") % (type(date(2021, 7, 9)).__name__, date(2021, 7, 9))
            ):
            contracts._get_unavailable_intervals(date(2021, 7, 9), datetime(2021, 7, 10))
        with self.assertRaises(
            ValidationError,
            msg=_("The given end must be `datetime` type but got `%s` (%s)") % (type(date(2021, 7, 10)).__name__, date(2021, 7, 10))
            ):
            contracts._get_unavailable_intervals(datetime(2021, 7, 9), date(2021, 7, 10))

    def test_32_get_unavailable_intervals(self):
        start1 = datetime.strptime('2021-07-9', '%Y-%m-%d').date()
        end1 = datetime.strptime('2021-07-16', '%Y-%m-%d').date()
        contracts = self.create_contract('open', 'normal', start1, end1)

        start2 = datetime.strptime('2021-07-20', '%Y-%m-%d').date()
        end2 = datetime.strptime('2021-08-03', '%Y-%m-%d').date()
        contracts |= self.create_contract('open', 'normal', start2, end2)

        # the res.calendar has as tzinfo=<DstTzInfo 'Europe/Brussels' CEST+2:00:00 DST>
        resource_calendar_std = self.env.ref('resource.resource_calendar_std')

        intervals = contracts._get_unavailable_intervals(datetime(2021, 7, 9, 0, 0), datetime(2021, 7, 10))
        self.assertEqual(list(intervals.keys()), [contracts[0], contracts[1]])
        self.assertEqual(intervals[contracts[0]][resource_calendar_std], [
            (datetime(2021, 7, 9, 0, 0, tzinfo=UTC), datetime(2021, 7, 9, 6, 0, tzinfo=UTC)),  # 2am ~ 8am Europe/Brussels local time
            (datetime(2021, 7, 9, 10, 0, tzinfo=UTC), datetime(2021, 7, 9, 11, 0, tzinfo=UTC)),  # 12am ~ 13pm Europe/Brussels local time
            (datetime(2021, 7, 9, 15, 0, tzinfo=UTC), datetime(2021, 7, 10, 0, 0, tzinfo=UTC))  # 17pm ~ 02am next day Europe/Brussels local time
            ]
        )
        self.assertEqual(intervals[contracts[1]][resource_calendar_std], [])

        intervals = contracts._get_unavailable_intervals(datetime(2021, 7, 9, 0, 0), datetime(2021, 7, 10, 23, 59, 59, 999999))
        self.assertEqual(list(intervals.keys()), [contracts[0], contracts[1]])
        self.assertEqual(intervals[contracts[0]][resource_calendar_std], [
            (datetime(2021, 7, 9, 0, 0, tzinfo=UTC), datetime(2021, 7, 9, 6, 0, tzinfo=UTC)),
            (datetime(2021, 7, 9, 10, 0, tzinfo=UTC), datetime(2021, 7, 9, 11, 0, tzinfo=UTC)),
            (datetime(2021, 7, 9, 15, 0, tzinfo=UTC), datetime(2021, 7, 10, 23, 59, 59, 999999, tzinfo=UTC)),
            ]
        )
        self.assertEqual(intervals[contracts[1]][resource_calendar_std], [])

        intervals = contracts._get_unavailable_intervals(datetime(2021, 7, 16, 0, 0), datetime(2021, 7, 20, 23, 59, 59, 999999))
        self.assertEqual(list(intervals.keys()), [contracts[0], contracts[1]])
        self.assertEqual(intervals[contracts[0]][resource_calendar_std], [
            (datetime(2021, 7, 16, 0, 0, tzinfo=UTC), datetime(2021, 7, 16, 6, 0, tzinfo=UTC)),
            (datetime(2021, 7, 16, 10, 0, tzinfo=UTC), datetime(2021, 7, 16, 11, 0, tzinfo=UTC)),
            (datetime(2021, 7, 16, 15, 0, tzinfo=UTC), datetime(2021, 7, 16, 23, 59, 59, 999999, tzinfo=UTC)),
            ]
        )
        self.assertEqual(intervals[contracts[1]][resource_calendar_std], [
            (datetime(2021, 7, 20, 0, 0, tzinfo=UTC), datetime(2021, 7, 20, 6, 0, tzinfo=UTC)),
            (datetime(2021, 7, 20, 10, 0, tzinfo=UTC), datetime(2021, 7, 20, 11, 0, tzinfo=UTC)),
            (datetime(2021, 7, 20, 15, 0, tzinfo=UTC), datetime(2021, 7, 20, 23, 59, 59, 999999, tzinfo=UTC)),
            ])

    def test_33_get_unavailable_intervals_naive(self):
        start1 = datetime.strptime('2021-07-9', '%Y-%m-%d').date()
        end1 = datetime.strptime('2021-07-16', '%Y-%m-%d').date()
        contracts = self.create_contract('open', 'normal', start1, end1)

        start2 = datetime.strptime('2021-07-20', '%Y-%m-%d').date()
        end2 = datetime.strptime('2021-08-03', '%Y-%m-%d').date()
        contracts |= self.create_contract('open', 'normal', start2, end2)

        # the res.calendar has as tzinfo=<DstTzInfo 'Europe/Brussels' CEST+2:00:00 DST>
        resource_calendar_std = self.env.ref('resource.resource_calendar_std')

        intervals = contracts._get_unavailable_intervals(datetime(2021, 7, 9, 0, 0), datetime(2021, 7, 10), naive_datetime=True)
        self.assertEqual(list(intervals.keys()), [contracts[0], contracts[1]])
        self.assertEqual(intervals[contracts[0]][resource_calendar_std], [
            (datetime(2021, 7, 9, 0, 0), datetime(2021, 7, 9, 6, 0)),  # 2am ~ 8am Europe/Brussels local time
            (datetime(2021, 7, 9, 10, 0), datetime(2021, 7, 9, 11, 0)),  # 12am ~ 13pm Europe/Brussels local time
            (datetime(2021, 7, 9, 15, 0), datetime(2021, 7, 10, 0, 0))  # 17pm ~ 02am next day Europe/Brussels local time
            ]
        )
        self.assertEqual(intervals[contracts[1]][resource_calendar_std], [])

        intervals = contracts._get_unavailable_intervals(datetime(2021, 7, 9, 0, 0), datetime(2021, 7, 10, 23, 59, 59, 999999), naive_datetime=True)
        self.assertEqual(list(intervals.keys()), [contracts[0], contracts[1]])
        self.assertEqual(intervals[contracts[0]][resource_calendar_std], [
            (datetime(2021, 7, 9, 0, 0), datetime(2021, 7, 9, 6, 0)),
            (datetime(2021, 7, 9, 10, 0), datetime(2021, 7, 9, 11, 0)),
            (datetime(2021, 7, 9, 15, 0), datetime(2021, 7, 10, 23, 59, 59, 999999)),
            ]
        )
        self.assertEqual(intervals[contracts[1]][resource_calendar_std], [])

        intervals = contracts._get_unavailable_intervals(datetime(2021, 7, 16, 0, 0), datetime(2021, 7, 20, 23, 59, 59, 999999), naive_datetime=True)
        self.assertEqual(list(intervals.keys()), [contracts[0], contracts[1]])
        self.assertEqual(intervals[contracts[0]][resource_calendar_std], [
            (datetime(2021, 7, 16, 0, 0), datetime(2021, 7, 16, 6, 0)),
            (datetime(2021, 7, 16, 10, 0), datetime(2021, 7, 16, 11, 0)),
            (datetime(2021, 7, 16, 15, 0), datetime(2021, 7, 16, 23, 59, 59, 999999)),
            ]
        )
        self.assertEqual(intervals[contracts[1]][resource_calendar_std], [
            (datetime(2021, 7, 20, 0, 0), datetime(2021, 7, 20, 6, 0)),
            (datetime(2021, 7, 20, 10, 0), datetime(2021, 7, 20, 11, 0)),
            (datetime(2021, 7, 20, 15, 0), datetime(2021, 7, 20, 23, 59, 59, 999999)),
            ])

    def test_33_get_unavailable_intervals_naive_global_leaves(self):
        start1 = datetime.strptime('2021-07-9', '%Y-%m-%d').date()
        end1 = datetime.strptime('2021-07-16', '%Y-%m-%d').date()
        contracts = self.create_contract('open', 'normal', start1, end1)

        start2 = datetime.strptime('2021-07-20', '%Y-%m-%d').date()
        end2 = datetime.strptime('2021-08-03', '%Y-%m-%d').date()
        contracts |= self.create_contract('open', 'normal', start2, end2)

        # the res.calendar has as tzinfo=<DstTzInfo 'Europe/Brussels' CEST+2:00:00 DST>
        resource_calendar_std = self.env.ref('resource.resource_calendar_std')
        resource_calendar_std.write({
            'global_leave_ids': [
                (0, 0, {
                    'name': 'First Global Time-Off',
                    'date_from': datetime(2021, 7, 9, 6, 30),
                    'date_to': datetime(2021, 7, 9, 7, 30)
                    }
                ),
                (0, 0, {
                    'name': 'Second Global Time-Off',
                    'date_from': datetime(2021, 7, 9, 11, 0),
                    'date_to': datetime(2021, 7, 9, 12, 0)
                    }
                ), ]
            })

        intervals = contracts._get_unavailable_intervals(datetime(2021, 7, 9, 0, 0), datetime(2021, 7, 10), naive_datetime=True)
        self.assertEqual(list(intervals.keys()), [contracts[0], contracts[1]])
        self.assertEqual(intervals[contracts[0]][resource_calendar_std], [
            (datetime(2021, 7, 9, 0, 0), datetime(2021, 7, 9, 6, 0)),  # 2am ~ 8am Europe/Brussels local time
            (datetime(2021, 7, 9, 6, 30), datetime(2021, 7, 9, 7, 30)),
            (datetime(2021, 7, 9, 10, 0), datetime(2021, 7, 9, 12, 0)),  # 12am ~ 13pm Europe/Brussels local time
            (datetime(2021, 7, 9, 15, 0), datetime(2021, 7, 10, 0, 0))  # 17pm ~ 02am next day Europe/Brussels local time
            ]
        )
        self.assertEqual(intervals[contracts[1]][resource_calendar_std], [])

