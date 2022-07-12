from odoo.tests import tagged
from odoo.exceptions import AccessError

from .test_to_hr_training_access_right_common import TestAccessRightCommon


@tagged('post_install','-at_install')
class TestAcessRightFunction(TestAccessRightCommon):
# Test access rights
    # Case 1: Check internal user access rights
    def test_01_internal_user_right(self): 
        garden_course = self.env['hr.require.training'].create({
                                    'slide_channel_id': self.garden_basic.id,
                                    'require_hour': 5
                                    })
        # Internal user can see the training course
        garden_course.with_user(self.internal_user).read([])
        # Internal user can not update training course
        self.assertRaises(AccessError, garden_course.with_user(self.internal_user).write, 
                          {'slide_channel_id': self.tree_basic.id}
                          )
        # Internal user can not delete the training course
        self.assertRaises(AccessError, garden_course.with_user(self.internal_user).unlink)
        # Internal user can not create the training course
        self.assertRaises(AccessError,
                          self.env['hr.require.training'].with_user(self.internal_user).create,
                          self.vals
                          )
    # Case 2: Check hr officer user access rights
    def test_02_hr_user_right(self): 
        garden_course = self.env['hr.require.training'].create({
                                    'slide_channel_id': self.garden_basic.id,
                                    'require_hour': 5
                                    })
        # hr officer user can see the training course
        garden_course.with_user(self.hr_user).read([])
        # hr officer can update training course
        garden_course.with_user(self.hr_user).update( 
                          {'slide_channel_id': self.tree_basic.id}
                          )
       # hr officer user can delete the training course
        garden_course.with_user(self.hr_user).unlink()
        # hr officer user can create the training course 
        self.env['hr.require.training'].with_user(self.hr_user).create(self.vals)
        

