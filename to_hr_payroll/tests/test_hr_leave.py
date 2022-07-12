from datetime import datetime, date
from odoo import fields
from odoo.exceptions import ValidationError, UserError
from odoo.tests import tagged
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestHRLeave(TestPayrollCommon):
    @classmethod
    def setUpClass(cls):
        super(TestHRLeave, cls).setUpClass()
        
        cls.leave_type = cls.env['hr.leave.type'].search(
            [('company_id', '=', cls.env.company.id), ('unpaid', '=', True)],
            limit=1)
        cls.leave_type.write({
            'request_unit': 'day'
        })
    
    # 14. Kiểu Nghỉ
    def test_leave_type(self):
        """
        Case 1: Payroll Code hợp lệ
            Input: Kiểu nghỉ
                TH1: Giá trị trường Payroll Code là chỉ bao gồm chữ/số/dấu _
                TH2: Có các ký tự: ví dụ !@#
            Output:
                Lưu thành công
        """
         
        # TH1: Giá trị trường Payroll Code là chỉ bao gồm chữ/số/dấu _
        LeaveType = self.env['hr.leave.type']
        type1 = LeaveType.create({
            'name': 'Paid Time Off ',
            'responsible_id': self.env.user.id
        })
        type2 = LeaveType.create({
            'name': ' Nghỉ có Lương ',
            'responsible_id': self.env.user.id
        })
        self.assertEqual('PaidTimeOff', type1.code, 'Test compute Code not oke')
        self.assertEqual('NghicoLuong', type2.code, 'Test compute Code not oke')
          
        # TH2: Có các ký tự: ví dụ !@#
        self.assertRaises(ValidationError, type2.write, {'code': 'ABC@A'})
        self.assertRaises(ValidationError, type2.write, {'code': 'ABC.A'})
        type2.write({'code': 'ABCA'})
        self.assertEqual('ABCA', type2.code, 'Test Write Code field note oke')
    
    # 13. Nghỉ
    def test_leave(self):
        """
        Case 1: Test Hủy các xin nghỉ của nhân viên, thời gian xin nghỉ của nhân viên trùng khoảng thời gian của phiếu lương của nhân viên
            Output: Từ chối không thành công, thông báo ngoại lệ
        """
        # leave request: 7-9/7/2021
        date_from = fields.Datetime.from_string('2021-07-07 06:00:00')
        date_to = fields.Datetime.from_string('2021-07-09 20:00:00')
        hol1 = self.create_holiday('Test Leave 1', self.product_emp_A.id, self.leave_type.id, date_from, date_to)
        
        # Validate leave request
        hol1.action_validate()
        # payslip: 1/7/2021 - 31/7-2021
        payslip = self.create_payslip(self.product_emp_A.id,
            fields.Date.from_string('2021-07-01'),
            fields.Date.from_string('2021-07-30'),
            self.contract_open_emp_A.id)
        
        # use flush to update the relationship between payslip and leaves
        hol1.flush()
        payslip.flush()
        self.assertRaises(UserError, hol1.action_refuse)
    
    def test_adjust_dates_1(self):
        """
        Điều chỉnh ngày kết thúc trùng với ngày kết thúc muộn nhất của phiếu lương nằm trong khoảng xin nghỉ
            Input:
                Nghỉ tháng 7+8 (5/7 - 31/8)
                Tạo phiếu lương tháng 7 (1/7 - 31/7)
                Điều chỉnh ngày kết thúc xin nghỉ về 31/7
            Output:
                Điều chỉnh ngày kết thúc thành công, tính lại ngày ,giờ nghỉ
                Phiếu lương không bị ảnh hưởng
        """
        leave = self.create_holiday(
            'Test Leave 1', 
            self.product_emp_A.id, 
            self.leave_type.id,
            datetime(2021, 7, 5, 6, 0),
            datetime(2021, 8, 31, 15, 0))
        leave.action_validate()
        
        # payslip: 1/7/2021 - 31/7-2021
        payslip = self.create_payslip(self.product_emp_A.id,
            fields.Date.from_string('2021-07-01'),
            fields.Date.from_string('2021-07-31'),
            self.contract_open_emp_A.id)
        
        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': fields.Date.from_string('2021-07-05'),
            'date_to': fields.Date.from_string('2021-07-31')
        })
        wizard.action_confirm()
        self.assertRecordValues(leave, [{
            'date_from': datetime(2021, 7, 5, 6, 0),
            'date_to': datetime(2021, 7, 31, 15, 0),
            'number_of_days': 20,
            'number_of_days_display': 20,
            'number_of_hours_display': 160
        }])
        self.assertRecordValues(payslip, [{
            'worked_days': 2,
            'worked_hours': 16,
            'leave_days': 20,
            'leave_hours': 160,
        }])
    
    def test_adjust_dates_2(self):
        """
        Điều chỉnh ngày kết thúc lớn hơn ngày kết thúc muộn nhất của phiếu lương nằm trong khoảng xin nghỉ
            Input:
                Nghỉ từ 23/5 - 23/11
                Tạo phiếu lương tháng 5 (1/5 - 31/5)
                Điều chỉnh ngày kết thúc xin nghỉ về 6/10
            Output:
                Điều chỉnh ngày kết thúc thành công, tính lại ngày ,giờ nghỉ
                Phiếu lương không bị ảnh hưởng
        """
        leave = self.create_holiday(
            'Test Leave 1', 
            self.product_emp_A.id, 
            self.leave_type.id,
            datetime(2021, 5, 23, 6, 0),
            datetime(2021, 11, 23, 15, 0))
        leave.action_validate()
        
        # payslip: 1/5/2021 - 31/5-2021
        payslip = self.create_payslip(self.product_emp_A.id,
            fields.Date.from_string('2021-05-01'),
            fields.Date.from_string('2021-05-31'),
            self.contract_open_emp_A.id)
        
        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': fields.Date.from_string('2021-05-23'),
            'date_to': fields.Date.from_string('2021-10-6')
        })
        wizard.action_confirm()
        self.assertRecordValues(leave, [{
            'date_from': datetime(2021, 5, 23, 6, 0),
            'date_to': datetime(2021, 10, 6, 15, 0),
            # Tháng 5: 6d - 48h
            # Tháng 6: 22d - 176h
            # tháng 7: 22d - 176h
            # tháng 8: 22d - 176h
            # tháng 9: 22d - 176h
            # tháng 10: 4d - 32h
            'number_of_days': 98,
            'number_of_days_display': 98,
            'number_of_hours_display': 784
        }])
        self.assertRecordValues(payslip, [{
            'worked_days': 15,
            'worked_hours': 120,
            'leave_days': 6,
            'leave_hours': 48,
        }])
    
    def test_adjust_dates_3(self):
        """
        Điều chỉnh ngày kết thúc nhỏ hơn ngày kết thúc muộn nhất của phiếu lương nằm trong khoảng xin nghỉ
            Input:
                Nghỉ tháng 7+8 (5/7 - 31/8)
                Tạo phiếu lương tháng 7 (1/7 - 31/7)
                Điều chỉnh ngày kết thúc xin nghỉ về 29/7
            Output: không thành công
        """
        leave = self.create_holiday(
            'Test Leave 1',
            self.product_emp_A.id, 
            self.leave_type.id,
            datetime(2021, 7, 5, 6, 0),
            datetime(2021, 8, 31, 15, 0))
        leave.action_validate()
        
        # payslip: 1/7/2021 - 31/7-2021
        self.create_payslip(self.product_emp_A.id,
            fields.Date.from_string('2021-07-01'),
            fields.Date.from_string('2021-07-31'),
            self.contract_open_emp_A.id)
        
        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': fields.Date.from_string('2021-07-05'),
            'date_to': fields.Date.from_string('2021-07-29')
        })
        self.assertRaises(UserError, wizard.action_confirm)
    
    def test_adjust_dates_4(self):
        """
        Điều chỉnh lại ngày kết thúc của xin nghỉ có ngày kết thúc đã nằm trong phiếu lương
            Input:
                Nghỉ từ 5/7 - 15/7
                Tạo phiếu lương tháng 7 (1/7 - 31/7)
                Điều chỉnh ngày kết thúc xin nghỉ
            Output: không thành công
        """
        leave = self.create_holiday(
            'Test Leave 1',
            self.product_emp_A.id, 
            self.leave_type.id,
            datetime(2021, 7, 5, 6, 0),
            datetime(2021, 7, 15, 15, 0))
        leave.action_validate()
        
        # payslip: 1/7/2021 - 31/7-2021
        self.create_payslip(self.product_emp_A.id,
            fields.Date.from_string('2021-07-01'),
            fields.Date.from_string('2021-07-31'),
            self.contract_open_emp_A.id)
        
        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': fields.Date.from_string('2021-07-05'),
            'date_to': fields.Date.from_string('2021-07-20')
        })
        self.assertRaises(UserError, wizard.action_confirm)
    
    def test_adjust_dates_5(self):
        """
        Điều chỉnh lại ngày bắt đầu của xin nghỉ vào khoảng thời gian của phiếu lương
            Input:
                Nghỉ từ  5/7 - 15/7
                Tạo phiếu lương tháng 6 (1/6 - 30/6)
                Điều chỉnh ngày bắt đầu từ 5/7 về 25/6 và 25/5
            Output: không thành công
        """
        leave = self.create_holiday(
            'Test Leave 1',
            self.product_emp_A.id, 
            self.leave_type.id,
            datetime(2021, 7, 5, 6, 0),
            datetime(2021, 7, 15, 15, 0))
        leave.action_validate()
        
        # payslip: 1/7/2021 - 31/7-2021
        self.create_payslip(self.product_emp_A.id,
            fields.Date.from_string('2021-06-01'),
            fields.Date.from_string('2021-06-30'),
            self.contract_open_emp_A.id)
        
        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': fields.Date.from_string('2021-06-25'),
            'date_to': fields.Date.from_string('2021-07-15')
        })
        self.assertRaises(UserError, wizard.action_confirm)
        
        wizard.write({
            'date_from': fields.Date.from_string('2021-5-25')
        })
        self.assertRaises(UserError, wizard.action_confirm)
    
    def test_adjust_dates_6(self):
        """
        Điều chỉnh lại ngày kết thúc của xin nghỉ vào khoảng thời gian của phiếu lương
            Input:
                Nghỉ từ  5/7 - 15/7
                Tạo phiếu lương tháng 8 (1/8 - 31/8)
                Điều chỉnh ngày kết thúc từ 15/7 về 25/8 và 25/9
            Output: không thành công
        """
        leave = self.create_holiday(
            'Test Leave 1',
            self.product_emp_A.id, 
            self.leave_type.id,
            datetime(2021, 7, 5, 6, 0),
            datetime(2021, 7, 15, 15, 0))
        leave.action_validate()
        
        # payslip: 1/7/2021 - 31/7-2021
        self.create_payslip(self.product_emp_A.id,
            fields.Date.from_string('2021-08-01'),
            fields.Date.from_string('2021-08-30'),
            self.contract_open_emp_A.id)
        
        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': fields.Date.from_string('2021-07-05'),
            'date_to': fields.Date.from_string('2021-8-25')
        })
        self.assertRaises(UserError, wizard.action_confirm)
        
        wizard.write({
            'date_to': fields.Date.from_string('2021-09-25')
        })
        self.assertRaises(UserError, wizard.action_confirm)
    
    def test_adjust_dates_7(self):
        """
        Điều chỉnh lại ngày kết thúc của xin nghỉ vào khoảng thời gian của phiếu lương đã hủy
            Input:
                Nghỉ từ  5/7 - 15/7
                Tạo phiếu lương tháng 8 (1/8 - 31/8) - đã hủy
                Điều chỉnh ngày kết thúc từ 15/7 về 25/8
            Output: Thành công, tính lại ngày, giờ xin nghỉ
        """
        leave = self.create_holiday(
            'Test Leave 1',
            self.product_emp_A.id, 
            self.leave_type.id,
            datetime(2021, 7, 5, 6, 0),
            datetime(2021, 7, 15, 15, 0))
        leave.action_validate()
        
        # payslip: 1/7/2021 - 31/7-2021
        payslip = self.create_payslip(self.product_emp_A.id,
            fields.Date.from_string('2021-08-01'),
            fields.Date.from_string('2021-08-30'),
            self.contract_open_emp_A.id)
        payslip.action_payslip_verify()
        payslip.action_payslip_cancel()
        
        wizard = self.env['adjustment.leave'].create({
            'leave_id': leave.id,
            'date_from': fields.Date.from_string('2021-07-05'),
            'date_to': fields.Date.from_string('2021-8-25')
        })
        wizard.action_confirm()
        
        self.assertRecordValues(leave, [{
            'date_from': datetime(2021, 7, 5, 6, 0),
            'date_to': datetime(2021, 8, 25, 15, 0),
            'number_of_days': 38,
            'number_of_days_display': 38,
            'number_of_hours_display': 304
        }])
