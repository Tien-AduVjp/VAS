from odoo.tests.common import tagged
from odoo.exceptions import AccessError
from .common import Common


@tagged('post_install', '-at_install')
class TestToProjectAccess(Common):

    def test_01_user_employee_view_timesheet(self):
        """
        Input:
            Project:
                Project manager: user_employee,
                project_user_full_access_rights: True
        Output: user_employee can view all timesheets of the project
        """
        timesheets = self.project_1.timesheet_ids
        self.assertTrue(timesheets)
        timesheets.with_user(self.user_employee).check_access_rule('read')

    def test_02_user_employee_view_timesheet(self):
        """
        Input:
            Project:
                Project manager: user_employee,
                project_user_full_access_rights: False
        Output: user_employee can't view all other people's timesheets
        """
        self.project_1.project_user_full_access_rights = False

        with self.assertRaises(AccessError):
            self.project_1.timesheet_ids.with_user(self.user_employee).check_access_rule('read')

    def test_03_user_employee_view_timesheet(self):
        """
        Input:
            Project:
                Project manager: user_projectmanager,
                project_user_full_access_rights: True
        Output: user_employee can't view all other people's timesheets
        """
        self.project_1.user_id = self.user_projectmanager.id

        with self.assertRaises(AccessError):
            self.project_1.timesheet_ids.with_user(self.user_employee).check_access_rule('read')
