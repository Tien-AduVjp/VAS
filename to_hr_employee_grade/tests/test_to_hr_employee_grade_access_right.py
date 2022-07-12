from odoo.tests import tagged
from odoo.exceptions import AccessError

from .test_to_hr_employee_grade_access_right_common import TestAccessRightCommon


@tagged('post_install', '-at_install')
class TestAcessRightFunction(TestAccessRightCommon):

# Test access rights
    # Case 1: Check internal user access rights
    def test_01_internal_user_right(self):
        # Internal user can see the Grade
        try:
            self.intern.with_user(self.internal_user).read()
        except AccessError:
            self.fail("Internal users should be able to read grades.")

        # Internal user can not update the Grade
        with self.assertRaises(AccessError):
            self.intern.with_user(self.internal_user).write({'name': 'beginner grade'})
        # Internal user can not delete the Grade
        with self.assertRaises(AccessError):
            self.intern.with_user(self.internal_user).unlink()
        # Internal user can not create the Grade
        with self.assertRaises(AccessError):
            self.env['hr.employee.grade'].with_user(self.internal_user).with_context(tracking_disable=True).create({
                'name': 'super grade'
            })

    # Case 2: Check hr officer user access rights
    def test_02_hr_user_right(self):
        beginner_grade = self.env['hr.employee.grade'].with_context(tracking_disable=True).with_context(tracking_disable=True).create({
            'name': 'beginner grade',
            'parent_id': self.intern.id
            })
        # hr officer user can see the Grade
        beginner_grade.with_user(self.hr_user).read([])
        # hr officer can update the Grade
        beginner_grade.with_user(self.hr_user).update({'name': 'beginner'})
        # hr officer user can delete the Grade
        beginner_grade.with_user(self.hr_user).unlink()
        # hr officer user can create grades
        self.env['hr.employee.grade'].with_user(self.hr_user).with_context(tracking_disable=True).create({
            'name': 'super grade'
        })

