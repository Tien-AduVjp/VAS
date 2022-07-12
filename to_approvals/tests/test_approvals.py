from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import Form, tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestApprovals(Common):
    
    def test_01_onchange_approve_request(self):
        #Users have employees
        approve_request_form = Form(self.env['approval.request'].with_user(self.user_employee_1))
        self.assertEqual(approve_request_form.employee_id.id, self.employee_1.id)
        self.assertEqual(fields.Date.to_date(approve_request_form.date), fields.Date.today())
        
    def test_02_onchange_approve_request(self):
        #Users have no employees
        self.employee_1.write({'user_id': False})
        approve_request_form = Form(self.env['approval.request'].with_user(self.user_employee_1))
        self.assertFalse(approve_request_form.employee_id)
        self.assertEqual(fields.Date.to_date(approve_request_form.date), fields.Date.today())
        
    def test_01_employee_approve_request(self):
        #Employee creates approval request with type that doesn't need anyone's approval
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_no_valid.id)
        self.assertEqual(self.approve_request_employee.employee_id.id, self.employee_1.id)
        self.assertEqual(self.approve_request_employee.date, fields.Date.today())
        self.assertEqual(self.approve_request_employee.state, 'draft')
        
        #Employee: action confirm request
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        
        #Employee: action done request
        self.approve_request_employee.with_user(self.user_employee_1).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_02_employee_approve_request(self):
        # Manager Approve
        #Employee creates approval request with type manager approval
        self.approve_request_employee.write({'approval_type_id': self.approve_type_leader.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_leader.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        #Manager: action approve
        self.approve_request_employee.with_user(self.user_manager).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        
    def test_03_employee_approve_request(self):
        # Manager Refuse
        #Employee creates approval request with type manager approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_leader.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_leader.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        #Manager: action refuse 
        self.approve_request_employee.with_user(self.user_manager).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
        
    def test_04_employee_approve_request(self):
        # Officer Approve
        #Employee creates approval request with type officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_hr.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_hr.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        #The officer received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_approve_officer.id)
        #Officer: action refuse 
        self.approve_request_employee.with_user(self.user_approve_officer).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        
    def test_05_employee_approve_request(self):
        # Officer Refuse
        #Employee creates approval request with type officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_hr.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_hr.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        #The officer received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_approve_officer.id)
        #Officer: action refuse 
        self.approve_request_employee.with_user(self.user_approve_officer).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
        
    def test_06_employee_approve_request(self):
        # Manager & Officer Approve
        #Employee creates approval request with type manager & officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_both.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_both.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')

        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        #Manager: action approve 
        self.approve_request_employee.with_user(self.user_manager).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate1')
        
        #The officer received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_approve_officer.id)
        #Officer: action validate 
        self.approve_request_employee.with_user(self.user_approve_officer).action_validate()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        #Officer: action done 
        self.approve_request_employee.with_user(self.user_approve_officer).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
        
    def test_07_employee_approve_request(self):
        # Manager & Officer Approve
        #Employee creates approval request with type manager & officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_both.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_both.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')

        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        #Manager: action refuse 
        self.approve_request_employee.with_user(self.user_manager).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
    
    def test_08_employee_approve_request(self):
        # Manager & Officer Approve
        #Employee creates approval request with type manager & officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_both.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_both.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')

        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        
        #Officer: action approve 
        self.approve_request_employee.with_user(self.user_approve_officer).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        #Officer: action done 
        self.approve_request_employee.with_user(self.user_approve_officer).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
    
    def test_09_delete_approve_request(self):
        # Delete approve request in draft status
        self.approve_request_employee.unlink()

    def test_10_delete_approve_request(self):
        # Delete approve request not in draft status
        self.approve_request_employee.write({'state': 'confirm'})
        with self.assertRaises(UserError):
            self.approve_request_employee.unlink()
