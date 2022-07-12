from odoo.tests.common import tagged

from .common import CommonTimesheetApproval


@tagged('-at_install', 'post_install')
class TestTimesheetApprovals(CommonTimesheetApproval):
    
    @classmethod
    def setUpClass(cls):
        super(TestTimesheetApprovals, cls).setUpClass()
        # Employee create timesheet approve request
        timesheet_approve_request_employee_1 = cls.env['approval.request'].create({
            'title': 'Timesheet Approval Request Employee 1',
            'employee_id': cls.employee_1.id,
            'approval_type_id': cls.approve_type_no_valid.id,
        })
        
        # Reassign value
        cls.approve_request_employee = timesheet_approve_request_employee_1
        
        # Invalidate cache to avoid cache storage problem
        cls.approve_request_employee.invalidate_cache()
        
    def test_01_employee_approve_request(self):
        #Employee creates approval request with type that doesn't need anyone's approval
        self.assertEqual(self.approve_request_employee.approval_type_id.id, self.approve_type_no_valid.id)
        self.assertEqual(self.approve_request_employee.employee_id.id, self.employee_1.id)
        self.assertEqual(self.approve_request_employee.state, 'draft')
        
        #Employee: action confirm request 
        self.approve_request_employee.with_user(self.user_employee_1).action_confirm()
        self.assertEqual(self.approve_request_employee.state, 'validate')
        timesheets_state = self.approve_request_employee.timesheet_line_ids.mapped('timesheet_state')
        self.assertEqual(set(timesheets_state), {'validate'})
        
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
        timesheets_state = self.approve_request_employee.timesheet_line_ids.mapped('timesheet_state')
        self.assertEqual(set(timesheets_state), {'validate'})
        
        
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
        timesheets_state = self.approve_request_employee.timesheet_line_ids.mapped('timesheet_state')
        self.assertEqual(set(timesheets_state), {'refuse'})
        
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
        timesheets_state = self.approve_request_employee.timesheet_line_ids.mapped('timesheet_state')
        self.assertEqual(set(timesheets_state), {'validate'})
        
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
        timesheets_state = self.approve_request_employee.timesheet_line_ids.mapped('timesheet_state')
        self.assertEqual(set(timesheets_state), {'refuse'})
        
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
        timesheets_state = self.approve_request_employee.timesheet_line_ids.mapped('timesheet_state')
        self.assertEqual(set(timesheets_state), {'validate'})
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
        timesheets_state = self.approve_request_employee.timesheet_line_ids.mapped('timesheet_state')
        self.assertEqual(set(timesheets_state), {'refuse'})
    
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
        timesheets_state = self.approve_request_employee.timesheet_line_ids.mapped('timesheet_state')
        self.assertEqual(set(timesheets_state), {'validate'})
        #Officer: action done 
        self.approve_request_employee.with_user(self.user_approve_officer).action_done()
        self.assertEqual(self.approve_request_employee.state, 'done')
