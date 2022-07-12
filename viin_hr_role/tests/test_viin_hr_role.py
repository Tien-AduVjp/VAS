from odoo.tests import tagged

from .common import Common
from odoo.exceptions import ValidationError

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

    def test_constrains_department_1(self):
        """
        Case 1: Both Employee and Role have Department
            1. Adding role and department for 1 employee
            2. Change another department
            Expect: Validation Error "Role does not belong to Department"
        """
        department_demo2 = self.env['hr.department'].create({'name': 'Department demo2'})
        self.role_1.write({'department_id': self.department_1.id})    
        with self.assertRaises(ValidationError):
            self.employee_1.write({'role_id': self.role_1.id,'department_id': department_demo2.id})

    def test_constrains_department_2(self):
        """
        Case 2: Role have Department, Employee don't have
            Adding department for Role
            Expect: Error not raised
        """
        self.role_1.write({'department_id': self.department_1.id})
        self.employee_1.write({'role_id': self.role_1.id})

    def test_constrains_department_3(self):
        """
        Case 3: Employee have Department, Role don't have
            Adding department for Employee
            Expect: Error not raised
        """
        self.employee_1.write({'role_id': self.role_1.id, 'department_id': self.department_1.id})

    def test_constrains_department_4(self):
        """
        Case 4: Neither Employee nor Role don't have Department
            Adding department for Employee and Role
            Expect: Error not raised
        """
        self.employee_1.write({'role_id': self.role_1.id})
