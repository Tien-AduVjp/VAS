from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import Common

@tagged('post_install','-at_install', 'access_rights')
class TestAccessRight(Common):
    def test_access_right_1(self):
        """
        Course is 'published' and visibility is 'public'.
        Expected: User can access through that course
        """
        self.course_1.write({
            'is_published' : True,
            'visibility':  'public'
            })
        self.course_1.with_user(self.employee).read([])

    def test_access_right_2(self):
        """
        Course is 'published' and visibility is 'members'.
        Expected: Users only access this course if they are course's attendees
        """
        # self.employee is not in attendees
        self.course_1.write({
            'is_published' : True,
            'visibility':  'members',
            })
        with self.assertRaises(AccessError):
            self.course_1.with_user(self.employee).read([])

        # self.employee is in attendees
        self.course_1.write({
            'partner_ids' : [(4,self.employee.partner_id.id,0)]
            })
        self.course_1.with_user(self.employee).read([])

    def test_access_right_3(self):
        """
        Course is 'unpublished'
        Expected: Whether 'visibility' is 'public' or'member,'
        user cannot access through that course.
        """
        # 'visibility' is 'public'
        self.course_1.write({
            'is_published' : False,
            'visibility':  'public'
            })
        with self.assertRaises(AccessError):
            self.course_1.with_user(self.employee).read([])
        # 'visibility' is 'members'
        self.course_1.write({
            'is_published' : False,
            'visibility':  'members',
            'partner_ids' : [(4,self.employee.partner_id.id,0)]
            })
        with self.assertRaises(AccessError):
            self.course_1.with_user(self.employee).read([])
