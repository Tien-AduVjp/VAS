from odoo.tests.common import tagged
from odoo.exceptions import AccessError

from .common import Common


@tagged('-at_install', 'post_install')
class TestPorjectTaskManager(Common):

    def _get_test_timesheet(self, task, user):
        test_timesheets = task.timesheet_ids.filtered(
            lambda t: t.employee_id.id == user.employee_id.id
        )
        return test_timesheets

    def test_01_test_access_rule_with_user(self):
        """
            project has privacy_visibility = followers
            test with Admin

            Test with CREATE right
        """

        self.assertRecordValues(self.project_r_d, [
            {
                'privacy_visibility': 'followers',
                'allowed_internal_user_ids': [],
            }
        ])
        self.assertFalse(self.r_d_task1.allowed_user_ids)

        with self.assertRaises(AccessError):
            self.r_d_task1.with_user(self.user_demo).action_start()

        admin_timesheets_before = self.r_d_task1.timesheet_ids.filtered(
            lambda t: t.employee_id.id == self.user_admin.employee_id.id
        )
        admin_timesheets_before = self._get_test_timesheet(self.r_d_task1, self.user_admin)
        self.assertEqual(len(admin_timesheets_before), 2)

        self.r_d_task1.with_user(self.user_admin).action_start()
        self.r_d_task1.with_user(self.user_admin).action_stop()

        admin_timesheets_after = self._get_test_timesheet(self.r_d_task1, self.user_admin)
        self.assertEqual(len(admin_timesheets_after), 3)

    def test_02_test_access_rule_with_user(self):
        """
            project has privacy_visibility = followers
            test with Marc Demo as USER

            Test with CREATE right
        """
        self.assertRecordValues(self.project_r_d, [
            {
                'privacy_visibility': 'followers',
                'allowed_internal_user_ids': [],
            }
        ])
        self.assertFalse(self.r_d_task1.allowed_user_ids)

        with self.assertRaises(AccessError), self.cr.savepoint():
            self.r_d_task1.with_user(self.user_demo).action_start()

        marc_demo_timesheets_before = self._get_test_timesheet(self.r_d_task1, self.user_demo)
        self.assertEqual(len(marc_demo_timesheets_before), 1)

        self.project_r_d.write({
            'allowed_internal_user_ids': [
                (6, 0, self.user_demo.ids)
            ]
        })

        self.r_d_task1.with_user(self.user_demo).action_start()
        self.r_d_task1.with_user(self.user_demo).action_stop()

        marc_demo_timesheets_after = self._get_test_timesheet(self.r_d_task1, self.user_demo)
        self.assertEqual(len(marc_demo_timesheets_after), 2)

    def test_03_test_access_rule_with_user(self):
        """
            project has privacy_visibility = followers

            Test with WRITE right
        """
        self.assertRecordValues(self.project_r_d, [
            {
                'privacy_visibility': 'followers',
                'allowed_internal_user_ids': [],
            }
        ])
        self.assertFalse(self.r_d_task1.allowed_user_ids)

        admin_timesheet = self._get_test_timesheet(self.r_d_task1, self.user_admin)[0]
        marc_demo_timesheet = self._get_test_timesheet(self.r_d_task1, self.user_demo)[0]

        admin_timesheet.with_user(self.user_admin).write({'time_start': 8})
        marc_demo_timesheet.with_user(self.user_admin).write({'time_start': 8})

        with self.assertRaises(AccessError), self.cr.savepoint():
            marc_demo_timesheet.with_user(self.user_demo).write({'time_start': 9})

        self.project_r_d.write({
            'allowed_internal_user_ids': [
                (6, 0, self.user_demo.ids)
            ]
        })

        marc_demo_timesheet.with_user(self.user_demo).write({'time_start': 9})

    def test_04_test_access_rule_with_user(self):
        """
            project has privacy_visibility = followers

            Test with UNLINK right
        """
        self.assertRecordValues(self.project_r_d, [
            {
                'privacy_visibility': 'followers',
                'allowed_internal_user_ids': [],
            }
        ])
        self.assertFalse(self.r_d_task1.allowed_user_ids)

        admin_timesheets = self._get_test_timesheet(self.r_d_task1, self.user_admin)
        marc_demo_timesheet = self._get_test_timesheet(self.r_d_task1, self.user_demo)[0]

        a_timesheet = self.r_d_task1.timesheet_ids.filtered(
            lambda t: t.employee_id.id != self.user_demo.employee_id.id and \
                      t.employee_id.id != self.user_admin.employee_id.id
        )[0]

        # On this task:
        #     Admin has 2 logged timesheets
        #     Demo  has 1 logged timesheet
        self.assertEqual(len(admin_timesheets), 2)
        self.assertEqual(len(marc_demo_timesheet), 1)
        self.assertEqual(len(a_timesheet), 1)

        # Admin unlinks 1 of the 2 timesheets of Admin
        admin_timesheets[0].with_user(self.user_admin).unlink()
        # Admin unlinks timesheet of other
        a_timesheet.with_user(self.user_admin).unlink()

        # Marc Demo has not the right to take action
        with self.assertRaises(AccessError), self.cr.savepoint():
            marc_demo_timesheet.with_user(self.user_demo).unlink()

        # Add the right for Marc Demo
        self.project_r_d.write({
            'allowed_internal_user_ids': [
                (6, 0, self.user_demo.ids)
            ]
        })

        marc_demo_timesheet_before_unlink = self._get_test_timesheet(self.r_d_task1, self.user_demo)[0]
        self.assertEqual(len(marc_demo_timesheet_before_unlink), 1)

        # Now Marc Demo can unlink his own timesheet
        marc_demo_timesheet.with_user(self.user_demo).unlink()

        marc_demo_timesheet_after_unlink = self._get_test_timesheet(self.r_d_task1, self.user_demo)
        self.assertFalse(marc_demo_timesheet_after_unlink)

        # Admin has only 1 logged timesheet left
        admin_last_timesheet = self._get_test_timesheet(self.r_d_task1, self.user_admin)
        self.assertEqual(len(admin_last_timesheet), 1)

        # Marc Demo doesn't has the right to take action on other's timesheet
        with self.assertRaises(AccessError), self.cr.savepoint():
            # get Marc Demo off the Timesheet Approver group
            self.env.ref('hr_timesheet.group_hr_timesheet_approver').write({'users': [(3, self.user_demo.id)]})
            admin_last_timesheet.with_user(self.user_demo).unlink()

    def test_05_test_access_rule_with_user(self):
        """
            project has privacy_visibility = followers
            test with Marc Demo as USER

            Test with CREATE right.
            Note:
                In this test case, Marc Demo is not added into the allowance list of the project,
                but into the allowance list of the task
        """
        self.assertRecordValues(self.project_r_d, [
            {
                'privacy_visibility': 'followers',
                'allowed_internal_user_ids': [],
            }
        ])
        self.assertFalse(self.r_d_task1.allowed_user_ids)

        with self.assertRaises(AccessError), self.cr.savepoint():
            self.r_d_task1.with_user(self.user_demo).action_start()

        marc_demo_timesheets_before = self._get_test_timesheet(self.r_d_task1, self.user_demo)
        self.assertEqual(len(marc_demo_timesheets_before), 1)

        self.r_d_task1.write({
            'allowed_user_ids': [
                (6, 0, self.user_demo.ids)
            ]
        })

        self.r_d_task1.with_user(self.user_demo).action_start()
        self.r_d_task1.with_user(self.user_demo).action_stop()

        marc_demo_timesheets_after = self._get_test_timesheet(self.r_d_task1, self.user_demo)
        self.assertEqual(len(marc_demo_timesheets_after), 2)
