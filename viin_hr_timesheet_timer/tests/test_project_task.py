from unittest.mock import patch
from datetime import date, datetime

from odoo.tests.common import tagged
from odoo import fields
from odoo.exceptions import UserError

from .common import Common


@tagged('-at_install', 'post_install')
class TestPorjectTask(Common):
    
    def test_01_log_timesheet(self):
        
        self.assertFalse(self.task1.timesheet_ids)
        
        # case 1:
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 2)), \
        patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 0, 0, 0)):
            self.task1.with_user(self.user_demo).action_start()
        
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 1, 30, 0)):
            self.task1.with_user(self.user_demo).action_stop()
            
        self.assertEqual(self.task1.timesheet_ids.unit_amount, 1.5)
        self.assertEqual(self.task1.timesheet_ids.date_start, datetime(2021, 10, 2))
        self.assertEqual(self.task1.timesheet_ids.employee_id, self.user_demo.employee_id)
        self.assertEqual(self.task1.timesheet_ids.name, self.task1.name)
    
    def test_02_log_timesheet(self):
        # case 2:
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 2)), \
        patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 15, 0, 0)):
            self.task1.with_user(self.user_demo).action_start()
        
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 3, 8, 0, 0)):
            with self.assertRaises(UserError):
                self.task1.with_user(self.user_demo).action_stop()
    
    def test_03_log_timesheet(self):
        """
            Test 1 user log multi timesheets at the same time
        """
        self.task1.with_user(self.user_admin).action_start()
        with self.assertRaises(UserError):
            self.task2.with_user(self.user_admin).action_start()
    
    def test_01_compute_timesheet_wip(self):
        self.task1.with_user(self.user_demo).action_start()
        self.task1.with_user(self.user_demo)._compute_timesheet_wip()
        self.assertTrue(self.task1.timesheet_wip)
        
    def test_02_compute_timesheet_wip(self):
        self.task1.with_user(self.user_demo).action_start()
        self.task2.with_user(self.user_admin).action_start()
        
        tasks = self.task1 + self.task2
        tasks.with_user(self.user_admin).with_context(all_wip_timesheet=True)._compute_timesheet_wip()
        
        self.assertTrue(self.task1.timesheet_wip)
        self.assertTrue(self.task2.timesheet_wip)
        
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
        current_timesheets = self.task1.timesheet_ids
        
        # Start button with mocked time
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 2)), \
        patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 0, 0, 0)):
            self.task1.with_user(self.user_demo).action_start()
        
        wip_timesheet_before = self.task1.timesheet_ids - current_timesheets 
        self.assertTrue(wip_timesheet_before)
        
        # Marc Demo unfollows himself with mocked time
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 1, 30, 0)):
            self.task1.with_user(self.user_demo).message_unsubscribe(partner_ids=self.user_demo.partner_id.ids)
        
        # Get WIP timesheet among all the timesheets of task1
        wip_timesheet_after = self.task1.timesheet_ids.filtered(
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
        current_timesheets = self.task1.timesheet_ids
        
        # Start button with mocked time
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 2)), \
        patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 0, 0, 0)):
            self.task1.with_user(self.user_demo).action_start()
        
        wip_timesheet_before = self.task1.timesheet_ids - current_timesheets 
        self.assertTrue(wip_timesheet_before)
        
        # Admin unfollows user demo with mocked time
        with patch.object(fields.Datetime, 'now', lambda: datetime(2021, 10, 2, 1, 30, 0)):
            self.task1.message_unsubscribe(partner_ids=self.user_demo.partner_id.ids)
        
        # Get WIP timesheet among all the timesheets of task1
        wip_timesheet_after = self.task1.timesheet_ids.filtered(
            lambda ts: ts.unit_amount == 0.0 and ts.employee_id.id == self.user_demo.employee_id.id
        )
        self.assertFalse(wip_timesheet_after)
