from odoo.tests.common import tagged

from .common import CommonOverTimeApproval


@tagged('-at_install', 'post_install')
class TestRquestApproval(CommonOverTimeApproval):
    
    @classmethod
    def setUpClass(cls):
        super(TestRquestApproval, cls).setUpClass()
        # Employee create overtime approval request
        overtime_approval_request_employee_1 = cls.env['approval.request'].create({
            'title': 'Overtime Approval Request Employee 1',
            'employee_id': cls.employee_1.id,
            'approval_type_id': cls.approve_type_no_valid.id,
            'overtime_plan_ids': [(6, 0, [cls.overtime_plan_1.id, cls.overtime_plan_2.id])]
        })
        
        # Reassign value
        cls.approve_request_employee = overtime_approval_request_employee_1
       
        # Invalidate cache to avoid cache storage problem
        cls.approve_request_employee.invalidate_cache()
    
    def test_01_request_approval(self):
        #Employee creates approval request with type that doesn't need anyone's approval
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_no_valid.id)
        self.assertEqual(self.approve_request_employee.employee_id.id, self.employee_1.id)
        self.assertEqual(self.approve_request_employee.state, 'draft')
        self.assertEqual(self.overtime_plan_1.state, 'draft')
        self.assertEqual(self.overtime_plan_2.state, 'draft')
        
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        self.assertEqual(self.overtime_plan_1.state, 'validate')
        self.assertEqual(self.overtime_plan_2.state, 'validate')
        
        #Employee: action done request
        self.approve_request_employee.with_user(self.user_employee_1).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
        self.assertEqual(self.overtime_plan_1.state, 'done')
        self.assertEqual(self.overtime_plan_2.state, 'done')
    
    def test_02_request_approval(self):
        # Manager Approve
        #Employee creates approval request with type manager approval
        self.approve_request_employee.write({'approval_type_id': self.approve_type_leader.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_leader.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')
        
        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        #Manager: action approve
        self.approve_request_employee.with_user(self.user_manager).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        self.assertEqual(self.overtime_plan_1.state, 'validate')
        self.assertEqual(self.overtime_plan_2.state, 'validate')
        
    def test_03_request_approval(self):
        # Manager Refuse
        #Employee creates approval request with type manager approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_leader.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_leader.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')
        
        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        #Manager: action refuse 
        self.approve_request_employee.with_user(self.user_manager).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
        self.assertEqual(self.overtime_plan_1.state, 'refuse')
        self.assertEqual(self.overtime_plan_2.state, 'refuse')
        
    def test_04_request_approval(self):
        # Officer Approve
        #Employee creates approval request with type officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_hr.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_hr.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')
        
        #The officer received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_approve_officer.id)
        #Officer: action refuse 
        self.approve_request_employee.with_user(self.user_approve_officer).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        self.assertEqual(self.overtime_plan_1.state, 'validate')
        self.assertEqual(self.overtime_plan_2.state, 'validate')
        
    def test_05_request_approval(self):
        # Officer Refuse
        #Employee creates approval request with type officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_hr.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_hr.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')
        
        #The officer received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_approve_officer.id)
        #Officer: action refuse 
        self.approve_request_employee.with_user(self.user_approve_officer).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
        self.assertEqual(self.overtime_plan_1.state, 'refuse')
        self.assertEqual(self.overtime_plan_2.state, 'refuse')
        
    def test_06_request_approval(self):
        # Manager & Officer Approve
        #Employee creates approval request with type manager & officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_both.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_both.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')

        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        #Manager: action approve 
        self.approve_request_employee.with_user(self.user_manager).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate1')
        self.assertEqual(self.overtime_plan_1.state, 'validate1')
        self.assertEqual(self.overtime_plan_2.state, 'validate1')
        
        #The officer received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_approve_officer.id)
        #Officer: action validate 
        self.approve_request_employee.with_user(self.user_approve_officer).action_validate()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        self.assertEqual(self.overtime_plan_1.state, 'validate')
        self.assertEqual(self.overtime_plan_2.state, 'validate')
        #Officer: action done 
        self.approve_request_employee.with_user(self.user_approve_officer).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
        self.assertEqual(self.overtime_plan_1.state, 'done')
        self.assertEqual(self.overtime_plan_2.state, 'done')
        
    def test_07_request_approval(self):
        # Manager & Officer Approve
        #Employee creates approval request with type manager & officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_both.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_both.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')

        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        #Manager: action refuse 
        self.approve_request_employee.with_user(self.user_manager).action_refuse()
        self.assertEqual(self.approve_request_employee.state, 'refuse')
        self.assertEqual(self.overtime_plan_1.state, 'refuse')
        self.assertEqual(self.overtime_plan_2.state, 'refuse')
    
    def test_08_request_approval(self):
        # Manager & Officer Approve
        #Employee creates approval request with type manager & officer approval 
        self.approve_request_employee.write({'approval_type_id': self.approve_type_both.id})
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_both.id)
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')

        #The manager received the notification
        self.assertEqual(self.approve_request_employee.activity_ids[:1].user_id.id, self.user_manager.id)
        
        #Officer: action approve 
        self.approve_request_employee.with_user(self.user_approve_officer).action_approve()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        self.assertEqual(self.overtime_plan_1.state, 'validate')
        self.assertEqual(self.overtime_plan_2.state, 'validate')
        #Officer: action done 
        self.approve_request_employee.with_user(self.user_approve_officer).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
        self.assertEqual(self.overtime_plan_1.state, 'done')
        self.assertEqual(self.overtime_plan_2.state, 'done')
