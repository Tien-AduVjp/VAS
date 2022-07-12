from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools.misc import mute_logger
from odoo.exceptions import ValidationError
try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    UniqueViolation = IntegrityError

from .test_employee_grade_common import TestGradeCommon


@tagged('post_install', '-at_install')
class TestGradeFunction(TestGradeCommon):

# Test functional
    # Case 1: Check recursive
    def test_01_recursive_grade(self):
        with self.assertRaises(ValidationError):
            self.expert.update({'parent_id': self.junior.id})

    # Case 2: Check parent grade's department is the same department with current grade
    def test_02_department_grade(self):
        self.senior.update({'parent_id': False, 'department_id': self.admin_dept.id})
        self.junior.update({'department_id': self.admin_dept.id})
        with self.assertRaises(ValidationError):
            self.junior.update({'department_id': self.sales_dept.id})

    # Case 3: Check grade in multi company environment 
    def test_03_multi_company_grade(self):
        (self.intern | self.junior | self.senior).write({'company_id': self.companya.id})
        self.expert.write({'company_id': self.companyb.id})
        grade_ids = (self.intern | self.junior | self.senior).ids
        grades = self.env['hr.employee.grade'].search([('id', 'in', grade_ids), ('company_id', '=', self.companya.id)])
        self.assertEqual(set(grade_ids), set(grades.ids), 'the {} not equal to {}'.format(set(grade_ids), set(grades.ids)))

    # Case 4: Check grade of department 
    def test_04_department_grade(self):
        self.reset_grade()
        (self.junior | self.senior).write({'department_id': self.sales_dept.id})
        self.employeea.update({'department_id': self.sales_dept.id})
        grade_ids = (self.junior | self.senior).ids
        grades = self.env['hr.employee.grade'].search([('department_id', '=', self.sales_dept.id)])
        self.assertEqual(set(grade_ids), set(grades.ids), 'the {} not equal to {}'.format(set(grade_ids), set(grades.ids)))

    # Case 5: Delete parent grade
    def test_05_delete_parent_grade(self):
        self.reset_grade()
        self.junior.update({'parent_id': self.senior.id})
        self.senior.unlink()
        self.assertEqual(self.junior.parent_id.id, False, 'the {} not equal to {}'.format(self.junior.parent_id.id, False))

    # Case 6: Delete grade which an employee has
    def test_06_delete_employee_grade(self):
        self.reset_grade()
        self.employeea.update({'grade_id': self.junior.id})
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.junior.unlink()

    # Case 7: Archive grade which an employee has
    def test_07_archive_employee_grade(self):
        self.reset_grade()
        self.employeea.update({'grade_id': self.junior.id})
        self.junior.active = False
        record_search = self.employeea.grade_id.search([('name', '=', 'junior')])
        # check pass if grade remains on the employee form 
        self.assertEqual(self.employeea.grade_id.id , self.junior.id, 'the {} not equal to {}'.format(self.employeea.grade_id.id, self.junior.id))
        # check pass if grade can not be listed on the employee form
        self.assertEqual(record_search.id , False, 'the {} not equal to {}'.format(record_search.id, False))

    # Case 8: Create 2 grades with the same 'name', 'department' and 'company' will raise an error
    def test_08_the_same_name_grade(self):
        self.reset_grade()
        self.env['hr.employee.grade'].with_context(tracking_disable=True).create({
            'name': 'Junior',
            'department_id': self.sales_dept.id,
            'company_id': self.companya.id
            })
        with self.assertRaises(UniqueViolation), mute_logger('odoo.sql_db'):
            self.env['hr.employee.grade'].with_context(tracking_disable=True).create({
                'name': 'Junior',
                'department_id': self.sales_dept.id,
                'company_id': self.companya.id
                })
