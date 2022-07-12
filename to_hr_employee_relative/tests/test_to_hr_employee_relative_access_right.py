from odoo.tests import tagged
from odoo.exceptions import AccessError

from .test_to_hr_employee_relative_access_right_common import TestAccessRightCommon


@tagged('post_install','-at_install')
class TestAcessRightFunction(TestAccessRightCommon):
# Test access rights
    # Case 1: Check internal user access rights
    def test_01_internal_user_right(self): 
        # Internal user can read the Relative
        self.relative_father_a.with_user(self.internal_user).read([])
        # Internal user can not update the Relative
        self.assertRaises(AccessError, self.relative_father_a.with_user(self.internal_user).write, 
                          {'employee_id': self.employee_b.id}
                          )
        # Internal user can not delete the Relative
        self.assertRaises(AccessError, self.relative_father_a.with_user(self.internal_user).unlink)
        # Internal user can not create the Relative
        self.assertRaises(AccessError,
                          self.env['hr.employee.relative'].with_user(self.internal_user).create,
                          self.vals
                          )
    # Case 2: Check hr officer user access rights
    def test_02_hr_user_right(self):       
        # hr officer user can see the Relative
        self.relative_mother_a.with_user(self.hr_user).read([])
        # hr officer can update the Relative
        self.relative_mother_a.with_user(self.hr_user).update( 
                           {'employee_id': self.employee_b.id}
                           )
        # hr officer user can delete the Relative
        self.relative_mother_a.with_user(self.hr_user).unlink()
        # hr officer user can create the Relative 
        self.env['hr.employee.relative'].with_user(self.hr_user).create(self.vals)
           

