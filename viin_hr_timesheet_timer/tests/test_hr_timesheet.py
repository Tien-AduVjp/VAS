from datetime import datetime
from unittest.mock import patch

from odoo.tests.common import tagged
from odoo import fields

from .common import Common


@tagged('-at_install', 'post_install')
class TestHrTimeSheet(Common):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.timesheet_1 = cls.env.ref('hr_timesheet.working_hours_testing')

    def test_get_elapsed_time(self):
        self.timesheet_1.date_start = '2021-10-02 08:00:00'
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 9, 30, 0)):
            self.assertEqual(self.timesheet_1._get_elapsed_time(), 1.5)
