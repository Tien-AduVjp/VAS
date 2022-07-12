from odoo.tests import tagged

from .common import Common

@tagged('post_install', '-at_install')
class TestViinHrRole(Common):
    def test_compute_employees_count(self):
        """
        Case 4: 
            Adding role for 1 person
            Expect: Counting employee in that role: 1 person
        """
        self.user_employee.action_create_employee()
        self.user_employee.employee_id.role_id = self.role_1
        self.assertEqual(self.role_1.employees_count, 1)
