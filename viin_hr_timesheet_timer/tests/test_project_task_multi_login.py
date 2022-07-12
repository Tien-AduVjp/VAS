from unittest.mock import patch
from datetime import date, datetime

from odoo.tests.common import tagged
from odoo import fields

from .common import Common


@tagged('-at_install', 'post_install')
class TestPorjectTaskMultiLogin(Common):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Ensure that Marc Demo has the right to take action
        cls.project_r_d.write({
            'allowed_internal_user_ids': [
                (6, 0, cls.user_demo.ids)
            ]
        })

    def test_01_multi_login(self):
        """
        """
        timesheets_t1_init = self.r_d_task1.timesheet_ids
        timesheets_t2_init = self.r_d_task2.timesheet_ids
        self.assertEqual(len(self.r_d_task1.timesheet_ids), 27)
        self.assertEqual(len(self.r_d_task2.timesheet_ids), 15)

        self.r_d_task1.with_user(self.user_admin).action_start()
        self.r_d_task2.with_user(self.user_demo).action_start()

        tasks = self.r_d_task1 + self.r_d_task2
        tasks.with_context(all_wip_timesheet=True)._compute_timesheet_wip()

        self.r_d_task1.with_user(self.user_demo)._compute_login_user_is_doing()
        self.assertFalse(self.r_d_task1.with_user(self.user_demo).is_login_user_doing)

        self.r_d_task2.with_user(self.user_demo)._compute_login_user_is_doing()
        self.assertTrue(self.r_d_task2.with_user(self.user_demo).is_login_user_doing)

        self.assertTrue(self.r_d_task1.timesheet_wip)
        self.assertTrue(self.r_d_task2.timesheet_wip)

    def test_02_multi_login(self):
        """
        """
        timesheets_t1_init = self.r_d_task1.timesheet_ids
        self.assertEqual(len(self.r_d_task1.timesheet_ids), 27)

        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 2)), \
        patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 0, 0, 0)):
            self.r_d_task1.with_user(self.user_admin).with_context(tracking_disable=True).action_start()
            self.r_d_task1.with_user(self.user_demo).with_context(tracking_disable=True).action_start()

        # Task 1 now is currently being logged timesheet by both Admin and Demo
        wip_timesheet_v1 = self.r_d_task1.timesheet_ids.filtered(lambda t: t.unit_amount == 0)
        self.assertEqual(len(wip_timesheet_v1), 2)

        # Admin stops the log timesheet on task 2
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 1, 30, 0)):
            self.r_d_task1.with_user(self.user_admin).action_stop()

        wip_timesheet_v2 = self.r_d_task1.timesheet_ids.filtered(lambda t: t.unit_amount == 0)
        self.assertEqual(len(wip_timesheet_v2), 1)

        self.assertEqual(wip_timesheet_v2.employee_id.name, self.user_demo.name)
