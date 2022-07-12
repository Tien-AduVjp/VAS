from datetime import datetime

from unittest.mock import patch
from odoo import fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF

from .common import TestPayrollCommon


class TestPayrollPayslipWorkingCalendarDetail(TestPayrollCommon): 
    
    @classmethod
    def setUpClass(cls):
        super(TestPayrollPayslipWorkingCalendarDetail, cls).setUpClass()
        
        cls.contract_open_emp_A.write({'wage': 5000000})  # không phải đóng thuế
        
        cls.salary_cycle_2 = cls.env['hr.salary.cycle'].create({
                'name': 'Test Salary Cycle 2',
                'start_day_offset': 5,
            })
        cls.salary_cycle_3 = cls.env['hr.salary.cycle'].create({
                'name': 'Test Salary Cycle 3',
                'start_day_offset': 5,
                'start_month_offset': 1
            })
        cls.salary_cycle_4 = cls.env['hr.salary.cycle'].create({
                'name': 'Test Salary Cycle 4',
                'start_day_offset': 5,
                'start_month_offset':-1
            })
        
        LeaveType = cls.env['hr.leave.type']
        cls.unpaid_type = LeaveType.search([('company_id', '=', cls.env.company.id), ('unpaid', '=', True)], limit=1)
        cls.paid_type = LeaveType.search(
            [('company_id', '=', cls.env.company.id),
             ('unpaid', '=', False),
             ('code', '=', 'PaidTimeOff')],
            limit=1)
    
    # 8. Phiếu lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-4'))
    def test_13th_month_payslip_working_calendar_1(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2A: Test bảng "Chi tiết lịch làm việc" trên phiếu lương 13
                TH1: chu kỳ lương không lệch chuẩn
                    TH1.1: chu kỳ của phiếu lương = chu kỳ lương
                        12 dòng
                    TH1.2: chu kỳ của phiếu lương nằm trong chu kỳ lương
                        <= 12 dòng
                    TH1.3: chu kỳ của phiếu lương nằm ngoài chu kỳ lương
                        >= 12 dòng
        """
             
        # TH1.1: chu kỳ của phiếu lương = chu kỳ lương    1/1/2020 - 31/12/2020
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        payslip.write({'thirteen_month_pay': True})
         
        self.assertEqual(len(payslip.working_month_calendar_ids), 12, 'Test working_month_calendar_ids field not oke')
         
        # TH1.2: chu kỳ của phiếu lương nằm trong chu kỳ lương
        payslip.write({'date_from': fields.Date.from_string('2020-1-10')})
        self.assertEqual(len(payslip.working_month_calendar_ids), 12, 'Test working_month_calendar_ids field not oke')
        
        payslip.write({'date_from': fields.Date.from_string('2020-7-7')})
        self.assertEqual(len(payslip.working_month_calendar_ids), 6, 'Test working_month_calendar_ids field not oke')
        
        # TH1.3: chu kỳ của phiếu lương nằm ngoài chu kỳ lương
        payslip.write({'date_to': fields.Date.from_string('2021-1-15')})
        self.assertEqual(len(payslip.working_month_calendar_ids), 13, 'Test working_month_calendar_ids field not oke')
     
    # 8. Phiếu lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-4'))
    def test_13th_month_payslip_working_calendar_2(self):
        """
        8.2 Test Thông tin của phiếu lương
            Case 2A: Test bảng "Chi tiết lịch làm việc" trên phiếu lương 13
                TH2: chu kỳ lương lệch chuẩn - lệch ngày dương
                    TH2.1: chu kỳ của phiếu lương = chu kỳ lương
                        12 dòng
                    TH2.2: chu kỳ của phiếu lương nằm trong chu kỳ lương
                        <= 12 dòng
                    TH2.3: chu kỳ của phiếu lương nằm ngoài chu kỳ lương
                        >= 12 dòng
        """
        # lệch dương 5 ngày
        self.env.company.salary_cycle_id = self.salary_cycle_2
         
        # TH2.1: chu kỳ của phiếu lương = chu kỳ lương    5/1/2020 - 5/1/2021
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        payslip.write({'thirteen_month_pay': True})
        self.assertEqual(payslip.thirteen_month_pay_year, 2020, 'Test thirteen_month_pay_year field not oke')
        self.assertEqual(len(payslip.working_month_calendar_ids), 12, 'Test working_month_calendar_ids field not oke')
         
        # TH2.2: chu kỳ của phiếu lương nằm trong chu kỳ lương: 6/1/2020 - 5/7/2020
        payslip.write({
            'date_to': fields.Date.from_string('2020-7-5')
            })
        self.assertEqual(len(payslip.working_month_calendar_ids), 6, 'Test working_month_calendar_ids field not oke')
         
        # TH2.3: chu kỳ của phiếu lương nằm ngoài chu kỳ lương: 6/1/2020 - 31/1/2021
        payslip.write({
            'date_to': fields.Date.from_string('2021-1-31')
            })
        self.assertEqual(len(payslip.working_month_calendar_ids), 13, 'Test working_month_calendar_ids field not oke')
     
    # 8. Phiếu lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-4'))
    def test_13th_month_payslip_working_calendar_3(self):
        """
        8.2 Test Thông tin của phiếu lương
            Case 2A: Test bảng "Chi tiết lịch làm việc" trên phiếu lương 13
                TH3: chu kỳ lương lệch chuẩn - lệch ngày dương, tháng dương
                    TH3.1: chu kỳ của phiếu lương = chu kỳ lương
                        12 dòng
                    TH3.2: chu kỳ của phiếu lương nằm trong chu kỳ lương
                        <= 12 dòng
                    TH3.3: chu kỳ của phiếu lương nằm ngoài chu kỳ lương
                        >= 12 dòng
        """
        # lệch dương 5 ngày, dương 1 tháng
        self.env.company.salary_cycle_id = self.salary_cycle_3
         
        # TH2.1: chu kỳ của phiếu lương = chu kỳ lương    6/2/2020 - 4/2/2021
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        payslip.write({'thirteen_month_pay': True})
        self.assertEqual(payslip.thirteen_month_pay_year, 2020, 'Test thirteen_month_pay_year field not oke')
        self.assertEqual(len(payslip.working_month_calendar_ids), 12, 'Test working_month_calendar_ids field not oke')
         
        # TH2.2: chu kỳ của phiếu lương nằm trong chu kỳ lương: 6/2/2020 - 5/7/2020
        payslip.write({
            'date_to': fields.Date.from_string('2020-7-5')
            })
        self.assertEqual(len(payslip.working_month_calendar_ids), 5, 'Test working_month_calendar_ids field not oke')
         
        # TH2.3: chu kỳ của phiếu lương nằm ngoài chu kỳ lương: 6/2/2020 - 28/2/2021
        payslip.write({
            'date_to': fields.Date.from_string('2021-2-28')
            })
        self.assertEqual(len(payslip.working_month_calendar_ids), 13, 'Test working_month_calendar_ids field not oke')
    
    # 8. Phiếu lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-4'))
    def test_13th_month_payslip_working_calendar_4(self):
        """
        8.2 Test Thông tin của phiếu lương
            Case 2A: Test bảng "Chi tiết lịch làm việc" trên phiếu lương 13
                TH4: chu kỳ lương lệch chuẩn - lệch ngày dương, tháng âm
                    TH4.1: chu kỳ của phiếu lương = chu kỳ lương
                        12 dòng
                    TH4.2: chu kỳ của phiếu lương nằm trong chu kỳ lương
                        <= 12 dòng
                    TH4.3: chu kỳ của phiếu lương nằm ngoài chu kỳ lương
                        >= 12 dòng
        """
        # lệch dương 5 ngày, âm 1 tháng    6/12/2019 - 5/12/2020
        self.env.company.salary_cycle_id = self.salary_cycle_4
        
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        payslip.write({'thirteen_month_pay': True})
        self.assertEqual(payslip.thirteen_month_pay_year, 2020, 'Test thirteen_month_pay_year field not oke')
        self.assertEqual(len(payslip.working_month_calendar_ids), 12, 'Test working_month_calendar_ids field not oke')
         
        # TH2.2: chu kỳ của phiếu lương nằm trong chu kỳ lương: 6/12/2019 - 5/7/2020
        payslip.write({
            'date_to': fields.Date.from_string('2020-7-5')
            })
        self.assertEqual(len(payslip.working_month_calendar_ids), 7, 'Test working_month_calendar_ids field not oke')
         
        # TH2.3: chu kỳ của phiếu lương nằm ngoài chu kỳ lương: 6/12/2019 - 1/1/2021
        payslip.write({
            'date_to': fields.Date.from_string('2021-1-1')
            })
        self.assertEqual(len(payslip.working_month_calendar_ids), 13, 'Test working_month_calendar_ids field not oke')
     
    # 8. Phiếu lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-4'))
    def test_13th_month_payslip_working_calendar_5(self):
        """
        8.2 Test Thông tin của phiếu lương
            Case 2A: Test bảng "Chi tiết lịch làm việc" trên phiếu lương 13
                TH5: Các TH liên quan đến lệch ngày âm:
        """
        # TODO: Fix me when start_day_offset is negative
     
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_1(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2B: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương không lệch chuẩn
                TH1: Không có ngày nghỉ, trong 1 tháng, Kiểu tính toán phiếu lương: giờ
        """
        # prepare data
        self.contract_open_emp_A.write({'salary_computation_mode': 'hour_basis'})
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1,
        }])
        
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': 5000000,
            },
            {
                'code': 'GROSS',
                'amount': 5000000,
            },
            {
                'code': 'NET',
                'amount': 5000000,
            }])
         
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_3(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2B: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương không lệch chuẩn
                TH3: Không có ngày nghỉ, trong nhiều tháng, Kiểu tính toán phiếu lương: giờ
        """
        # prepare data
        self.contract_open_emp_A.write({'salary_computation_mode': 'hour_basis'})
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-15'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 44,
            'calendar_working_hours': 352,
            'duty_working_days': 34,
            'duty_working_hours': 272,
            'worked_days': 34,
            'worked_hours': 272,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            # 15/6 -> 30/6: 22days - 96hours
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 12,
            'duty_working_hours': 96,
            'worked_days': 12,
            'worked_hours': 96,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 96 / 176
            },
            {
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-6-1'),
            'date_to': fields.Date.from_string('2021-6-30'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 12,
            'duty_working_hours': 96,
            'worked_days': 12,
            'worked_hours': 96,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 96 / 176,
            },
            {
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1,
        }])
        
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        currnecy = payslip.currency_id
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': currnecy.round(7727272.72727),  # 5000000 + 5000000 * 96/176,
            },
            {
                'code': 'GROSS',
                'amount': currnecy.round(7727272.72727),  # 5000000 + 5000000 * 96/176,
            },
            {
                'code': 'NET',
                'amount': currnecy.round(7727272.72727),  # 5000000 + 5000000 * 96/176,
            }])
             
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_2(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2B: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương không lệch chuẩn
                TH2: Không có ngày nghỉ, trong 1 tháng, Kiểu tính toán phiếu lương: ngày
        """
        # prepare data
        self.contract_open_emp_A.write({'salary_computation_mode': 'day_basis'})
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1,
        }])
        
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': 5000000,
            },
            {
                'code': 'GROSS',
                'amount': 5000000,
            },
            {
                'code': 'NET',
                'amount': 5000000,
            }])
          
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_4(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2B: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương không lệch chuẩn
                TH4: Không có ngày nghỉ, trong nhiều tháng, Kiểu tính toán phiếu lương: ngày
        """
        # prepare data
        self.contract_open_emp_A.write({'salary_computation_mode': 'day_basis'})
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-15'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 44,
            'calendar_working_hours': 352,
            'duty_working_days': 34,
            'duty_working_hours': 272,
            'worked_days': 34,
            'worked_hours': 272,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            # 15/6 -> 30/6: 22days - 96hours
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 12,
            'duty_working_hours': 96,
            'worked_days': 12,
            'worked_hours': 96,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 96 / 176
            },
            {
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-6-1'),
            'date_to': fields.Date.from_string('2021-6-30'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 12,
            'duty_working_hours': 96,
            'worked_days': 12,
            'worked_hours': 96,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 96 / 176,
            },
            {
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1,
        }])
          
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        currency = payslip.currency_id
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': currency.round(7727272.72727),  # 5000000 + 5000000 * 96/176,
            },
            {
                'code': 'GROSS',
                'amount': currency.round(7727272.72727),  # 5000000 + 5000000 * 96/176,
            },
            {
                'code': 'NET',
                'amount': currency.round(7727272.72727),  # 5000000 + 5000000 * 96/176,
            }])
          
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_5(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2B: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương không lệch chuẩn
                TH5: Có ngày nghỉ, trong 1 tháng, Kiểu tính toán phiếu lương: giờ
        """
        # prepare data
        self.contract_open_emp_A.write({'salary_computation_mode': 'hour_basis'})
              
        # leave: 2.5 days - 20 hours
        # unpaid: 1.5 days - 12 hours
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-10h
            datetime.strptime('2021-7-1 6:00:00', DTF),
            datetime.strptime('2021-7-2 10:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 2',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-6 6:00:00', DTF),
            datetime.strptime('2021-7-6 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
              
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 176 - 12
            'paid_rate': 164 / 176
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 176 - 12
            'paid_rate': 164 / 176
        }])
         
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        currency = payslip.currency_id
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': currency.round(4659090.90909),  # 5000000 * 164/176,
            },
            {
                'code': 'GROSS',
                'amount': currency.round(4659090.90909),  # 5000000 * 164/176,
            },
            {
                'code': 'NET',
                'amount': currency.round(4659090.90909),  # 5000000 * 164/176,
            }])
          
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_7(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2B: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương không lệch chuẩn
                TH7: Có ngày nghỉ, trong nhiều tháng, Kiểu tính toán phiếu lương: giờ
        """
        # prepare data
        self.contract_open_emp_A.write({'salary_computation_mode': 'hour_basis'})
              
        # July
        # leave: 2.5 days - 20 hours
        # unpaid: 1.5 days - 12 hours
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-12h
            datetime.strptime('2021-7-1 6:00:00', DTF),
            datetime.strptime('2021-7-2 10:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-6 6:00:00', DTF),
            datetime.strptime('2021-7-6 15:59:59', DTF))
        hol1.action_validate()
        hol2.action_validate()
        # June
        # leaves: 1.5 days - 12 hours
        # unpaid: 0.5 days - 4 hours
        hol3 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-12h
            datetime.strptime('2021-6-21 6:00:00', DTF),
            datetime.strptime('2021-6-21 10:00:00', DTF))
        hol4 = self.create_holiday(
            'Test Unpaid Leave 2',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-6-22 6:00:00', DTF),
            datetime.strptime('2021-6-22 15:00:00', DTF))
        hol3.action_validate()
        hol4.action_validate()
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-15'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 44,
            'calendar_working_hours': 352,
            'duty_working_days': 34,
            'duty_working_hours': 272,
            'worked_days': 30,
            'worked_hours': 240,
            'leave_days': 4,
            'leave_hours': 32,
            'unpaid_leave_days': 2,
            'unpaid_leave_hours': 16,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            # 15/6 -> 30/6: 22days - 96hours
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 12,
            'duty_working_hours': 96,
            'worked_days': 10.5,
            'worked_hours': 84,
            'leave_days': 1.5,
            'leave_hours': 12,
            'unpaid_leave_days': 0.5,
            'unpaid_leave_hours': 4,
            # 96 - 4
            'paid_rate': 92 / 176
            },
            {
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 176 - 12
            'paid_rate': 164 / 176
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-6-1'),
            'date_to': fields.Date.from_string('2021-6-30'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 12,
            'duty_working_hours': 96,
            'worked_days': 10.5,
            'worked_hours': 84,
            'leave_days': 1.5,
            'leave_hours': 12,
            'unpaid_leave_days': 0.5,
            'unpaid_leave_hours': 4,
            # 96 - 4
            'paid_rate': 92 / 176,
            },
            {
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 176 - 12
            'paid_rate': 164 / 176,
        }])
                   
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        currency = payslip.currency_id
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': currency.round(7272727.27273),  # 5000000 * 92/176 + 5000000 * 164/176,
            },
            {
                'code': 'GROSS',
                'amount': currency.round(7272727.27273),  # 5000000 * 92/176 + 5000000 * 164/176,
            },
            {
                'code': 'NET',
                'amount': currency.round(7272727.27273),  # 5000000 * 92/176 +  5000000 * 164/176,
            }])
           
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_6(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2B: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương không lệch chuẩn
                TH6: Có ngày nghỉ, trong 1 tháng, Kiểu tính toán phiếu lương: ngày
        """
        # prepare data
        self.contract_open_emp_A.write({'salary_computation_mode': 'day_basis'})
             
        # July
        # leave: 2.5 days - 20 hours
        # unpaid: 1.5 days - 12 hours
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-1 6:00:00', DTF),
            datetime.strptime('2021-7-2 10:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-6 6:00:00', DTF),
            datetime.strptime('2021-7-6 15:00:0', DTF))
        hol1.action_validate()
        hol2.action_validate()
             
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
        }])
          
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 22 - 1.5
            'paid_rate': 20.5 / 22
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 22 - 1.5
            'paid_rate': 20.5 / 22
        }])
          
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        currency = payslip.currency_id
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': currency.round(4659090.90909),  # 5000000 * 20.5/22
            },
            {
                'code': 'GROSS',
                'amount': currency.round(4659090.90909),  # 5000000 * 20.5/22
            },
            {
                'code': 'NET',
                'amount': currency.round(4659090.90909),  # 5000000 * 20.5/22
            }])
          
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_8(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2B: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương không lệch chuẩn
                Th8: Có ngày nghỉ, trong nhiều tháng, Kiểu tính toán phiếu lương: ngày
        """
        # prepare data
        self.contract_open_emp_A.write({'salary_computation_mode': 'hour_basis'})
             
        # July
        # leave: 2.5 days - 20 hours
        # unpaid: 1.5 days - 12 hours
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-12h
            datetime.strptime('2021-7-1 6:00:00', DTF),
            datetime.strptime('2021-7-2 10:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-6 6:00:00', DTF),
            datetime.strptime('2021-7-6 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        # June
        # leaves: 1.5 days - 12 hours
        # unpaid: 0.5 days - 4 hours
        hol3 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-12h
            datetime.strptime('2021-6-21 6:00:00', DTF),
            datetime.strptime('2021-6-21 10:00:00', DTF))
        hol4 = self.create_holiday(
            'Test Unpaid Leave 2',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-6-22 6:00:00', DTF),
            datetime.strptime('2021-6-22 15:59:59', DTF))
        hol3.action_validate()
        hol4.action_validate()
             
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-15'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 44,
            'calendar_working_hours': 352,
            'duty_working_days': 34,
            'duty_working_hours': 272,
            'worked_days': 30,
            'worked_hours': 240,
            'leave_days': 4,
            'leave_hours': 32,
            'unpaid_leave_days': 2,
            'unpaid_leave_hours': 16,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            # 15/6 -> 30/6: 22days - 96hours
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 12,
            'duty_working_hours': 96,
            'worked_days': 10.5,
            'worked_hours': 84,
            'leave_days': 1.5,
            'leave_hours': 12,
            'unpaid_leave_days': 0.5,
            'unpaid_leave_hours': 4,
            # 12 - 0.5
            'paid_rate': 11.5 / 22
            },
            {
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 22 - 1.5
            'paid_rate': 20.5 / 22
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-6-1'),
            'date_to': fields.Date.from_string('2021-6-30'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 12,
            'duty_working_hours': 96,
            'worked_days': 10.5,
            'worked_hours': 84,
            'leave_days': 1.5,
            'leave_hours': 12,
            'unpaid_leave_days': 0.5,
            'unpaid_leave_hours': 4,
            # 12 - 0.5
            'paid_rate': 11.5 / 22
            },
            {
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 22 - 1.5
            'paid_rate': 20.5 / 22
        }])
        
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        currency = payslip.currency_id
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': currency.round(7272727.27273),  # 5000000 * 20.5/22 + 5000000 * 11.5/22
            },
            {
                'code': 'GROSS',
                'amount': currency.round(7272727.27273),  # 5000000 * 20.5/22 + 5000000 * 11.5/22
            },
            {
                'code': 'NET',
                'amount': currency.round(7272727.27273),  # 5000000 * 20.5/22 + 5000000 * 11.5/22
            }])
          
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_9(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2B: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương không lệch chuẩn
                TH9: trong 1 tháng, có nhiều hợp đồng hợp lệ trong khoảng này
        """
              
        # prepare data
        contract_1 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-10'),
            'open',
            wage=5000000)
        contract_2 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-11'),
            fields.Date.from_string('2021-7-20'),
            'open',
            wage=5000000)
        contract_3 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-21'),
            fields.Date.from_string('2021-7-31'),
            'open',
            wage=5000000)
        
        payslip = self.create_payslip(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            contract_3.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
           
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 22,
            'worked_hours': 176,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 3, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            # 1/7 -> 10/7 : 7 days - 56 hours
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-10'),
            'contract_id': contract_1.id,
            'calendar_working_days': 7,
            'calendar_working_hours': 56,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 7,
            'worked_hours': 56,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 56 / 176
            },
            {
            # 11/7 -> 20/7 : 7 days - 56 hours
            'date_from': fields.Date.from_string('2021-7-11'),
            'date_to': fields.Date.from_string('2021-7-20'),
            'contract_id': contract_2.id,
            'calendar_working_days': 7,
            'calendar_working_hours': 56,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 7,
            'worked_hours': 56,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 56 / 176
            },
            {
            # 21/7 -> 31/7 : 8 days - 64 hours
            'date_from': fields.Date.from_string('2021-7-21'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'contract_id': contract_3.id,
            'calendar_working_days': 8,
            'calendar_working_hours': 64,
            'duty_working_days': 8,
            'duty_working_hours': 64,
            'worked_days': 8,
            'worked_hours': 64,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 64 / 176
            },
        ])
        
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': 5000000,  # 5000000 * 56/176 + 5000000 * 56/176 + 5000000 * 64/176
            },
            {
                'code': 'GROSS',
                'amount': 5000000,  # 5000000 * 20.5/22 + 5000000 * 11.5/22
            },
            {
                'code': 'NET',
                'amount': 5000000,  # 5000000 * 20.5/22 + 5000000 * 11.5/22
            }])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_10(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày dương
                TH1: Không có ngày nghỉ, trong 1 tháng, Kiểu tính toán phiếu lương: giờ
                    => 1 dòng chi tiết lịch làm việc với 1 dòng chi tiết, các thông tin về giờ/ngày nghỉ = 0, 
                        tỷ lệ chi trả được tính theo giờ
        """
        # prepare data: lệch dương 5 ngày
        self.env.company.salary_cycle_id = self.salary_cycle_2
        self.contract_open_emp_A.write({'salary_computation_mode': 'hour_basis'})
        # lệch 5 ngày => 6/7/2021 - 5/8/2021
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-6'),
            fields.Date.from_string('2021-8-5'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 23,
            'month_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-6'),
            'date_to': fields.Date.from_string('2021-8-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1,
        }])
        
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': 5000000,
            },
            {
                'code': 'GROSS',
                'amount': 5000000,
            },
            {
                'code': 'NET',
                'amount': 5000000,
            }])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_11(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày dương
                TH2: Không có ngày nghỉ, trong 1 tháng, Kiểu tính toán phiếu lương: ngày
        """
        # prepare data: lệch dương 5 ngày => 6/7/2021 - 5/8/2021
        self.env.company.salary_cycle_id = self.salary_cycle_2
        self.contract_open_emp_A.write({'salary_computation_mode': 'day_basis'})
        # lệch 5 ngày => 6/7/2021 - 5/8/2021
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-6'),
            fields.Date.from_string('2021-8-5'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 23,
            'month_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-6'),
            'date_to': fields.Date.from_string('2021-8-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1,
        }])
        
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': 5000000,
            },
            {
                'code': 'GROSS',
                'amount': 5000000,
            },
            {
                'code': 'NET',
                'amount': 5000000,
            }])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_12(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày dương
                TH3: Không có ngày nghỉ, trong nhiều tháng, Kiểu tính toán phiếu lương: giờ
        """
        # prepare data: lệch dương 5 ngày
        self.env.company.salary_cycle_id = self.salary_cycle_2
        self.contract_open_emp_A.write({'salary_computation_mode': 'hour_basis'})
        # lệch 5 ngày, nhiều tháng => 25/6/2021 - 5/8/2021
            # => 25/6/2021 - 5/7/2021  và  6/7/2021 - 5/8/2021
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-25'),
            fields.Date.from_string('2021-8-5'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 44,
            'calendar_working_hours': 352,
            'duty_working_days': 30,
            'duty_working_hours': 240,
            'worked_days': 30,
            'worked_hours': 240,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            # 6/6 -> 5/7: 21days - 168hours
            # 25/6 -> 5/7: 7days - 56hours
            'month_working_days': 21,
            'month_working_hours': 168,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 7,
            'worked_hours': 56,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 56 / 168
            },
            {
            # 6/7 -> 5/8: 23days - 184hours
            'month_working_days': 23,
            'month_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months[0].line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-6-6'),
            'date_to': fields.Date.from_string('2021-7-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 21,
            'calendar_working_hours': 168,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 7,
            'worked_hours': 56,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 56 / 168,
        }])
        working_months_lines = working_months[1].line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-6'),
            'date_to': fields.Date.from_string('2021-8-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1,
        }])
        
        payslip.compute_sheet()
        salary_lines = payslip.line_ids.filtered(lambda r:r.code in ['BASIC', 'GROSS', 'NET'])
        self.assertRecordValues(salary_lines, [
            {
                'code': 'BASIC',
                'amount': 6666666.67,  # 2 tháng
            },
            {
                'code': 'GROSS',
                'amount': 6666666.67,
            },
            {
                'code': 'NET',
                'amount': 6666666.67,
            }])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_13(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày dương
                TH4: Không có ngày nghỉ, trong nhiều tháng, Kiểu tính toán phiếu lương: ngày
        """
        # prepare data: lệch dương 5 ngày
        self.env.company.salary_cycle_id = self.salary_cycle_2
        self.contract_open_emp_A.write({'salary_computation_mode': 'day_basis'})
        # lệch 5 ngày, nhiều tháng => 25/6/2021 - 5/8/2021
            # => 25/6/2021 - 5/7/2021  và  6/7/2021 - 5/8/2021
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-25'),
            fields.Date.from_string('2021-8-5'),
            self.contract_open_emp_A.id)
        
            # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 44,
            'calendar_working_hours': 352,
            'duty_working_days': 30,
            'duty_working_hours': 240,
            'worked_days': 30,
            'worked_hours': 240,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            # 6/6 -> 5/7: 21days - 168hours
            # 25/6 -> 5/7: 7days - 56hours
            'month_working_days': 21,
            'month_working_hours': 168,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 7,
            'worked_hours': 56,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 7 / 21
            },
            {
            # 6/7 -> 5/8: 23days - 184hours
            'month_working_days': 23,
            'month_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months[0].line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-6-6'),
            'date_to': fields.Date.from_string('2021-7-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 21,
            'calendar_working_hours': 168,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 7,
            'worked_hours': 56,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 7 / 21,
        }])
        working_months_lines = working_months[1].line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-6'),
            'date_to': fields.Date.from_string('2021-8-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1,
        }])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_14(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày dương
                TH5: Có ngày nghỉ, trong 1 tháng, Kiểu tính toán phiếu lương: giờ
        """
        # prepare data: lệch 5 ngày
        self.env.company.salary_cycle_id = self.salary_cycle_2
        self.contract_open_emp_A.write({'salary_computation_mode': 'hour_basis'})
        
        # leave: 2.5 days - 20 hours
        # unpaid: 1.5 days - 12 hours
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-12h
            datetime.strptime('2021-7-6 6:00:00', DTF),
            datetime.strptime('2021-7-7 10:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 2',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-9 6:00:00', DTF),
            datetime.strptime('2021-7-9 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        
        # lệch dương 5 ngày => 6/7/2021 - 5/8/2021
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-6'),
            fields.Date.from_string('2021-8-5'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 23,
            'month_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 184 - 12
            'paid_rate': 172 / 184
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-6'),
            'date_to': fields.Date.from_string('2021-8-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 184 - 12
            'paid_rate': 172 / 184
        }])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_15(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày dương
                TH6: Có ngày nghỉ, trong 1 tháng, Kiểu tính toán phiếu lương: ngày
        """
        # prepare data: lệch 5 ngày
        self.env.company.salary_cycle_id = self.salary_cycle_2
        self.contract_open_emp_A.write({'salary_computation_mode': 'day_basis'})
             
        # leave: 2.5 days - 20 hours
        # unpaid: 1.5 days - 12 hours
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-12h
            datetime.strptime('2021-7-6 6:00:00', DTF),
            datetime.strptime('2021-7-7 10:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 2',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-9 6:00:00', DTF),
            datetime.strptime('2021-7-9 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        # lệch 5 ngày => 6/7/2021 - 5/8/2021
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-6'),
            fields.Date.from_string('2021-8-5'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 23,
            'month_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 23 - 1.5
            'paid_rate': 21.5 / 23
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-6'),
            'date_to': fields.Date.from_string('2021-8-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 23 - 1.5
            'paid_rate': 21.5 / 23
        }])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_16(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày dương
                TH7: Có ngày nghỉ, trong nhiều tháng, Kiểu tính toán phiếu lương: giờ
        """
        # prepare data: lệch 5 ngày
        self.env.company.salary_cycle_id = self.salary_cycle_2
        self.contract_open_emp_A.write({'salary_computation_mode': 'hour_basis'})
        # July
        # leave: 2.5 days - 20 hours
        # unpaid: 1.5 days - 12 hours
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-6 6:00:00', DTF),
            datetime.strptime('2021-7-7 10:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 2',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-9 6:00:00', DTF),
            datetime.strptime('2021-7-9 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        # June
        # leaves: 1.5 days - 12 hours
        # unpaid: 0.5 days - 4 hours
        hol3 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-6-28 6:00:00', DTF),
            datetime.strptime('2021-6-28 10:00:00', DTF))
        hol4 = self.create_holiday(
            'Test Unpaid Leave 2',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-6-29 6:00:00', DTF),
            datetime.strptime('2021-6-29 15:00:00', DTF))
        hol3.action_validate()
        hol4.action_validate()
        
        # lệch 5 ngày, nhiều tháng => 25/6/2021 - 5/8/2021
            # => 25/6/2021 - 5/7/2021  và  6/7/2021 - 5/8/2021
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-25'),
            fields.Date.from_string('2021-8-5'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 44,
            'calendar_working_hours': 352,
            'duty_working_days': 30,
            'duty_working_hours': 240,
            'worked_days': 26,
            'worked_hours': 208,
            'leave_days': 4,
            'leave_hours': 32,
            'unpaid_leave_days': 2,
            'unpaid_leave_hours': 16,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            # 6/6 -> 5/7: 21days - 168hours
            # 25/6 -> 5/7: 7days - 56hours
            'month_working_days': 21,
            'month_working_hours': 168,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 5.5,
            'worked_hours': 44,
            'leave_days': 1.5,
            'leave_hours': 12,
            'unpaid_leave_days': 0.5,
            'unpaid_leave_hours': 4,
            # 56 - 4
            'paid_rate': 52 / 168
            },
            {
            # 6/7 -> 5/8: 23days - 184hours
            'month_working_days': 23,
            'month_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 184 - 12
            'paid_rate': 172 / 184
        }])
        working_months_lines = working_months[0].line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-6-6'),
            'date_to': fields.Date.from_string('2021-7-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 21,
            'calendar_working_hours': 168,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 5.5,
            'worked_hours': 44,
            'leave_days': 1.5,
            'leave_hours': 12,
            'unpaid_leave_days': 0.5,
            'unpaid_leave_hours': 4,
            'paid_rate': 52 / 168,
        }])
        working_months_lines = working_months[1].line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-6'),
            'date_to': fields.Date.from_string('2021-8-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            'paid_rate': 172 / 184,
        }])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_17(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày dương
                TH8: Có ngày nghỉ, trong nhiều tháng, Kiểu tính toán phiếu lương: ngày
        """
        # prepare data: lệch 5 ngày
        self.env.company.salary_cycle_id = self.salary_cycle_2
        self.contract_open_emp_A.write({'salary_computation_mode': 'day_basis'})
             
        # July
        # leave: 2.5 days - 20 hours
        # unpaid: 1.5 days - 12 hours
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-12h
            datetime.strptime('2021-7-6 6:00:00', DTF),
            datetime.strptime('2021-7-7 10:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 2',
            self.product_emp_A.id,
            self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-9 6:00:00', DTF),
            datetime.strptime('2021-7-9 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        # June
        # leaves: 1.5 days - 12 hours
        # unpaid: 0.5 days - 4 hours
        hol3 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            self.unpaid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-6-28 6:00:00', DTF),
            datetime.strptime('2021-6-28 10:00:00', DTF))
        hol4 = self.create_holiday(
            'Test Unpaid Leave 2',
            self.product_emp_A.id, self.paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-6-29 6:00:00', DTF),
            datetime.strptime('2021-6-29 15:00:00', DTF))
        hol3.action_validate()
        hol4.action_validate()
        # lệch 5 ngày, nhiều tháng => 25/6/2021 - 5/8/2021
            # => 25/6/2021 - 5/7/2021  và  6/7/2021 - 5/8/2021 
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-25'),
            fields.Date.from_string('2021-8-5'),
            self.contract_open_emp_A.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 44,
            'calendar_working_hours': 352,
            'duty_working_days': 30,
            'duty_working_hours': 240,
            'worked_days': 26,
            'worked_hours': 208,
            'leave_days': 4,
            'leave_hours': 32,
            'unpaid_leave_days': 2,
            'unpaid_leave_hours': 16,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 2, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            # 6/6 -> 5/7: 21days - 168hours
            # 25/6 -> 5/7: 7days - 56hours
            'month_working_days': 21,
            'month_working_hours': 168,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 5.5,
            'worked_hours': 44,
            'leave_days': 1.5,
            'leave_hours': 12,
            'unpaid_leave_days': 0.5,
            'unpaid_leave_hours': 4,
            # 7 - 0.5
            'paid_rate': 6.5 / 21
            },
            {
            # 6/7 -> 5/8: 23days - 184hours
            'month_working_days': 23,
            'month_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 23 - 1.5
            'paid_rate': 21.5 / 23
        }])
        working_months_lines = working_months[0].line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-6-6'),
            'date_to': fields.Date.from_string('2021-7-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 21,
            'calendar_working_hours': 168,
            'duty_working_days': 7,
            'duty_working_hours': 56,
            'worked_days': 5.5,
            'worked_hours': 44,
            'leave_days': 1.5,
            'leave_hours': 12,
            'unpaid_leave_days': 0.5,
            'unpaid_leave_hours': 4,
            # 7 - 0.5
            'paid_rate': 6.5 / 21,
        }])
        working_months_lines = working_months[1].line_ids
        self.assertEqual(len(working_months_lines), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            'date_from': fields.Date.from_string('2021-7-6'),
            'date_to': fields.Date.from_string('2021-8-5'),
            'contract_id': self.contract_open_emp_A.id,
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 1.5,
            'unpaid_leave_hours': 12,
            # 23 - 1.5
            'paid_rate': 21.5 / 23,
        }])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_18(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày dương
                TH9: trong 1 tháng, có nhiều hợp đồng hợp lệ trong khoảng này
        """
        # prepare data: lệch 5 ngày
        self.env.company.salary_cycle_id = self.salary_cycle_2
        
        contract_1 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-6'),
            fields.Date.from_string('2021-7-15'),
            'open')
        contract_2 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-16'),
            fields.Date.from_string('2021-7-25'),
            'open')
        contract_3 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-26'),
            fields.Date.from_string('2021-8-5'),
            'open')
        # lệch 5 ngày => 6/7/2021 - 5/8/2021
        payslip = self.create_payslip(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-6'),
            fields.Date.from_string('2021-8-5'),
            contract_3.id)
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 23,
            'calendar_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertEqual(len(working_months), 1, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months, [{
            'month_working_days': 23,
            'month_working_hours': 184,
            'duty_working_days': 23,
            'duty_working_hours': 184,
            'worked_days': 23,
            'worked_hours': 184,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        working_months_lines = working_months.line_ids
        self.assertEqual(len(working_months_lines), 3, 'Test working_month_calendar_ids field not oke')
        self.assertRecordValues(working_months_lines, [{
            # 1/7 -> 10/7 : 7 days - 56 hours
            'date_from': fields.Date.from_string('2021-7-6'),
            'date_to': fields.Date.from_string('2021-7-15'),
            'contract_id': contract_1.id,
            'calendar_working_days': 8,
            'calendar_working_hours': 64,
            'duty_working_days': 8,
            'duty_working_hours': 64,
            'worked_days': 8,
            'worked_hours': 64,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 64 / 184
            },
            {
            # 11/7 -> 20/7 : 7 days - 56 hours
            'date_from': fields.Date.from_string('2021-7-16'),
            'date_to': fields.Date.from_string('2021-7-25'),
            'contract_id': contract_2.id,
            'calendar_working_days': 6,
            'calendar_working_hours': 48,
            'duty_working_days': 6,
            'duty_working_hours': 48,
            'worked_days': 6,
            'worked_hours': 48,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 48 / 184
            },
            {
            # 21/7 -> 31/7 : 8 days - 64 hours
            'date_from': fields.Date.from_string('2021-7-26'),
            'date_to': fields.Date.from_string('2021-8-5'),
            'contract_id': contract_3.id,
            'calendar_working_days': 9,
            'calendar_working_hours': 72,
            'duty_working_days': 9,
            'duty_working_hours': 72,
            'worked_days': 9,
            'worked_hours': 72,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 72 / 184
            },
        ])
    
    # 8. Phiếu lương
    def test_payslip_working_calendar_detail_19(self): 
        """
        8.2 Test Thông tin của phiếu lương
            Case 2C: Test Thông tin chi tiết của bảng "Chi tiết lịch làm việc" - Với chu kỳ lương lệch ngày âm
        """
        # TODO: Fix me when start_day_offset is negative

    def test_payslip_working_calendar_detail_20(self):
        """
        Test Thông tin của phiếu lương T4/2021
        Input: 
            Chu kỳ lương không lệch chuẩn
            Có 2 xin nghỉ có lương đã duyệt:
                Nghỉ 1: Từ 8h 31/3 -> 10h 1/4
                Nghỉ 2: Từ 10h 1/4 -> 17h 1/4
            Phiếu lương : từ 1/4 - 30/4
        Ouput:
            Thông tin nghỉ của phiếu lương: nghỉ 8h (1 ngày), ...
        """
        # UTC+2
        hol1 = self.create_holiday(
            'Leave 1',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-3-31 6:00:00', DTF),
            datetime.strptime('2021-4-1 8:00:00', DTF))
        hol2 = self.create_holiday(
            'Leave 2',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-4-1 8:00:00', DTF),
            datetime.strptime('2021-4-1 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-4-1'),
            fields.Date.from_string('2021-4-30'),
            self.contract_open_emp_A.id)
        payslip.compute_sheet()
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 21,
            'worked_hours': 168,
            'leave_days': 1,
            'leave_hours': 8,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertRecordValues(working_months, [{
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 21,
            'worked_hours': 168,
            'leave_days': 1,
            'leave_hours': 8,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        # Check working_month_calendar_line_ids
        self.assertRecordValues(working_months.line_ids, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 21,
            'worked_hours': 168,
            'leave_days': 1,
            'leave_hours': 8,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
    
    def test_payslip_working_calendar_detail_21(self):
        """
        Test Thông tin của phiếu lương T4/2021
        Input: 
            Chu kỳ lương không lệch chuẩn
            Có 2 xin nghỉ có lương đã duyệt:
                Nghỉ 1: Từ 8h 5/4 -> 10h 6/4
                Nghỉ 2: Từ 10h 6/4 -> 17h 6/4
            Phiếu lương : từ 1/4 - 30/4
        Ouput:
            Thông tin nghỉ của phiếu lương: nghỉ 16h (2 ngày), ...
        """
        # UTC+2
        hol1 = self.create_holiday(
            'Leave 1',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-4-5 6:00:00', DTF),
            datetime.strptime('2021-4-6 8:00:00', DTF))
        hol2 = self.create_holiday(
            'Leave 2',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-4-6 8:00:00', DTF),
            datetime.strptime('2021-4-6 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-4-1'),
            fields.Date.from_string('2021-4-30'),
            self.contract_open_emp_A.id)
        payslip.compute_sheet()
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 20,
            'worked_hours': 160,
            'leave_days': 2,
            'leave_hours': 16,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertRecordValues(working_months, [{
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 20,
            'worked_hours': 160,
            'leave_days': 2,
            'leave_hours': 16,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        # Check working_month_calendar_line_ids
        self.assertRecordValues(working_months.line_ids, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 20,
            'worked_hours': 160,
            'leave_days': 2,
            'leave_hours': 16,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
    
    def test_payslip_working_calendar_detail_22(self):
        """
        Test Thông tin của phiếu lương T4/2021
        Input: 
            Chu kỳ lương không lệch chuẩn
            Có 3 xin nghỉ có lương đã duyệt:
                Nghỉ 1: Từ 8h 5/4 -> 10h 6/4
                Nghỉ 2: Từ 10h 6/4 -> 15h 6/4
                Nghỉ 3: Từ 15h 6/4 -> 10h 7/4
            Phiếu lương : từ 1/4 - 30/4
        Ouput:
            Thông tin nghỉ của phiếu lương: nghỉ 20h (2.5 ngày), ...
        """
        # UTC+2
        hol1 = self.create_holiday(
            'Leave 1',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-4-5 6:00:00', DTF),
            datetime.strptime('2021-4-6 8:00:00', DTF))
        hol2 = self.create_holiday(
            'Leave 2',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-4-6 8:00:00', DTF),
            datetime.strptime('2021-4-6 11:00:00', DTF))
        hol3 = self.create_holiday(
            'Leave 3',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-4-6 11:00:00', DTF),
            datetime.strptime('2021-4-7 10:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        hol3.action_validate()
        
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-4-1'),
            fields.Date.from_string('2021-4-30'),
            self.contract_open_emp_A.id)
        payslip.compute_sheet()
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertRecordValues(working_months, [{
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        # Check working_month_calendar_line_ids
        self.assertRecordValues(working_months.line_ids, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 19.5,
            'worked_hours': 156,
            'leave_days': 2.5,
            'leave_hours': 20,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])

    def test_payslip_working_calendar_detail_23(self):
        """
        Test Thông tin của phiếu lương T4/2021
        Input: 
            Chu kỳ lương không lệch chuẩn
            Có 3 xin nghỉ có lương đã duyệt:
                Nghỉ 1: Từ 8h 5/4 -> 10h 6/4
                Nghỉ 2: Từ 10h 6/4 -> 15h 6/4
                Nghỉ 3: Từ 15h 6/4 -> 17h 6/4
            Phiếu lương : từ 1/4 - 30/4
        Ouput:
            Thông tin nghỉ của phiếu lương: nghỉ 16h (2 ngày), ...
        """
        # UTC+2
        hol1 = self.create_holiday(
            'Leave 1',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-4-5 6:00:00', DTF),
            datetime.strptime('2021-4-6 8:00:00', DTF))
        hol2 = self.create_holiday(
            'Leave 2',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-4-6 8:00:00', DTF),
            datetime.strptime('2021-4-6 13:00:00', DTF))
        hol3 = self.create_holiday(
            'Leave 3',
            self.product_emp_A.id, self.paid_type.id,
            datetime.strptime('2021-4-6 13:00:00', DTF),
            datetime.strptime('2021-4-6 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        hol3.action_validate()
        
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-4-1'),
            fields.Date.from_string('2021-4-30'),
            self.contract_open_emp_A.id)
        payslip.compute_sheet()
        
        # Check working & leaves
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 20,
            'worked_hours': 160,
            'leave_days': 2,
            'leave_hours': 16,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
        }])
        # Check working_month_calendar_ids
        working_months = payslip.working_month_calendar_ids
        self.assertRecordValues(working_months, [{
            'month_working_days': 22,
            'month_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 20,
            'worked_hours': 160,
            'leave_days': 2,
            'leave_hours': 16,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
        # Check working_month_calendar_line_ids
        self.assertRecordValues(working_months.line_ids, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 20,
            'worked_hours': 160,
            'leave_days': 2,
            'leave_hours': 16,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0,
            'paid_rate': 1
        }])
