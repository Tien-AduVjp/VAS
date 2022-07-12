from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import Common


@tagged('post_install','-at_install', 'access_rights')
class TestAccessRight(Common):

    def test_access_rights_1(self):
        """
        Case 1: User is HR Officer, having full CRUD rights
        """
        demo_role = self.env['hr.role'].with_user(self.user_hr_officer).create({
            'name': 'Demo Role',
            })
        demo_role.with_user(self.user_hr_officer).read()
        demo_role.with_user(self.user_hr_officer).write({
            'name': 'Demo Role edited'
            })
        demo_role.with_user(self.user_hr_officer).unlink()
    
    def test_access_rights_2(self):
        """
        Case 2: User is internal user, only able to read record
        """
        self.role_1.with_user(self.user_employee).read()
        with self.assertRaises(AccessError):
            self.role_1.with_user(self.user_employee).write({
                'name': 'role 1 edited'
                })
        with self.assertRaises(AccessError):
            self.role_test = self.env['hr.role'].with_user(self.user_employee).create({
                'name': 'Test Role',
                })
        with self.assertRaises(AccessError):
            self.role_1.with_user(self.user_employee).unlink()

    def test_access_rights_3(self):
        """
        Case 3: User belongs to group 'hr.group_hr_user' but different company
        Expect: User able to read role in all company that user participant
                or roles which not in any company
        """
        self.role_2 = self.env['hr.role'].create({
            'name' : 'Role 2',
            'company_id': self.company_demo.id
            })
        self.role_2.with_user(self.user_multicomp).read()
        self.role_1.with_user(self.user_multicomp).read()
        # User from company A cannot read role from company B
        # if User not in both Company A and Company B
        with self.assertRaises(AccessError):
            self.role_2.with_user(self.user_hr_officer).read()
