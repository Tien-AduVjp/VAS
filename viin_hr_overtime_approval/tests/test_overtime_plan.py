from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import CommonOverTimeApproval


@tagged('-at_install', 'post_install')
class TestOverTimePlan(CommonOverTimeApproval):
    
    def test_01_check_overtime_plan(self):
        # Unassigned overtime plan with approval request
        self.assertFalse(self.overtime_plan_1.approval_id)
        self.assertFalse(self.overtime_plan_1.state)
    
    def test_02_check_overtime_plan(self):
        # Assigned overtime plan with approval request
        self.overtime_plan_1.write({
            'approval_id': self.overtime_approval_request.id
        })
        self.assertEqual(self.overtime_plan_1.approval_id, self.overtime_approval_request)
        self.assertEqual(self.overtime_plan_1.state, self.overtime_approval_request.state)
        
    def test_03_check_overtime_plan(self):
        # Assigned overtime plan with approval request are not overtime type
        self.overtime_approval_request.write({
            'approval_type_id': self.approve_type_generic.id
        })
        with self.assertRaises(UserError):
            self.overtime_plan_1.write({
                'approval_id': self.overtime_approval_request.id
            })
        
    def test_04_check_overtime_plan(self):
        # change the state when the 'approval_state_exception' field not is ticked
        self.overtime_plan_1.write({
            'approval_id': self.overtime_approval_request.id,
        })
        self.assertFalse(self.overtime_plan_1.approval_state_exception)
        self.assertEqual(self.overtime_plan_1.approval_id, self.overtime_approval_request)
        self.assertEquals(self.overtime_approval_request.state, 'draft')
        self.assertEqual(self.overtime_plan_1.state, 'draft')
        # change approval request to confirmed status
        self.overtime_approval_request.write({'state': 'confirm'})
        # status of overtime plan changed
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        
    def test_05_check_overtime_plan(self):
        # unchange the state when the 'approval_state_exception' field is ticked
        self.overtime_plan_1.write({
            'approval_id': self.overtime_approval_request.id
        })
        self.assertEqual(self.overtime_plan_1.approval_id, self.overtime_approval_request)
        self.assertEquals(self.overtime_approval_request.state, 'draft')
        self.assertEqual(self.overtime_plan_1.state, 'draft')
        # 'approval_state_exception' field is ticked
        self.overtime_plan_1.write({'approval_state_exception': True})
        self.assertTrue(self.overtime_plan_1.approval_state_exception)
        # change approval request to confirmed status
        self.overtime_approval_request.write({'state': 'confirm'})
        # status of overtime plan unchanged
        self.assertEqual(self.overtime_plan_1.state, 'draft')
        
    def test_06_check_overtime_plan(self):
        # Delete overtime plan when not assigned with approval request
        self.overtime_plan_1.unlink()
        
    def test_07_check_overtime_plan(self):
        # Delete overtime plan when assigned with approval request in draft status
        self.overtime_plan_1.write({
            'approval_id': self.overtime_approval_request.id
        })
        self.assertEqual(self.overtime_approval_request.state, 'draft')
        self.overtime_plan_1.unlink()
            
    def test_08_check_overtime_plan(self):
        # Delete overtime plan when assigned with approval request not in draft status
        self.overtime_plan_1.write({
            'approval_id': self.overtime_approval_request.id
        })
        self.overtime_approval_request.write({'state': 'confirm'})
        self.assertEqual(self.overtime_approval_request.state, 'confirm')
        with self.assertRaises(UserError):
            self.overtime_plan_1.unlink()
