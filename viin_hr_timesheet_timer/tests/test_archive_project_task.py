from odoo.tests.common import tagged
from odoo import fields
from odoo.exceptions import UserError

from .common import Common


@tagged('-at_install', 'post_install')
class TestArchiveProjectTask(Common):
    """
        Test Admin as login user with the right:
            Project:      Administrator
            Timesheet:    Administrator
    """
    def test_01_log_timesheet_on_archived_task(self):
        """
            Test feature:
                Cannot log timesheet on an archived task using the Button
        """
        self.task1.action_archive()

        with self.assertRaises(UserError):
            self.task1.action_start()

    def test_02_log_timesheet_not_allow_archive_task(self):
        """
            Test feature:
                Cannot archive a task with minimum 1 wip timesheet
        """
        self.task1.with_user(self.user_admin).action_start()

        with self.assertRaises(UserError):
            self.task1.with_user(self.user_admin).action_archive()
            
    def test_03_log_multi_timesheet_ignore_archived_task(self):
        """
            Test feature:
                If a user:
                    does not have any WIP timesheet on any un-archived task
                    BUT, have WIP timesheet on an archived task
                then:
                    still allows user to log timesheet on a new un-archived task
        """
        # Archive task 2
        self.task2.with_user(self.user_admin).action_archive()

        # Purposely make that Admin user has one WIP timesheet on task 2
        self.env['account.analytic.line'].with_user(self.user_admin).create({
            'project_id': self.task2.project_id.id,
            'task_id': self.task2.id,
            'name': 'Test WIP timesheet 1 Admin',
            'unit_amount': 0.0,
            'employee_id': self.user_admin.employee_id.id,
        })
        wip_timesheet = self.env['account.analytic.line'].with_context(active_test=False).search([
            ('employee_id', '!=', False),
            ('project_id', '=', self.task2.project_id.id),
            ('task_id', '=', self.task2.id),
            ('employee_id', '=', self.user_admin.employee_id.id),
            ('unit_amount', '=', 0.0),
        ])
        self.assertEqual(len(wip_timesheet), 1, "Expect: Admin user has now 1 WIP timesheet on an archived task.")

        # Admin user still can log timesheet on task 1 despite of having a wip timesheet on task 2
        self.task1.with_user(self.user_admin).action_start()
        
    def test_04_log_timesheet_archived_project(self):
        """
            Test feature:
                Not allow to use the Button to log timesheet on an un-archived task but in an archived project
        """
        project1 = self.env.ref('project.project_project_1')
        task8 = project1.task_ids[0]

        project1.action_archive()
        task8.action_unarchive()

        with self.assertRaises(UserError):
            task8.action_start()
            
    def test_05_log_timesheet_archived_project(self):
        """
            Test feature:
                Not allow to archive a project while having minimum 1 wip timesheet on project level. 
        """
        project1 = self.env.ref('project.project_project_1')
        project1.write({
            'timesheet_ids': [
                (0, 0, {
                    'date': fields.Date.today(),
                    'time_start': 8,
                    'employee_id': self.user_admin.employee_id.id,
                    'name': 'Project has WIP timesheet on itself',
                    'unit_amount': 0.0
                })
            ]
        })
        
        with self.assertRaises(UserError):
            project1.action_archive()
