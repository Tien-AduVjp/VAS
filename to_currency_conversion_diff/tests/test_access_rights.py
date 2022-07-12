from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestAccessRights(TestCommon):
    
    def test_access_account_manager(self):
        """ 
        [Security Test] TC01 
        
        - Case: Test access rights of account manager group on supported currency map model
        - Expected Result: account manager group has full permissions on supported currency map model
        """
        self.default_payment_acquirer.supported_currency_map_ids.with_user(self.user_manager).read()

        new_supported_currency = self.env['payment.acquirer.supported.currency.map'].with_user(self.user_manager).create({
            'acquirer_id': self.default_payment_acquirer.id,
            'currency_id': self.currency_vnd.id,
        })

        new_supported_currency.with_user(self.user_manager).write({'currency_id': self.currency_jpy.id})

        new_supported_currency.with_user(self.user_manager).unlink()

    def test_access_account_user(self):
        """ 
        [Security Test] TC02 
        
        - Case: Test read permission of account user group on supported currency map model
        - Expected Result: account user group has read permission on supported currency map model
        """
        self.default_payment_acquirer.supported_currency_map_ids.with_user(self.user_user).read()

        """ 
        [Security Test] TC03 
        
        - Case: Test create/update/delete permissions of account user group on supported currency map model
        - Expected Result: account user group doesn't have create/update/delete permission on supported currency map model
        """
        with self.assertRaises(AccessError):
            self.env['payment.acquirer.supported.currency.map'].with_user(self.user_user).create({
                'acquirer_id': self.default_payment_acquirer.id,
                'currency_id': self.currency_vnd.id,
            })

        with self.assertRaises(AccessError):
            self.default_payment_acquirer.supported_currency_map_ids[0].with_user(self.user_user).write({'currency_id': self.currency_vnd.id})

        with self.assertRaises(AccessError):
            self.default_payment_acquirer.supported_currency_map_ids[0].with_user(self.user_user).unlink()

    def test_access_account_invoice(self):
        """ 
        [Security Test] TC04 
        
        - Case: Test read permission of account invoice group on supported currency map model
        - Expected Result: account invoice group has read permission on supported currency map model
        """
        self.default_payment_acquirer.supported_currency_map_ids.with_user(self.user_invoice).read()

        """ 
        [Security Test] TC05 
        
        - Case: Test create/update/delete permissions of account invoice group on supported currency map model
        - Expected Result: account invoice group doesn't have create/update/delete permission on supported currency map model
        """
        with self.assertRaises(AccessError):
            self.env['payment.acquirer.supported.currency.map'].with_user(self.user_invoice).create({
                'acquirer_id': self.default_payment_acquirer.id,
                'currency_id': self.currency_vnd.id,
            })

        with self.assertRaises(AccessError):
            self.default_payment_acquirer.supported_currency_map_ids[0].with_user(self.user_invoice).write({'currency_id': self.currency_vnd.id})

        with self.assertRaises(AccessError):
            self.default_payment_acquirer.supported_currency_map_ids[0].with_user(self.user_invoice).unlink()
