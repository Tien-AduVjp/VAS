try:
    # try to use ObjectNotInPrerequisiteState if psycopg2's version >= 2.8
    from psycopg2 import errors
    ObjectNotInPrerequisiteState = errors.ObjectNotInPrerequisiteState
except Exception:
    import psycopg2
    ObjectNotInPrerequisiteState = psycopg2.OperationalError

from odoo.tests import tagged
from odoo.exceptions import AccessError
from odoo.tools import mute_logger

from .test_base import TestBase


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestBase):

    def test_access_user_stock_user(self):
        """ 
        [Security Test] TC01, TC02
        
        - Case: Test access rights of stock user group on repair report model
        - Expected Result: stock user group has create/read/update permissions on repair report model but doesn't have delete permission
        * Note: we don't test create permission because data in VIEW of database will be created by its defined query
        """
        reports = self.env['repair.report'].with_user(self.stock_user).search([])
        
        if reports:
            
            reports[0].with_user(self.stock_user).write({'partner_id': reports[0].partner_id})
            
            with self.assertRaises(AccessError):
                reports[0].with_user(self.stock_user).unlink()
        
    def test_access_user_stock_manager(self):
        """
        [Security Test] TC03
        
        - Case: Test access rights of stock manager group on repair report model
        - Expected Result: stock user group has create/read/update/delete permissions on repair report model
        * Note: we don't test create permission because data in VIEW of database will be created by its defined query
        """
        reports = self.env['repair.report'].with_user(self.stock_manager).search([])
        
        if reports:
            
            reports[0].with_user(self.stock_manager).write({'partner_id': reports[0].partner_id})
            
            with mute_logger('odoo.sql_db'):
                with self.assertRaises(ObjectNotInPrerequisiteState):
                    reports[0].with_user(self.stock_manager).unlink()
