from datetime import datetime, date
from unittest.mock import patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestHrContracts(TestCommon):

    def patch_datetime_now(self, now):
        return patch('odoo.fields.Datetime.now', return_value=now)

    def patch_date_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.today', return_value=today)

    def _create_contracts(self):
        contract1 = self.create_contract('open', 'normal', date(2021, 6, 2), date(2021, 6, 16))
        contract2 = self.create_contract('open', 'normal', date(2021, 6, 17), date(2021, 7, 4))
        contract3 = self.create_contract('open', 'normal', date(2021, 8, 1))
        return contract1, contract2, contract3

    def test_01__get_resource_calendar_intervals_raise(self):
        with self.assertRaises(ValidationError):
            self.employee._get_resource_calendar_intervals(datetime(2021, 7, 1), date(2021, 7, 4))
        with self.assertRaises(ValidationError):
            self.employee._get_resource_calendar_intervals(date(2021, 7, 1), datetime(2021, 7, 4))
        with self.assertRaises(ValidationError):
            self.employee._get_resource_calendar_intervals(date(2021, 7, 9), date(2021, 7, 4))

    def test_02__get_resource_calendar_intervals__no_given_date(self):
        contract1, contract2, contract3 = self._create_contracts()

        resource_calendar_std = self.env.ref('resource.resource_calendar_std')
        with self.patch_date_today(date(2021, 6, 1)):
            intervals = self.employee._get_resource_calendar_intervals()[self.employee]
            # ensure no contract here
            self.assertEqual(list(intervals.keys()), [False])
            # ensure
            self.assertEqual(intervals[False], [(date(2021, 6, 1), date(2021, 6, 1), resource_calendar_std)])

        with self.patch_date_today(date(2021, 6, 2)):
            intervals = self.employee._get_resource_calendar_intervals()[self.employee]
            # ensure no contract here
            self.assertEqual(list(intervals.keys()), [contract1])
            # ensure
            self.assertEqual(intervals[contract1], [(date(2021, 6, 2), date(2021, 6, 2), resource_calendar_std)])

        with self.patch_date_today(date(2021, 6, 17)):
            intervals = self.employee._get_resource_calendar_intervals()[self.employee]
            # ensure no contract here
            self.assertEqual(list(intervals.keys()), [contract2])
            # ensure
            self.assertEqual(intervals[contract2], [(date(2021, 6, 17), date(2021, 6, 17), resource_calendar_std)])

        with self.patch_date_today(date(2021, 8, 1)):
            intervals = self.employee._get_resource_calendar_intervals()[self.employee]
            # ensure no contract here
            self.assertEqual(list(intervals.keys()), [contract3])
            # ensure
            self.assertEqual(intervals[contract3], [(date(2021, 8, 1), date(2021, 8, 1), resource_calendar_std)])

        with self.patch_date_today(date(2021, 10, 1)):
            intervals = self.employee._get_resource_calendar_intervals()[self.employee]
            # ensure no contract here
            self.assertEqual(list(intervals.keys()), [contract3])
            # ensure
            self.assertEqual(intervals[contract3], [(date(2021, 10, 1), date(2021, 10, 1), resource_calendar_std)])

    def test_03__get_resource_calendar_intervals__single_date_start__date_type(self):
        contract1, contract2, contract3 = self._create_contracts()

        resource_calendar_std = self.env.ref('resource.resource_calendar_std')

        # no date_end passed, the intervals will start from the given date_start to today
        intervals = self.employee._get_resource_calendar_intervals(date(2021, 6, 1))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (date(2021, 6, 1), date(2021, 6, 1), resource_calendar_std),
                    (date(2021, 7, 5), date(2021, 7, 31), resource_calendar_std)
                    ],
                contract1: [
                    (date(2021, 6, 2), date(2021, 6, 16), resource_calendar_std)
                    ],
                contract2: [
                    (date(2021, 6, 17), date(2021, 7, 4), resource_calendar_std)
                    ],
                contract3: [
                    (date(2021, 8, 1), fields.Date.today(), resource_calendar_std)
                    ]
                }
            )

        intervals = self.employee._get_resource_calendar_intervals(date(2021, 6, 2))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (date(2021, 7, 5), date(2021, 7, 31), resource_calendar_std)
                    ],
                contract1: [
                    (date(2021, 6, 2), date(2021, 6, 16), resource_calendar_std)
                    ],
                contract2: [
                    (date(2021, 6, 17), date(2021, 7, 4), resource_calendar_std)
                    ],
                contract3: [
                    (date(2021, 8, 1), fields.Date.today(), resource_calendar_std)
                    ]
                }
            )

        intervals = self.employee._get_resource_calendar_intervals(date(2021, 6, 5))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (date(2021, 7, 5), date(2021, 7, 31), resource_calendar_std)
                    ],
                contract1: [
                    (date(2021, 6, 5), date(2021, 6, 16), resource_calendar_std)
                    ],
                contract2: [
                    (date(2021, 6, 17), date(2021, 7, 4), resource_calendar_std)
                    ],
                contract3: [
                    (date(2021, 8, 1), fields.Date.today(), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(date(2021, 7, 30))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (date(2021, 7, 30), date(2021, 7, 31), resource_calendar_std)
                    ],
                contract3: [
                    (date(2021, 8, 1), fields.Date.today(), resource_calendar_std)
                    ]
                }
            )

    def test_04__get_resource_calendar_intervals__single_date_start__datetime_type(self):
        contract1, contract2, contract3 = self._create_contracts()

        resource_calendar_std = self.env.ref('resource.resource_calendar_std')

        # patch_datetime_now to ensure now is the same at all the time during execution
        now = datetime(2021, 10, 1, 8, 0, 0)
        with self.patch_datetime_now(now):
            # no date_end passed, the intervals will start from the given date_start to today
            intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 6, 1))[self.employee]
            self.assertDictEqual(
                intervals,
                {
                    False: [
                        (datetime(2021, 6, 1), datetime(2021, 6, 1, 23, 59, 59, 999999), resource_calendar_std),
                        (datetime(2021, 7, 5), datetime(2021, 7, 31, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract1: [
                        (datetime(2021, 6, 2), datetime(2021, 6, 16, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract2: [
                        (datetime(2021, 6, 17), datetime(2021, 7, 4, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract3: [
                        (datetime(2021, 8, 1), now, resource_calendar_std)
                        ]
                    }
                )

            intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 6, 2))[self.employee]
            self.assertDictEqual(
                intervals,
                {
                    False: [
                        (datetime(2021, 7, 5), datetime(2021, 7, 31, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract1: [
                        (datetime(2021, 6, 2), datetime(2021, 6, 16, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract2: [
                        (datetime(2021, 6, 17), datetime(2021, 7, 4, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract3: [
                        (datetime(2021, 8, 1), now, resource_calendar_std)
                        ]
                    }
                )

            intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 6, 5))[self.employee]
            self.assertDictEqual(
                intervals,
                {
                    False: [
                        (datetime(2021, 7, 5), datetime(2021, 7, 31, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract1: [
                        (datetime(2021, 6, 5), datetime(2021, 6, 16, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract2: [
                        (datetime(2021, 6, 17), datetime(2021, 7, 4, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract3: [
                        (datetime(2021, 8, 1), now, resource_calendar_std)
                        ]
                    }
                )
            intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 7, 30))[self.employee]
            self.assertDictEqual(
                intervals,
                {
                    False: [
                        (datetime(2021, 7, 30), datetime(2021, 7, 31, 23, 59, 59, 999999), resource_calendar_std)
                        ],
                    contract3: [
                        (datetime(2021, 8, 1), now, resource_calendar_std)
                        ]
                    }
                )

    def test_05__get_resource_calendar_intervals__single_date_end__date_type(self):
        contract1, contract2, contract3 = self._create_contracts()

        resource_calendar_std = self.env.ref('resource.resource_calendar_std')

        # no date_end passed, the intervals will start from the given date_start to today
        intervals = self.employee._get_resource_calendar_intervals(date_end=date(2021, 6, 1))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (date(2021, 6, 1), date(2021, 6, 1), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(date_end=date(2021, 6, 2))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                contract1: [
                    (date(2021, 6, 2), date(2021, 6, 2), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(date_end=date(2021, 6, 5))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                contract1: [
                    (date(2021, 6, 5), date(2021, 6, 5), resource_calendar_std)
                    ]
                }
            )

    def test_06__get_resource_calendar_intervals__start_and_end_date_type(self):
        """
        contract1 = self.create_contract('open', 'normal', date(2021, 6, 2), date(2021, 6, 16))
        contract2 = self.create_contract('open', 'normal', date(2021, 6, 17), date(2021, 7, 4))
        contract3 = self.create_contract('open', 'normal', date(2021, 8, 1))
        """
        contract1, contract2, contract3 = self._create_contracts()

        resource_calendar_std = self.env.ref('resource.resource_calendar_std')

        intervals = self.employee._get_resource_calendar_intervals(date(2021, 5, 25), date(2021, 6, 1))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (date(2021, 5, 25), date(2021, 6, 1), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(date(2021, 5, 25), date(2021, 6, 2))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (date(2021, 5, 25), date(2021, 6, 1), resource_calendar_std)
                    ],
                contract1: [
                    (date(2021, 6, 2), date(2021, 6, 2), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(date(2021, 6, 2), date(2021, 6, 10))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                contract1: [
                    (date(2021, 6, 2), date(2021, 6, 10), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(date(2021, 6, 2), date(2021, 6, 17))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                contract1: [
                    (date(2021, 6, 2), date(2021, 6, 16), resource_calendar_std)
                    ],
                contract2: [
                    (date(2021, 6, 17), date(2021, 6, 17), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(date(2021, 6, 2), date(2021, 7, 31))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (date(2021, 7, 5), date(2021, 7, 31), resource_calendar_std)
                    ],
                contract1: [
                    (date(2021, 6, 2), date(2021, 6, 16), resource_calendar_std)
                    ],
                contract2: [
                    (date(2021, 6, 17), date(2021, 7, 4), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(date(2021, 5, 30), date(2021, 9, 1))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (date(2021, 5, 30), date(2021, 6, 1), resource_calendar_std),
                    (date(2021, 7, 5), date(2021, 7, 31), resource_calendar_std)
                    ],
                contract1: [
                    (date(2021, 6, 2), date(2021, 6, 16), resource_calendar_std)
                    ],
                contract2: [
                    (date(2021, 6, 17), date(2021, 7, 4), resource_calendar_std)
                    ],
                contract3: [
                    (date(2021, 8, 1), date(2021, 9, 1), resource_calendar_std)
                    ]
                }
            )

    def test_07__get_resource_calendar_intervals__start_and_end_datetime_type(self):
        """
        contract1 = self.create_contract('open', 'normal', date(2021, 6, 2), date(2021, 6, 16))
        contract2 = self.create_contract('open', 'normal', date(2021, 6, 17), date(2021, 7, 4))
        contract3 = self.create_contract('open', 'normal', date(2021, 8, 1))
        """
        contract1, contract2, contract3 = self._create_contracts()

        resource_calendar_std = self.env.ref('resource.resource_calendar_std')

        intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 5, 25), datetime(2021, 6, 1, 23, 59, 59, 999999))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (datetime(2021, 5, 25), datetime(2021, 6, 1, 23, 59, 59, 999999), resource_calendar_std)
                    ],
                }
            )

        intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 5, 25), datetime(2021, 6, 2))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (datetime(2021, 5, 25), datetime(2021, 6, 1, 23, 59, 59, 999999), resource_calendar_std)
                    ],
                # the last 1 microsecond has contract
                contract1: [
                    (datetime(2021, 6, 2), datetime(2021, 6, 2), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 5, 25), datetime(2021, 6, 2, 23, 59, 59, 999999))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (datetime(2021, 5, 25), datetime(2021, 6, 1, 23, 59, 59, 999999), resource_calendar_std)
                    ],
                contract1: [
                    (datetime(2021, 6, 2), datetime(2021, 6, 2, 23, 59, 59, 999999), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 6, 2), datetime(2021, 6, 10))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                contract1: [
                    (datetime(2021, 6, 2), datetime(2021, 6, 10), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 6, 2), datetime(2021, 6, 17))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                contract1: [
                    (datetime(2021, 6, 2), datetime(2021, 6, 16, 23, 59, 59, 999999), resource_calendar_std)
                    ],
                contract2: [
                    (datetime(2021, 6, 17), datetime(2021, 6, 17), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 6, 2), datetime(2021, 7, 31))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (datetime(2021, 7, 5), datetime(2021, 7, 31), resource_calendar_std)
                    ],
                contract1: [
                    (datetime(2021, 6, 2), datetime(2021, 6, 16, 23, 59, 59, 999999), resource_calendar_std)
                    ],
                contract2: [
                    (datetime(2021, 6, 17), datetime(2021, 7, 4, 23, 59, 59, 999999), resource_calendar_std)
                    ]
                }
            )
        intervals = self.employee._get_resource_calendar_intervals(datetime(2021, 5, 30), datetime(2021, 9, 1))[self.employee]
        self.assertDictEqual(
            intervals,
            {
                False: [
                    (datetime(2021, 5, 30), datetime(2021, 6, 1, 23, 59, 59, 999999), resource_calendar_std),
                    (datetime(2021, 7, 5), datetime(2021, 7, 31, 23, 59, 59, 999999), resource_calendar_std)
                    ],
                contract1: [
                    (datetime(2021, 6, 2), datetime(2021, 6, 16, 23, 59, 59, 999999), resource_calendar_std)
                    ],
                contract2: [
                    (datetime(2021, 6, 17), datetime(2021, 7, 4, 23, 59, 59, 999999), resource_calendar_std)
                    ],
                contract3: [
                    (datetime(2021, 8, 1), datetime(2021, 9, 1), resource_calendar_std)
                    ]
                }
            )
