from odoo.exceptions import AccessError
from odoo.tests.common import tagged

from .common import Common

@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):

    #Case 1
    def test_partner_manager_access_right(self):
        """
        INPUT: User manager
        OUTPUT: Can read, create, write, unlink information of ownership type
        """
        ownership_type_test = self.env['res.partner.ownership.type'].with_user(self.user_partner_manager).create({
            'name': 'Limited Company'
        })
        ownership_type_test.with_user(self.user_partner_manager).read()
        ownership_type_test.with_user(self.user_partner_manager).write({
            'description': 'Limited Company'
        })
        ownership_type_test.with_user(self.user_partner_manager).unlink()

    #Case 2
    def test_internal_user_access_right(self):
        """
        INPUT: User internal, can not create a new contact
        OUTPUT: Can read information of ownership type
                Can not create, write, unlink information of ownership type
        """
        self.ownership_type_joint_stock_company.with_user(self.user_internal).read()
        with self.assertRaises(AccessError):
            ownership_type_test = self.env['res.partner.ownership.type'].with_user(self.user_internal).create({
                'name': 'Limited Company'
            })
        with self.assertRaises(AccessError):
            self.ownership_type_joint_stock_company.with_user(self.user_internal).write({'description': 'Limited Company'})
        with self.assertRaises(AccessError):
            self.ownership_type_joint_stock_company.with_user(self.user_internal).unlink()
