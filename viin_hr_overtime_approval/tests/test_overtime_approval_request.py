from datetime import date

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import CommonOverTimeApproval


@tagged('-at_install', 'post_install')
class TestOverTimeApprovalRequest(CommonOverTimeApproval):
    
    def test_01_check_overtime_approval_request(self):
        # Request approval of overtime with 2 plans of the same employee
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_2.id])]
        })
        self.assertEqual(len(self.overtime_approval_request.overtime_plan_ids), 2)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.employee_id, self.employee_1)
    
    def test_02_check_overtime_approval_request(self):
        # Request approval for overtime with 2 different employee plans
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_3.id])]
        })
        self.assertEqual(len(self.overtime_approval_request.overtime_plan_ids), 2)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.employee_id, self.employee_1 | self.employee_2)
    
    def test_03_check_overtime_approval_request(self):
        # Delete Overtime Approval Request
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id])]
        })
        self.assertEqual(self.overtime_approval_request.state, 'draft')
        self.overtime_approval_request.unlink()
        
    def test_04_check_overtime_approval_request(self):
        # Confirm the request for approval of overtime with 2 plans of the same employee who are not at the same time
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_2.id])]
        })
        self.overtime_approval_request.action_confirm()
        self.assertEqual(self.overtime_approval_request.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')
    
    def test_05_check_overtime_approval_request(self):
        # confirm the request for overtime approval with 2 plans of the same employee at the same time
        overtime_plan_test_data = {
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'time_start': 17,
            'time_end': 18,
        }
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(0, 0, overtime_plan_test_data), (0, 0, overtime_plan_test_data)]
        })
        with self.assertRaises(UserError):
            self.overtime_approval_request.overtime_plan_ids.action_confirm()
    
    def test_06_check_overtime_approval_request(self):
        # confirm overtime approval request with different employee's plan at the same time
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_3.id])]
        })
        self.overtime_approval_request.action_confirm()
        self.assertEqual(self.overtime_approval_request.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_3.state, 'confirm')
    
    def test_07_check_overtime_approval_request(self):
        # Approve overtime request with a denied plan
        self.approve_type_overtime.write({'validation_type': 'leader'})
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_2.id])],
            'state': 'confirm'
        })
        self.assertEqual(self.overtime_approval_request.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')
        
        # refuse the plan to overtime 1
        self.overtime_plan_1.action_refuse()
        # Approve overtime request
        self.overtime_approval_request.action_approve()
        self.assertEqual(self.overtime_approval_request.state, 'validate')
        self.assertEqual(self.overtime_plan_1.state, 'refuse')
        self.assertTrue(self.overtime_plan_1.approval_state_exception)
        self.assertEqual(self.overtime_plan_2.state, 'validate')
        self.assertFalse(self.overtime_plan_2.approval_state_exception)
        
    def test_08_check_overtime_approval_request(self):
        # Plan duplication check is in the draft status overtime approval requirement
        overtime_plan_test_data = {
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'time_start': 20,
            'time_end': 21,
        }
        overtime_approval_request = self.env['approval.request'].create({
            'title': 'Overtime Approval Request',
            'employee_id': self.env.ref('base.user_admin').employee_id.id,
            'approval_type_id': self.approve_type_overtime.id,
            'overtime_plan_ids': [(0, 0, overtime_plan_test_data), (0, 0, overtime_plan_test_data)]
        })
        self.assertEquals(set(overtime_approval_request.overtime_plan_ids.mapped('time_start')), {20})
        self.assertEquals(set(overtime_approval_request.overtime_plan_ids.mapped('time_end')), {21}) 
    
    def test_09_check_overtime_approval_request(self):
        # check for plan duplication is in 2 different overtime approval requirements
        overtime_plan_test_data = {
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'time_start': 20,
            'time_end': 21,
        }
        overtime_approval_request_1 = self.env['approval.request'].create({
            'title': 'Overtime Approval Request 1',
            'employee_id': self.env.ref('base.user_admin').employee_id.id,
            'approval_type_id': self.approve_type_overtime.id,
            'overtime_plan_ids': [(0, 0, overtime_plan_test_data)]
        })
        overtime_approval_request_2 = self.env['approval.request'].create({
            'title': 'Overtime Approval Request 1',
            'employee_id': self.env.ref('base.user_admin').employee_id.id,
            'approval_type_id': self.approve_type_overtime.id,
            'overtime_plan_ids': [(0, 0, overtime_plan_test_data)]
        })
        # Confirm overtime plan 1
        overtime_approval_request_1.overtime_plan_ids.action_confirm()
        # Confirm overtime plan 2
        with self.assertRaises(UserError):
            overtime_approval_request_2.overtime_plan_ids.action_confirm()
    
    def test_10_check_overtime_approval_request(self):
        # Check the overtime plan is in the approval request in draft status and the overtime plan is not in the approval request
        overtime_plan_1 = self.env['hr.overtime.plan'].create({
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'time_start': 20,
            'time_end': 21,
            'approval_id': self.overtime_approval_request.id
        })
        overtime_plan_2 = self.env['hr.overtime.plan'].create({
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'time_start': 20,
            'time_end': 21,
        })
    
    def test_11_check_overtime_approval_request(self):
        # Check the overtime plan is in the approval request not in draft status and the overtime plan is not in the approval request
        self.overtime_approval_request.write({'state': 'confirm'})
        overtime_plan_1 = self.env['hr.overtime.plan'].create({
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'time_start': 20,
            'time_end': 21,
            'approval_id': self.overtime_approval_request.id,
        })
        with self.assertRaises(UserError):
            overtime_plan_2 = self.env['hr.overtime.plan'].create({
                'employee_id': self.employee_1.id,
                'reason_id': self.reason_general.id,
                'time_start': 20,
                'time_end': 21,
            })
    
    def test_12_check_overtime_approval_request(self):
        # Recalculate overtime plan
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_2.id])]
        })
        planned_overtime_pay = sum(self.overtime_approval_request.overtime_plan_ids.mapped('planned_overtime_pay'))
        actual_overtime_pay = sum(self.overtime_approval_request.overtime_plan_ids.mapped('actual_overtime_pay'))
        self.assertEqual(sum(self.overtime_approval_request.overtime_plan_ids.contract_ids.mapped('wage')), self.contract_1.wage)
        # Change base salary on employee contract
        self.contract_1.write({'wage': 20000000})
        self.assertEqual(sum(self.overtime_approval_request.overtime_plan_ids.contract_ids.mapped('wage')), 20000000)
        # Recalculate the plan
        self.overtime_approval_request.action_recompute_overtime_plans()
        self.assertNotEqual(sum(self.overtime_approval_request.overtime_plan_ids.mapped('planned_overtime_pay')), planned_overtime_pay)
        self.assertNotEqual(sum(self.overtime_approval_request.overtime_plan_ids.mapped('actual_overtime_pay')), actual_overtime_pay)
        
    def test_13_check_overtime_approval_request(self):
        # Mass registration with overtime approval request, mark request for approval
        user_admin = self.env.ref('base.user_admin')
        context = {'default_approval_required': True, 'default_approval_id': self.overtime_approval_request.id}
        line_data = {
            'date': date.today(),
            'time_start': 20,
            'time_end': 21
        }
        mass_registration = self.env['hr.overtime.request.mass'].with_context(context).with_user(user_admin).create({
            'mode': 'department',
            'reason_id': self.reason_general.id,
            'line_ids': [(0, 0, line_data)]
        })
        
        mass_registration.action_schedule()
        plan_of_approval = self.env['hr.overtime.plan'].search([('approval_id','=', self.overtime_approval_request.id)])
        self.assertTrue(plan_of_approval)
    
    def test_14_check_overtime_approval_request(self):
        # Mass registration with overtime approval request, do not mark approval request
        user_admin = self.env.ref('base.user_admin')
        context = {'default_approval_required': False, 'default_approval_id': self.overtime_approval_request.id}
        line_data = {
            'date': date.today(),
            'time_start': 20,
            'time_end': 21
        }
        mass_registration = self.env['hr.overtime.request.mass'].with_context(context).with_user(user_admin).create({
            'mode': 'department',
            'reason_id': self.reason_general.id,
            'line_ids': [(0, 0, line_data)]
        })
        
        mass_registration.action_schedule()
        plan_of_approval = self.env['hr.overtime.plan'].search([('approval_id','=', self.overtime_approval_request.id)])
        self.assertFalse(plan_of_approval)
    
    def test_15_check_overtime_approval_request(self):
        # Mass overtime plan cancellation, plan in overtime approval request
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_2.id])]
        })
        self.assertEqual(self.overtime_plan_1.approval_id, self.overtime_approval_request)
        self.assertEqual(self.overtime_plan_2.approval_id, self.overtime_approval_request)
        self.assertEqual(self.overtime_plan_1.state, 'draft')
        self.assertEqual(self.overtime_plan_2.state, 'draft')
        
        # Cancel plan
        (self.overtime_plan_1 | self.overtime_plan_2).action_cancel()
        self.assertEqual(self.overtime_plan_1.state, 'cancel')
        self.assertEqual(self.overtime_plan_2.state, 'cancel')
    
    def test_16_check_overtime_approval_request(self):
        # Mass overtime plan cancellation, plan not in overtime approval request
        self.assertFalse(self.overtime_plan_1.approval_id)
        self.assertFalse(self.overtime_plan_2.approval_id)
        
        # Cancel plan
        with self.assertRaises(UserError):
            (self.overtime_plan_1 | self.overtime_plan_2).action_cancel()
