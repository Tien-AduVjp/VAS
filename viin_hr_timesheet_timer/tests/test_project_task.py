from unittest.mock import patch
from datetime import date, datetime

from odoo.tests.common import tagged
from odoo import fields
from odoo.exceptions import UserError, AccessError

from .common import Common


@tagged('-at_install', 'post_install')
class TestPorjectTaskManager(Common):
    """
        Test Admin as login user with the right:
            Project:      Administrator
            Timesheet:    Administrator
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Ensure that Marc Demo has the right to take action
        cls.project_r_d.write({
            'allowed_internal_user_ids': [
                (6, 0, cls.user_demo.ids)
            ]
        })

    def test_01_compute_timesheet_wip(self):
        """
        """
        wip_timesheet_init = self.r_d_task1.timesheet_ids.filtered(lambda t: t.date_start and not t.date_end)
        self.assertFalse(wip_timesheet_init)

        init_number_of_timesheets = len(self.r_d_task1.timesheet_ids)

        self.r_d_task1.with_user(self.user_demo).action_start()

        self.assertEqual(len(self.r_d_task1.timesheet_ids), init_number_of_timesheets + 1)

        wip_timesheet = self.r_d_task1.timesheet_ids.filtered(lambda t: t.date_start and not t.date_end)
        self.assertTrue(wip_timesheet)

        self.r_d_task1.with_user(self.user_demo)._compute_timesheet_wip()
        self.assertTrue(self.r_d_task1.timesheet_wip)

    def test_02_compute_is_login_user_doing(self):
        self.r_d_task1.with_user(self.user_demo).action_start()
        self.r_d_task1.with_user(self.user_demo)._compute_login_user_is_doing()

        self.assertTrue(self.r_d_task1.with_user(self.user_demo).is_login_user_doing)

    def test_01_log_timesheet_manager(self):
        timesheets_init = self.r_d_task1.timesheet_ids
        self.assertEqual(len(timesheets_init), 27)

        # case 1:
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 2)), \
        patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 0, 0, 0)):
            self.r_d_task1.with_user(self.user_demo).action_start()

        wip_timesheet = self.r_d_task1.timesheet_ids.filtered(lambda t: t.date_start and not t.date_end)
        self.assertEqual(len(wip_timesheet), 1)

        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 1, 30, 0)):
            self.r_d_task1.with_user(self.user_demo).action_stop()

        new_logged_timesheet = self.r_d_task1.timesheet_ids - timesheets_init
        self.assertEqual(len(new_logged_timesheet), 1)

        self.assertRecordValues(new_logged_timesheet, [
            {
                'date_start': datetime(2021, 10, 2),
                'date_end': datetime(2021, 10, 2, 1, 30),
                'unit_amount': 1.5,
                'employee_id': self.user_demo.employee_id.id,
                'name': self.r_d_task1.name,
            }
        ])

    def test_02_log_timesheet(self):
        """
            case 2: Must Start loging and stop the logging on a same day
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 2)), \
        patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 15, 0, 0)):
            self.r_d_task1.with_user(self.user_demo).action_start()

        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 3, 8, 0, 0)):
            with self.assertRaises(UserError):
                self.r_d_task1.with_user(self.user_demo).action_stop()

    def test_03_log_timesheet(self):
        """
            Test 1 user cannot log multi timesheets at the same time
        """
        self.r_d_task1.with_user(self.user_demo).action_start()
        with self.assertRaises(UserError):
            self.r_d_task2.with_user(self.user_demo).action_start()

    def test_01_wip_timesheet_unfollow_task(self):
        '''
            Test case:
                user Marc Demo is having a WIP timesheet on task1
                he then unfollowes this task himself
            Expect:
                The wip timesheet will automatically be ended with appropriated end time

            Note:
                If the date_start and end_date is not the same, an UserError is raised instead
        '''
        current_timesheets = self.r_d_task1.timesheet_ids

        # Start button with mocked time
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 2)), \
        patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 0, 0, 0)):
            self.r_d_task1.with_user(self.user_demo).action_start()

        wip_timesheet_before = self.r_d_task1.timesheet_ids - current_timesheets
        self.assertTrue(wip_timesheet_before)

        # Marc Demo unfollows himself with mocked time
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 1, 30, 0)):
            self.r_d_task1.with_user(self.user_demo).message_unsubscribe(partner_ids=self.user_demo.partner_id.ids)

        # Get WIP timesheet among all the timesheets of task1
        wip_timesheet_after = self.r_d_task1.timesheet_ids.filtered(
            lambda ts: ts.unit_amount == 0.0 and ts.employee_id.id == self.user_demo.employee_id.id
        )
        self.assertFalse(wip_timesheet_after)

    def test_02_wip_timesheet_unfollow_task(self):
        '''
            Test case:
                user Marc Demo is having a WIP timesheet on task1
                he then gets unfollowed on this task by Admin
            Expect:
                The wip timesheet will automatically be ended with appropriated end time

            Note:
                If the date_start and end_date is not the same, an UserError is raised instead
        '''
        current_timesheets = self.r_d_task1.timesheet_ids

        # Start button with mocked time
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 2)), \
        patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 0, 0, 0)):
            self.r_d_task1.with_user(self.user_demo).action_start()

        wip_timesheet_before = self.r_d_task1.timesheet_ids - current_timesheets
        self.assertTrue(wip_timesheet_before)

        # Admin unfollows user demo with mocked time
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 1, 30, 0)):
            self.r_d_task1.message_unsubscribe(partner_ids=self.user_demo.partner_id.ids)

        # Get WIP timesheet among all the timesheets of task1
        wip_timesheet_after = self.r_d_task1.timesheet_ids.filtered(
            lambda ts: ts.unit_amount == 0.0 and ts.employee_id.id == self.user_demo.employee_id.id
        )
        self.assertFalse(wip_timesheet_after)
