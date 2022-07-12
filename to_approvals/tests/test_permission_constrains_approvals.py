from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestPermissionConstrains(Common):
    
    """
        Check constraint with type approval: No Validation
    """
    def test_01_permission_constrains_approve_request_1(self):
        #Officer: action confirm 
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_confirm()
        #Manager: action confirm
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_manager).action_confirm()
        #Employee: action confirm 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        
    def test_01_permission_constrains_approve_request_2(self):
        self.approve_request_employee.write({'state': 'confirm'})
        #Officer: action confirm -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_approve()
        #Manager: action confirm -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_manager).action_approve()
        #Employee: acction approve -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_employee_1).action_approve()
    
    def test_01_permission_constrains_approve_request_3(self):
        self.approve_request_employee.write({'state': 'confirm'})
        #Officer: action_validate -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_validate()
        #Manager: action_validate -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_manager).action_validate()
        #Employee: action_validate -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_employee_1).action_validate()
    
    def test_01_permission_constrains_approve_request_4(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({'state': 'validate'})
        #Officer: action done -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_done()
        #Manager: action done -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_manager).action_done()
        #Employee: action done
        self.approve_request_employee.with_user(self.user_employee_1).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_01_permission_constrains_approve_request_5(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({'state': 'validate'})
        #Officer: action_refuse -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_refuse()
        #Manager: action_refuse -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_manager).action_refuse()
        #Employee: action_refuse -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).action_refuse()
    
    """
        Check constraint with type approval: Manager
    """
    def test_02_permission_constrains_approve_request_1(self):
        self.approve_request_employee.write({'approval_type_id': self.approve_type_leader.id})
        #Officer: action confirm -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_confirm()
        #Manager: action confirm
        self.approve_request_employee.with_user(self.user_manager).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        #Employee: action confirm
        self.approve_request_employee.with_context(approval_action_call=True).write({'state': 'draft'})
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        
    def test_02_permission_constrains_approve_request_2(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_leader.id, 
            'state': 'confirm'
        })
        #Officer: action confirm -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_approve()
        #Employee: acction approve -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_employee_1).action_approve()
        #Manager: action confirm -> error
        self.approve_request_employee.with_user(self.user_manager).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate')
    
    def test_02_permission_constrains_approve_request_3(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_leader.id, 
            'state': 'confirm'
        })
        #Officer: action_validate -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_validate()
        #Manager: action_validate -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_manager).action_validate()
        #Employee: action_validate -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_employee_1).action_validate()
    
    def test_02_permission_constrains_approve_request_4(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_leader.id, 
            'state': 'validate'
        })
        #Officer: action done -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_done()
        #Employee: action done -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).action_done()
        #Manager: action done 
        self.approve_request_employee.with_user(self.user_manager).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_02_permission_constrains_approve_request_5(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_leader.id, 
            'state': 'confirm'
        })
        #Officer: action_refuse -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_refuse()
        #Employee: action_refuse -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).action_refuse()
        #Manager: action_refuse
        self.approve_request_employee.with_user(self.user_manager).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
    
    """
        Check constraint with type approval: HR
    """
    def test_03_permission_constrains_approve_request_1(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({'approval_type_id': self.approve_type_hr.id})
        #Manager: action confirm -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).action_confirm()
        #Officer: action confirm
        self.approve_request_employee.with_user(self.user_approve_officer).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        #Employee: action confirm
        self.approve_request_employee.with_context(approval_action_call=True).write({'state': 'draft'})
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        
    def test_03_permission_constrains_approve_request_2(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_hr.id, 
            'state': 'confirm'
        })
        #Manager: action confirm -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_manager).action_approve()
        #Employee: acction approve -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_employee_1).action_approve()
        #Officer: action confirm
        self.approve_request_employee.with_user(self.user_approve_officer).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate')
    
    def test_03_permission_constrains_approve_request_3(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_hr.id, 
            'state': 'confirm'
        })
        #Officer: action_validate -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_approve_officer).action_validate()
        #Manager: action_validate -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_manager).action_validate()
        #Employee: action_validate -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_employee_1).action_validate()
    
    def test_03_permission_constrains_approve_request_4(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_hr.id, 
            'state': 'validate'
        })
        #Employee: action done -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).action_done()
        #Manager: action done -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).action_done()
        #Officer: action done
        self.approve_request_employee.with_user(self.user_approve_officer).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_03_permission_constrains_approve_request_5(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_hr.id, 
            'state': 'confirm'
        })
        #Employee: action_refuse -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).action_refuse()
        #Manager: action_refuse -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).action_refuse()
        #Officer: action_refuse
        self.approve_request_employee.with_user(self.user_approve_officer).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
    
    """
        Check constraint with type approval: HR & Manager
    """
    def test_04_permission_constrains_approve_request_1(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({'approval_type_id': self.approve_type_both.id})
        #Manager: action confirm -> error
        self.approve_request_employee.with_user(self.user_manager).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        #Officer: action confirm
        self.approve_request_employee.with_context(approval_action_call=True).write({'state': 'draft'})
        self.approve_request_employee.with_user(self.user_approve_officer).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        #Employee: action confirm
        self.approve_request_employee.with_context(approval_action_call=True).write({'state': 'draft'})
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        
    def test_04_permission_constrains_approve_request_2(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id, 
            'state': 'confirm'
        })
        #Employee: acction approve -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_employee_1).action_approve()
        #Manager: action confirm
        self.approve_request_employee.with_user(self.user_manager).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate1')
        #Officer: action confirm
        self.approve_request_employee.with_context(approval_action_call=True).write({'state': 'confirm'})
        self.approve_request_employee.with_user(self.user_approve_officer).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate')
    
    def test_04_permission_constrains_approve_request_3(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id, 
            'state': 'confirm'
        })
        #Employee: action_validate -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_employee_1).action_validate()
        #Manager: action_validate -> error
        with self.assertRaises(UserError): 
            self.approve_request_employee.with_user(self.user_manager).action_validate()
        #Officer: action_validate -> error
        self.approve_request_employee.with_user(self.user_approve_officer).action_validate()
        self.assertEqual(self.approve_request_employee.state, 'validate')
    
    def test_04_permission_constrains_approve_request_4(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id, 
            'state': 'validate'
        })
        #Employee: action done -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).action_done()
        #Manager: action done -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_manager).action_done()
        #Officer: action done
        self.approve_request_employee.with_user(self.user_approve_officer).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_04_permission_constrains_approve_request_5(self):
        self.approve_request_employee.with_context(approval_action_call=True).write({
            'approval_type_id': self.approve_type_both.id, 
            'state': 'confirm'
        })
        #Employee: action_refuse -> error
        with self.assertRaises(UserError):
            self.approve_request_employee.with_user(self.user_employee_1).action_refuse()
        #Manager: action_refuse
        self.approve_request_employee.with_user(self.user_manager).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
        #Officer: action_refuse
        self.approve_request_employee.with_context(approval_action_call=True).write({'state': 'confirm'})
        self.approve_request_employee.with_user(self.user_approve_officer).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
