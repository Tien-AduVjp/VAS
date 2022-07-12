from odoo.tests import tagged, Form

from .common import HrTestEmployeeCommon


@tagged('post_install', '-at_install')
class TestHremployee(HrTestEmployeeCommon):

    def test_compute_hr_applicants_count(self):
        self.assertEqual(self.employee_a.hr_applicants_count,
                         1, "compute_hr_applicants_count.")
