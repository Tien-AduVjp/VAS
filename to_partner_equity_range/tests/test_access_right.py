from odoo.exceptions import AccessError
from odoo.tests.common import tagged


from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):

    #Case 1
    def test_partner_manager_access_right(self):
        """
        INPUT: User manager
        OUTPUT: Can read, create, write, unlink information of equity range
        """
        equity_range_test = self.env['res.partner.equity.range'].with_user(self.user_partner_manager).create({
            'name': 'from_10_50M_USD'
        })
        equity_range_test.with_user(self.user_partner_manager).read()
        equity_range_test.with_user(self.user_partner_manager).write({
            'description': 'from 10 to 50M USD'
        })
        equity_range_test.with_user(self.user_partner_manager).unlink()

    #Case 2
    def test_internal_user_access_right(self):
        """
        INPUT: User internal, can not create a new contact
        OUTPUT: Can read information of equity range
                Can not create, write, unlink information of equity range
        """
        self.equity_range_5_10M_USD.with_user(self.user_internal).read()
        with self.assertRaises(AccessError):
            self.env['res.partner.equity.range'].with_user(self.user_internal).create({
                'name': 'From 10 to 50M USD'
            })
        with self.assertRaises(AccessError):
            self.equity_range_5_10M_USD.with_user(self.user_internal).write({
                'description': 'From 5 to 10M USD'
            })
        with self.assertRaises(AccessError):
            self.equity_range_5_10M_USD.with_user(self.user_internal).unlink()
