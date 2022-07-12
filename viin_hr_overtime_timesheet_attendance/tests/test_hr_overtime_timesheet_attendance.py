from datetime import datetime,time,date
from unittest.mock import patch

from odoo.tests import tagged
from odoo import fields
from odoo.addons.viin_hr_overtime.tests.common import Common


@tagged('post_install','-at_install')
class TestHrOvertimeTimesheetAttendance(Common):
    
    def test_01_calculate_overtime_actual_hours(self):
        """
            Test case: Kiểm tra tính toán giờ tăng ca thực tế khi chế độ nhận diện tăng ca là "có mặt hoặc chấm công"
            Input: Chỉ có dữ liệu vào ra khớp với thời gian kế hoạch tăng ca
            Expect: Giờ tăng ca thực tế tính theo giờ vào ra hợp lệ.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            #Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'recognition_mode':'attendance_or_timesheet',
                'date':fields.Date.today(),
                'time_end':21.5,
                'time_start':19.0
               })
            #Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC. 
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(17,0)),
                'check_out':datetime.combine(fields.Date.today(), time(19,0))
            })
            self.overtime_plan_emp_01.action_match_attendances()   
            self.assertRecordValues(
                self.overtime_plan_emp_01,
                [
                    {
                        'matched_attendance_hours': 2.0,
                        'matched_timesheet_hours': 0.0,
                        'actual_hours': 2.0,
                    }
                ]
            )   
    
    def test_02_calculate_overtime_actual_hours(self):
        """
            Test case: Kiểm tra tính toán giờ tăng ca thực tế khi chế độ nhận diện tăng ca là "có mặt hoặc chấm công"
            Input: Chỉ có dữ liệu chấm công khớp với thời gian kế hoạch tăng ca
            Expect: Giờ tăng ca thực tế tính theo giờ chấm công.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
        #Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'recognition_mode':'attendance_or_timesheet',
                'date':fields.Date.today(),
                'time_end':21.5,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({            
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':19.0,
                'unit_amount':2.5,
                'project_id': self.env.ref('project.project_project_1').id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertRecordValues(
                self.overtime_plan_emp_01,
                [
                    {
                        'matched_attendance_hours': 0.0,
                        'matched_timesheet_hours': 2.5,
                        'actual_hours': 2.5,
                    }
                ]
            )   
        
    def test_03_calculate_overtime_actual_hours(self):
        """
            Test case: Kiểm tra tính toán giờ tăng ca thực tế khi chế độ nhận diện tăng ca là "có mặt hoặc chấm công"
            Input: Cả giờ chấm công và giờ đăng ký vào ra đều không khớp với giờ kế hoạch tăng ca.
            Expect: Giờ tăng ca thực tế bằng 0.0
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
             #Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'recognition_mode':'attendance_or_timesheet',
                'date':fields.Date.today(),
                'time_end':21.5,
                'time_start':19.0
            })
            #Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(15,0)),
                'check_out':datetime.combine(fields.Date.today(), time(17,0))
            })
            self.env['account.analytic.line'].create({            
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':self.next_monday,
                'time_start':17.0,
                'unit_amount':2.0,
                'project_id': self.env.ref('project.project_project_1').id
            })
            self.overtime_plan_emp_01.action_match_attendances()      
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            #Giờ đăng ký vào ra và giờ chấm công đều không nằm trong giờ kế hoạch tăng ca. Giờ tăng ca thực tế bằng 0.0. 
            self.assertRecordValues(
                self.overtime_plan_emp_01,
                [
                    {
                        'matched_attendance_hours': 0.0,
                        'matched_timesheet_hours': 0.0,
                        'actual_hours': 0.0,
                    }
                ]
            ) 
                 
    def test_04_calculate_overtime_actual_hours(self):
        """
            Test case: Kiểm tra tính toán giờ tăng ca thực tế khi chế độ nhận diện tăng ca là "có mặt hoặc chấm công"
            Input: Cả giờ chấm công và giờ đăng ký vào ra đều khớp với giờ kế hoạch tăng ca.
            Expect: Giờ tăng ca thực tế được ưu tiên tính theo giờ đăng ký vào ra hợp lệ.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            #Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'recognition_mode':'attendance_or_timesheet',
                'date':fields.Date.today(),
                'time_end':21.5,
                'time_start':19.0
            })
            #Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC.
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(17,0)),
                'check_out':datetime.combine(fields.Date.today(), time(19,0))
            })
            self.env['account.analytic.line'].create({            
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':19.0,
                'unit_amount':2.5,
                'project_id': self.env.ref('project.project_project_1').id
            })
            self.overtime_plan_emp_01.action_match_attendances()      
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            #Giờ tăng ca thực tế uu tiên lấy theo thời gian đăng ký vào ra. 
            self.assertRecordValues(
                self.overtime_plan_emp_01,
                [
                    {
                        'matched_attendance_hours': 2.0,
                        'matched_timesheet_hours': 2.5,
                        'actual_hours': 2.0,
                    }
                ]
            ) 
    
    def test_05_calculate_overtime_actual_hours(self):
        """
            Test case: Kiểm tra tính toán giờ tăng ca thực tế khi chế độ nhận diện tăng ca là "có mặt và chấm công"
            Input: Chỉ có dữ liệu chấm công khớp với giờ kế hoạch tăng ca.
            Expect: Giờ tăng ca thực tế bằng 0.0
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            #Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'recognition_mode':'attendance_and_timesheet',
                'date':fields.Date.today(),
                'time_end':21.5,
                'time_start':19.0
            })
            self.env['account.analytic.line'].create({            
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':19.0,
                'unit_amount':2.5,
                'project_id': self.env.ref('project.project_project_1').id
            })
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertRecordValues(
                self.overtime_plan_emp_01,
                [
                    {
                        'matched_attendance_hours': 0.0,
                        'matched_timesheet_hours': 2.5,
                        'actual_hours': 0.0,
                    }
                ]
            ) 
            
    def test_06_calculate_overtime_actual_hours(self):
        """
            Test case: Kiểm tra tính toán giờ tăng ca thực tế khi chế độ nhận diện tăng ca là "có mặt và chấm công"
            Input: Chỉ có dữ đăng ký vào ra khớp với giờ kế hoạch tăng ca.
            Expect: Giờ tăng ca thực tế bằng 0.0
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            #Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'recognition_mode':'attendance_and_timesheet',
                'date':fields.Date.today(),
                'time_end':21.5,
                'time_start':19.0
            })
            #Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC. 
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(17,0)),
                'check_out':datetime.combine(fields.Date.today(), time(19,30))
            })
            self.overtime_plan_emp_01.action_match_attendances()    
            self.assertRecordValues(
                self.overtime_plan_emp_01,
                [
                    {
                        'matched_attendance_hours': 2.5,
                        'matched_timesheet_hours': 0.0,
                        'actual_hours': 0.0,
                    }
                ]
            )  
            
    def test_07_calculate_overtime_actual_hours(self):
        """
            Test case: Kiểm tra tính toán giờ tăng ca thực tế khi chế độ nhận diện tăng ca là "có mặt và chấm công"
            Input: có cả dữ liệu giờ đăng ký vào ra và chấm công khớp với thời gian kế hoạch tăng ca.
            Expect: Giờ tăng ca thực tế bằng giờ kế hoạch tăng ca.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            #Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'recognition_mode':'attendance_and_timesheet',
                'date':fields.Date.today(),
                'time_end':21.5,
                'time_start':19.0
            })
            #Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC. 
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(17,0)),
                'check_out':datetime.combine(fields.Date.today(), time(19,30))
            })
            self.env['account.analytic.line'].create({            
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':19.0,
                'unit_amount':2.5,
                'project_id': self.env.ref('project.project_project_1').id
            })
            self.overtime_plan_emp_01.action_match_attendances()    
            self.overtime_plan_emp_01.action_match_timesheet_entries()    
            self.assertRecordValues(
                self.overtime_plan_emp_01,
                [
                    {
                        'matched_attendance_hours': 2.5,
                        'matched_timesheet_hours': 2.5,
                        'actual_hours': 2.5,
                    }
                ]
            )
            
    def test_08_calculate_overtime_actual_hours(self):
        """
            Test case: Kiểm tra tính toán giờ tăng ca thực tế khi chế độ nhận diện tăng ca là "có mặt và chấm công"
            Input: Giờ đăng ký vào ra và giờ chấm công nằm trong khoảng thời gian tăng ca.
            Expect: Giờ tăng ca thực tế là thời gian khớp giữa giờ đăng ký vào ra và giờ chấm công.
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            #Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'recognition_mode':'attendance_and_timesheet',
                'date':fields.Date.today(),
                'time_end':21.5,
                'time_start':19.0
            })
            #Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC. 
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(17,0)),
                'check_out':datetime.combine(fields.Date.today(), time(19,0))
            })
            self.env['account.analytic.line'].create({            
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':19.5,
                'unit_amount':2.0,
                'project_id': self.env.ref('project.project_project_1').id
            })
            self.overtime_plan_emp_01.action_match_attendances()    
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertRecordValues(
                self.overtime_plan_emp_01,
                [
                    {
                        'matched_attendance_hours': 2.0,
                        'matched_timesheet_hours': 2.0,
                        'actual_hours': 1.5,
                    }
                ]
            ) 
      
    def test_09_calculate_overtime_actual_hours(self):   
        """
            Test case: Kiểm tra tính toán giờ tăng ca thực tế khi chế độ nhận diện tăng ca là "có mặt và chấm công"
            Input: Giờ đăng ký vào ra và giờ chấm công nằm trong khoảng thời gian tăng ca nhưng không khớp nhau
            Expect: Giờ tăng ca thực tế bằng 0.0
        """
        with patch.object(fields.Date, 'today', lambda: date(2021, 10, 18)):
            self.contracts_emp_01.date_start = date(2021,3,2)
            #Thời gian kế bắt đầu và kết thúc kế hoạch tăng ca được tham chiếu theo múi giờ của người dùng (mặc định là UTC +2)
            self.overtime_plan_emp_01.update({
                'recognition_mode':'attendance_and_timesheet',
                'date':fields.Date.today(),
                'time_end':21.5,
                'time_start':19.0
            })
            #Thời gian đăng ký vào ra được tham chiếu theo giờ tại thiết bị của người dùng, trong trường hợp test này sẽ trùng với thời gian UTC. 
            self.env['hr.attendance'].create({
                'employee_id':self.employee_01.id,
                'check_in':datetime.combine(fields.Date.today(), time(17,0)),
                'check_out':datetime.combine(fields.Date.today(), time(18,0))
            })
            self.env['account.analytic.line'].create({            
                'name':'Research new project',
                'employee_id':self.employee_01.id,
                'date':fields.Date.today(),
                'time_start':20.5,
                'unit_amount':1.0,
                'project_id': self.env.ref('project.project_project_1').id
            })
            self.overtime_plan_emp_01.action_match_attendances()    
            self.overtime_plan_emp_01.action_match_timesheet_entries()
            self.assertRecordValues(
                self.overtime_plan_emp_01,
                [
                    {
                        'matched_attendance_hours': 1.0,
                        'matched_timesheet_hours': 1.0,
                        'actual_hours': 0.0,
                    }
                ]
            ) 
