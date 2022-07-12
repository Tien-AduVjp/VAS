from datetime import date, datetime, timedelta
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import Form, tagged
from odoo import fields

from . import common
from odoo.addons.viin_hr_overtime.models.res_company import OVERTIME_RECOGNITION_MODE


@tagged('post_install', '-at_install')
class TestHrOvertimePlan(common.Common):
        
    #-------------------------------------------------------------Test Form-------------------------------------------------------------#
    
    def test_01_contract_form(self):
        """
            Case: Only can input Overtime Base Amount if Over Time Base Mode is Manual.
        """
        contract = Form(self.env['hr.contract'])       
        contract.overtime_base_mode = 'manual'
        self.assertFalse(contract._get_modifier('overtime_base_amount', 'readonly'))
        contract.overtime_base_mode = 'wage'
        self.assertTrue(contract._get_modifier('overtime_base_amount', 'readonly'))
    
    def test_02_compute_contract_ids(self):
        """
            Case 1 : Test compute contract in case period of overtime plan is in period of contract.
            Expect: 
                - contract of employee is draft/cancel: overtime plan don't display contract.
                - contract of employee is new/closed: overtime plan display contract.
            Case 2: Test compute contract (new/closed) in case period of overtime plan is NOT in period of contract.
            Expect: overtime plan don't display contract.
        """  
        # Case 1:
        self.assertEqual(self.overtime_plan_emp_01.contract_ids, self.contracts_emp_01)
        self.contracts_emp_01.set_as_close()
        self.assertEqual(self.overtime_plan_emp_01.contract_ids, self.contracts_emp_01)
        self.contracts_emp_01.action_cancel()
        self.assertFalse(self.overtime_plan_emp_01.contract_ids)   
        self.contracts_emp_01.action_set_to_draft()    
        self.assertFalse(self.overtime_plan_emp_01.contract_ids)   
        # Case 2:
        self.contracts_emp_01.date_end = date.today() + timedelta(days=365)     
        self.contracts_emp_01.date_start = date.today() + timedelta(days=1)
        self.contracts_emp_01.action_start_contract()
        self.assertFalse(self.overtime_plan_emp_01.contract_ids)
        
    def test_03_compute_mismatch_overtime_plan(self):
        """
            Case: Test compute mismatch overtime plan in contract when overtime plan change to an other employee.
        """
        self.overtime_plan_emp_01.date = self.next_monday
        contract_02 = self.contracts_emp_01.copy()
        contract_02.employee_id = self.user_02.employee_id
        contract_02.action_start_contract()
        self.overtime_plan_emp_01.time_end = 16.0 
        self.overtime_plan_emp_01.time_start = 14.0
        self.assertFalse(self.overtime_plan_emp_01.line_ids)
        self.assertEqual(self.contracts_emp_01.mismatched_overtime_plan_ids, self.overtime_plan_emp_01)
        self.overtime_plan_emp_01.employee_id = self.user_02.employee_id       
        self.assertFalse(self.contracts_emp_01.mismatched_overtime_plan_ids)
        self.assertEqual(self.user_02.employee_id.contract_id.mismatched_overtime_plan_ids, self.overtime_plan_emp_01)

    #-----------------------------------------------------------Test Functional-----------------------------------------------------------#
    
    def test_01_compute_line_ids(self):
        """
            Case: Test OT interval in 1 overtime rule.
    
            *Overtime plan                                             
                Date Plan: NextMonday (from day testing)              
                Time Start      : 18.0                                      
                Time End        : 20.0                                      
    
            * Monday overtime rule:                                          
                +--------+----------------------+-----------+---------+             
                |Code    |         Name         | Hour From | Hour To |             
                +--------+----------------------+-----------+---------+             
                | OT0006 | Monday Early Morning |       0.0 |     6.0 |
                | OT0618 | Monday Daytime       |       6.0 |    18.0 |
                | OT1822 | Monday Evening       |      18.0 |    22.0 |
                | OT1822 | Monday Night         |      22.0 |    24.0 |   
                +--------+----------------------+-----------+---------+
    
            * Working time in monday (Standard 40 hours/week)
                +----+----------------------+-----------+---------+
                | ID |         Name         | Hour From | Hour To |
                +----+----------------------+-----------+---------+
                | 1  | Monday  Morning      |       8.0 |    12.0 |
                | 2  | Monday Afternoon     |       13.0|    17.0 |
                +----+----------------------+-----------+---------+
    
            * Lines Overtime was generated:
                +-----------+---------+--------------+----------------------+-----------+
                | Hour from | Hour To | Planned Hour | Rule name            | Rule Code |
                +-----------+---------+--------------+----------------------+-----------+  
                | 18.0      | 20.0    | 2.0          | Monday Evening       | OT1822    |
                +-----------+---------+--------------+----------------------+-----------+           
        """       
        next_monday = self._generate_overtime_plan_date(0) 
        self.overtime_plan_emp_01.date = next_monday
        self.overtime_plan_emp_01.time_end = 20.0    
        self.overtime_plan_emp_01.time_start = 18.0  
        line_ids = self.overtime_plan_emp_01.line_ids
        self.assertEqual(len(line_ids) , 1)
        self.assertTrue(line_ids[0].planned_hours == 2.0\
            and line_ids[0].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_ot1822').name)
    
    def test_02_compute_line_ids(self):
        """
            Case: Test OT interval in multiple overtime rule
    
            *Overtime plan                                             
                Date Plan: NextMonday (from day testing)              
                Time      : 0.0                                      
                time_end  : 24.0                                      
    
            * Lines Overtime was generated:
                +-----------+---------+--------------+----------------------+-----------+
                | Hour from | Hour To | Planned Hour | Rule name            | Rule Code |
                +-----------+---------+--------------+----------------------+-----------+
                | 0.0       | 6.0     | 6.0          | Monday Early Morning | OT0006    |
                +-----------+---------+--------------+----------------------+-----------+
                | 6.0       | 8.0     | 2.0          | Monday Daytime       | OT0618    |
                +-----------+---------+--------------+----------------------+-----------+
                | 12.0      | 13.0    | 1.0          | Monday Daytime       | OT0618    |
                +-----------+---------+--------------+----------------------+-----------+
                | 17.0      | 18.0    | 1.0          | Monday Daytime       | OT0618    |
                +-----------+---------+--------------+----------------------+-----------+
                | 18.0      | 22.0    | 4.0          | Monday Evening       | OT1822    |
                +-----------+---------+--------------+----------------------+-----------+  
                | 22.0      | 24.0    | 2.0          | Monday Night         | OT2224    |
                +-----------+---------+--------------+----------------------+-----------+           
        """       
    
        self.overtime_plan_emp_01.date = self.next_monday
        self.overtime_plan_emp_01.time_end = 24.0    
        self.overtime_plan_emp_01.time_start = 0.0  
        line_ids = self.overtime_plan_emp_01.line_ids
        self.assertEqual(len(line_ids) , 6)
        self.assertTrue(line_ids[0].planned_hours == 6.0\
            and line_ids[0].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_ot0006').name)
        self.assertTrue(line_ids[1].planned_hours == 2.0\
            and line_ids[1].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_ot0618').name)
        self.assertTrue(line_ids[2].planned_hours == 1.0\
            and line_ids[2].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_ot0618').name)
        self.assertTrue(line_ids[3].planned_hours == 1.0\
            and line_ids[3].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_ot0618').name)
        self.assertTrue(line_ids[4].planned_hours == 4.0\
            and line_ids[4].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_ot1822').name)
        self.assertTrue(line_ids[5].planned_hours == 2.0\
            and line_ids[5].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_ot2224').name)
    
    def test_03_compute_line_ids(self):
        """
            Case: Test overtime interval NOT BELONG to any overtime rules.
            Expect: Failed to generate overtime line, overtime line is empty.
        """     
        monday_evening_ot_rule = self.env['hr.overtime.rule'].search(
            [('weekday', '=', str(self.next_monday.weekday())),
            ('code', '=', self.env.ref('viin_hr_overtime.rule_code_ot1822').name)
            ])
        monday_evening_ot_rule.hour_from = 20.0      
        self.overtime_plan_emp_01.date = self.next_monday
        self.overtime_plan_emp_01.time_end = 20.0    
        self.overtime_plan_emp_01.time_start = 18.0  
        self.assertFalse(self.overtime_plan_emp_01.line_ids)
    
    def test_04_compute_line_ids(self):
        """
            Case: Test OT interval is both inside and outside a overtime rule.
    
            *Overtime plan                                             
                Date Plan: NextMonday (from day testing)              
                Time Start: 18.0                                      
                Time End  : 22.0  
    
            * Monday evening overtime rule:                                          
                +--------+----------------------+-----------+---------+             
                |Code    |         Name         | Hour From | Hour To |             
                +--------+----------------------+-----------+---------+             
                | OT1822 | Monday Evening       |      20.0 |    22.0 |
                +--------+----------------------+-----------+---------+
    
            * Lines Overtime was generated:
                +-----------+---------+--------------+----------------------+-----------+
                | Hour from | Hour To | Planned Hour | Rule name            | Rule Code |
                +-----------+---------+--------------+----------------------+-----------+
                | 20.0      | 22.0    | 2.0          | Monday Evening       | OT1822    |
                +-----------+---------+--------------+----------------------+-----------+  
        """
        monday_evening_ot_rule = self.env['hr.overtime.rule'].search(
            [('weekday', '=', str(self.next_monday.weekday())),
            ('code', '=', self.env.ref('viin_hr_overtime.rule_code_ot1822').name)
        ])
        monday_evening_ot_rule.hour_from = 20.0      
        self.overtime_plan_emp_01.date = self.next_monday
        self.overtime_plan_emp_01.time_end = 22.0    
        self.overtime_plan_emp_01.time_start = 18.0  
        line_ids = self.overtime_plan_emp_01.line_ids
        self.assertTrue(len(line_ids) == 1)
        self.assertTrue(line_ids.planned_hours == 2.0\
            and line_ids.hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_ot1822').name)
    
    def test_05_compute_line_ids(self):
        """
            Case: Test compute OT interval in holiday.
            Expect: Overtime line was generated with total time is full plan period and satisfy overtime rule.
        """
        resource_calendar = self.contracts_emp_01.resource_calendar_id
        resource_calendar.global_leave_ids = [(0, 0, {
            'name':'Viin Holiday',
            'date_from':datetime.combine(self.next_monday , datetime.min.time()),
            'date_to':datetime.combine(self.next_monday + timedelta(days=1) , datetime.min.time()),
            'holiday':True
        })]     
        self.overtime_plan_emp_01.date = self.next_monday
        self.overtime_plan_emp_01.time_end = 22.0   
        self.overtime_plan_emp_01.time_start = 8.0
        line_ids = self.overtime_plan_emp_01.line_ids
        self.assertEquals(len(line_ids), 2)
        self.assertTrue(line_ids[0].planned_hours == 10.0\
            and line_ids[0].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_othol0618').name)
        self.assertTrue(line_ids[1].planned_hours == 4.0\
            and line_ids[1].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_othol1822').name)
    
    def test_06_compute_line_ids(self):
        """
            Case: Test compute OT interval in the day is not working.            
            Expect: Overtime line was generated with total time is full plan period and satisfy overtime rule.
        """   
        self.overtime_plan_emp_01.date = self._generate_overtime_plan_date(6)  # for Sunday
        self.overtime_plan_emp_01.time_end = 22.0   
        self.overtime_plan_emp_01.time_start = 8.0
        line_ids = self.overtime_plan_emp_01.line_ids
        self.assertEquals(len(line_ids), 3)
        self.assertTrue(line_ids[0].planned_hours == 4.0\
            and line_ids[0].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_otsun0612').name)
        self.assertTrue(line_ids[1].planned_hours == 6.0\
            and line_ids[1].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_otsun1218').name)
        self.assertTrue(line_ids[2].planned_hours == 4.0\
            and line_ids[2].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_otsun1822').name)
        
    def test_07_compute_line_ids(self):
        """
            Case: Test compute OT interval in Sunday with patch datetime/date.
            Expect: Overtime line was generated with total time is full plan period and satisfy overtime rule.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 17)):
            self.contracts_emp_01.date_start = date(2021, 3, 2)
            self.overtime_plan_emp_01.date = fields.Date.today()
            self.overtime_plan_emp_01.time_end = 22.0   
            self.overtime_plan_emp_01.time_start = 8.0
            line_ids = self.overtime_plan_emp_01.line_ids
            self.assertEquals(len(line_ids), 3)
            self.assertTrue(line_ids[0].planned_hours == 4.0\
                and line_ids[0].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_otsun0612').name)
            self.assertTrue(line_ids[1].planned_hours == 6.0\
                and line_ids[1].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_otsun1218').name)
            self.assertTrue(line_ids[2].planned_hours == 4.0\
                and line_ids[2].hr_overtime_rule_id.code == self.env.ref('viin_hr_overtime.rule_code_otsun1822').name)
    
    def test_07_compute_planned_hours_actual_hours_planed_pay_actual_pay(self):
        """
            Test compute overtime planned hours / actual hours and standard pay.
            * Overtime planned hours is totality of all plan lines planned hour.
            * Overtime actual hours is totality of all plan lines actual hour. 
            * Overtime planned pay is totality of all plan lines planned pay.
            * Overtime actual pay is totality of all plan lines actual pay.  
        """       
        self.overtime_plan_emp_01.date = self.next_monday
        self.overtime_plan_emp_01.time_end = 24.0    
        self.overtime_plan_emp_01.time_start = 0.0  
        line_ids = self.overtime_plan_emp_01.line_ids
        self.assertAlmostEqual(self.overtime_plan_emp_01.planned_hours, sum(line_ids.mapped('planned_hours')), 2)
        self.assertAlmostEqual(self.overtime_plan_emp_01.actual_hours, sum(line_ids.mapped('actual_hours')), 2)
        self.assertAlmostEqual(self.overtime_plan_emp_01.planned_overtime_pay, sum(line_ids.mapped('planned_overtime_pay')), 2)
        self.assertAlmostEqual(self.overtime_plan_emp_01.actual_overtime_pay, sum(line_ids.mapped('actual_overtime_pay')), 2)
    
    def test_08_compute_regconition_mode(self):
        """
            Case: Test compute overtime recognition mode.
            Expect: Overtime plan recognition mode should corresponding with Overtime Reason.
        """     
        self.env.ref('viin_hr_overtime.hr_overtime_reason_general').recognition_mode = OVERTIME_RECOGNITION_MODE[0][0]
        self.overtime_plan_emp_01.reason_id = self.env.ref('viin_hr_overtime.hr_overtime_reason_general').id
        self.assertEqual(
            self.overtime_plan_emp_01.recognition_mode,
            self.env.ref('viin_hr_overtime.hr_overtime_reason_general').recognition_mode)
    
    def test_09_duplicate_overtime_plan (self):
        """
            Case: Test compute duplicate overtime plan.
            Expect: Overtime plan cannot duplicate.
        """
        with self.assertRaises(UserError):
            self.overtime_plan_emp_01.copy()
    
    def test_10_overlap_period_overtime(self):
        """
            Case: Test overlap period in difference day.
            Expect: Can create successfully overtime plans with overlap period but in difference date.
        """        
        next_tuesday = self._generate_overtime_plan_date(1)  # for Tuesday
        self.overtime_plan_emp_01.date = next_tuesday
        self.overtime_plan_emp_01.time_end = 19.0    
        self.overtime_plan_emp_01.time_start = 17.0
    
        other_overtime_plan = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.overtime_reason_general.id,
            'date':self.next_monday,
            'time_end': 19.0,
            'time_start':17.0
        })  
        self.assertTrue(other_overtime_plan and True)
    
    def test_11_overlap_period_overtime(self):
        """
            Case: Test overlap period in same day.
            Expect: Failed to create overtime plans overlap period in same date.
        """        
        self.overtime_plan_emp_01.date = self.next_monday
        self.overtime_plan_emp_01.time_end = 19.0    
        self.overtime_plan_emp_01.time_start = 17.0
    
        with self.assertRaises(UserError):
            self.env['hr.overtime.plan'].create({
                'employee_id':self.employee_01.id,
                'reason_id':self.overtime_reason_general.id,
                'date':self.next_monday,
                'time_end': 19.0,
                'time_start':17.0
            })
