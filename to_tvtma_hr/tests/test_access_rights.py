from odoo.tests import tagged
from odoo.exceptions import AccessError

from .test_tvtma_hr_savepoint import HrTestEmployeeCommon


@tagged('post_install', '-at_install')
class TestHremployee(HrTestEmployeeCommon):
    
    def test_hr_officer(self):
        # Check features allow Hr'Officer update the fields 'Phone', 'mobile, 'email', 'name', ... on partner of others employees.
        partner = self.employee_a.address_home_id
        self.assertTrue(partner.with_user(self.user_hr_user).write({'mobile': '0988888888'}),
                        "Hr'Officer does not update information private address on the partner of other employees.")

    def test_hr_administrator(self):
        # Check features allow Hr'Administrator update the fields 'Phone', 'mobile, 'email', 'name', ... on partner of others employees.
        partner = self.employee_a.address_home_id
        self.assertTrue(partner.with_user(self.user_hr_admin).write({'mobile': '098888999'}),
                        "Hr'Administrator does not update information private address on the partner of other employees.")
    
    def test_user(self):
        # Check features not allow User update the fields 'Phone', 'mobile, 'email', 'name', ... on partner of others employees.
        partner = self.employee_a.address_home_id
        with self.assertRaises(AccessError):
            partner.with_user(self.user).write({'mobile': '098888999'})
        
        # Check access read with user
        with self.assertRaises(AccessError):
            partner.with_user(self.user).read(['mobile', 'email', 'phone'])
