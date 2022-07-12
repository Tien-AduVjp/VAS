from odoo.addons.viin_hr_overtime_approval.tests.common import CommonOverTimeApproval
from odoo.tests.common import tagged


@tagged('-at_install', 'post_install')
class TestOvertimeTimesheetApproval(CommonOverTimeApproval):
    
    @classmethod
    def setUpClass(cls):
        super(TestOvertimeTimesheetApproval, cls).setUpClass()
        cls.project = cls.env.ref('project.project_project_2')
        cls.timesheet_1 = cls.env['account.analytic.line'].create({
            'name': 'Timesheet Employee 1',
            'time_start': 20,
            'project_id': cls.project.id,
            'employee_id': cls.employee_1.id,
            'unit_amount': 2,
            'timesheet_state': 'validate'
        })
    
    def test_01_check_overtime_timesheet_approval(self):
        #Plan: Force Recognition Mode is By Plan , Timesheet in validate status
        overtime_plan_test_data = {
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'recognition_mode': 'none',
            'time_start': 20,
            'time_end': 23,
        }
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(0, 0, overtime_plan_test_data)]
        })
        
        timesheets = self.overtime_approval_request.overtime_plan_ids.line_ids.timesheet_ids
        self.assertIn(self.timesheet_1.id, timesheets.ids)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.planned_hours, 3.0)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.matched_timesheet_hours, 2.0)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.actual_hours, 3.0)
        planned_overtime_pay = self.overtime_approval_request.overtime_plan_ids.planned_overtime_pay
        actual_overtime_pay = self.overtime_approval_request.overtime_plan_ids.actual_overtime_pay
        self.assertEqual(planned_overtime_pay, actual_overtime_pay)
    
    def test_02_check_overtime_timesheet_approval(self):
        #Plan: Force Recognition Mode is Timesheet , Timesheet in validate status
        overtime_plan_test_data = {
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'recognition_mode': 'timesheet',
            'time_start': 20,
            'time_end': 23,
        }
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(0, 0, overtime_plan_test_data)]
        })
        
        timesheets = self.overtime_approval_request.overtime_plan_ids.line_ids.timesheet_ids
        self.assertIn(self.timesheet_1.id, timesheets.ids)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.planned_hours, 3.0)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.matched_timesheet_hours, 2.0)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.actual_hours, 2.0)
        planned_overtime_pay = self.overtime_approval_request.overtime_plan_ids.planned_overtime_pay
        actual_overtime_pay = self.overtime_approval_request.overtime_plan_ids.actual_overtime_pay
        self.assertNotEqual(planned_overtime_pay, actual_overtime_pay)
    
    def _check_plan_timesheet_not_in_validate(self, timesheet_state):
        self.timesheet_1.write({'timesheet_state': timesheet_state})
        overtime_plan_test = self.env['hr.overtime.plan'].create({
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'recognition_mode': 'timesheet',
            'time_start': 20,
            'time_end': 23,
        })
        overtime_plan_test.line_ids.invalidate_cache()
        timesheets = overtime_plan_test.line_ids.timesheet_ids
        self.assertFalse(timesheets)
        if timesheet_state in ('draft', 'confirm', 'validate1'):
            self.assertIn(self.timesheet_1.id, overtime_plan_test.approval_await_timesheet_ids.ids)
            self.assertTrue(overtime_plan_test.need_timesheets_approval)
        self.assertEqual(overtime_plan_test.planned_hours, 3.0)
        self.assertEqual(overtime_plan_test.matched_timesheet_hours, 0.0)
        self.assertEqual(overtime_plan_test.actual_hours, 0.0)
    
    def test_03_check_overtime_timesheet_approval(self):
        #Plan: Force Recognition Mode is Timesheet , Timesheet in draft state
        self._check_plan_timesheet_not_in_validate('draft')
    
    def test_04_check_overtime_timesheet_approval(self):
        #Plan: Force Recognition Mode is Timesheet , Timesheet in confirm state
        self._check_plan_timesheet_not_in_validate('confirm')
    
    def test_05_check_overtime_timesheet_approval(self):
        #Plan: Force Recognition Mode is Timesheet , Timesheet in confirm state
        self._check_plan_timesheet_not_in_validate('validate1')
    
    def test_06_check_overtime_timesheet_approval(self):
        #Plan: Force Recognition Mode is Timesheet , Timesheet in confirm state
        self._check_plan_timesheet_not_in_validate('refuse')
    
    def test_07_check_overtime_timesheet_approval(self):
        #Plan: Force Recognition Mode is Timesheet , Timesheet in confirm state
        self._check_plan_timesheet_not_in_validate('cancel')
    
    def test_08_check_overtime_timesheet_approval(self):
        #Plan: Force Recognition Mode is Timesheet , Timesheet in draft state then changed to approved
        self.timesheet_1.write({'timesheet_state': 'draft'})
        overtime_plan_test = self.env['hr.overtime.plan'].create({
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'recognition_mode': 'timesheet',
            'time_start': 20,
            'time_end': 23,
        })
        overtime_plan_test.line_ids.invalidate_cache()
        self.assertFalse(overtime_plan_test.line_ids.timesheet_ids)
        self.assertIn(self.timesheet_1.id, overtime_plan_test.approval_await_timesheet_ids.ids)
        self.assertTrue(overtime_plan_test.need_timesheets_approval)
        self.assertEqual(overtime_plan_test.planned_hours, 3.0)
        self.assertEqual(overtime_plan_test.matched_timesheet_hours, 0.0)
        self.assertEqual(overtime_plan_test.actual_hours, 0.0)
        # Change timesheet status to approved
        self.timesheet_1.write({'timesheet_state': 'validate'})
        self.assertFalse(overtime_plan_test.line_ids.timesheet_ids)
        
        # Match Timesheet
        overtime_plan_test.action_match_timesheet_entries()
        self.assertTrue(overtime_plan_test.line_ids.timesheet_ids)
        self.assertIn(self.timesheet_1.id, overtime_plan_test.line_ids.timesheet_ids.ids)
        self.assertEqual(overtime_plan_test.matched_timesheet_hours, 2.0)
        self.assertEqual(overtime_plan_test.actual_hours, 2.0)
        planned_overtime_pay = overtime_plan_test.planned_overtime_pay
        actual_overtime_pay = overtime_plan_test.actual_overtime_pay
        self.assertNotEqual(planned_overtime_pay, actual_overtime_pay)
