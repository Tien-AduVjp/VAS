from odoo.tests.common import tagged

from .common import CommonTimesheetApproval


@tagged('-at_install', 'post_install')
class TestHrDepartment(CommonTimesheetApproval):

    def test_01_check_compute_department(self):
    # Department has parent department
        self.assertTrue(self.department_b.timesheet_approval)

    def test_02_check_compute_department(self):
    # Department has no parent department
        self.department_b.write({'parent_id': False})
        self.assertFalse(self.department_b.timesheet_approval)
