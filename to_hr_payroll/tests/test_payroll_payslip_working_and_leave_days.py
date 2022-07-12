from datetime import datetime

from odoo import fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.tests import tagged

from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestPayrollPayslipWorkingAndLeaveDay(TestPayrollCommon):
    @classmethod
    def setUpClass(cls):
        super(TestPayrollPayslipWorkingAndLeaveDay, cls).setUpClass()
        LeaveType = cls.env['hr.leave.type']
        cls.unpaid_type = LeaveType.search([('company_id', '=', cls.env.company.id),('unpaid', '=', True)], limit=1)
        cls.paid_type = LeaveType.search(
            [('company_id', '=', cls.env.company.id),
             ('unpaid', '=', False),
             ('code', '=', 'PaidTimeOff')], limit=1)
        cls.paid_type.write({
            'allocation_type': 'no',
            'validity_start': fields.Date.to_date('2021-1-1')
        })

    # 8. Phiếu lương
    def test_payslip_working_days_global_leave(self):
        """
        Case 3: Test thông tin Thông tin Lịch làm việc và Tổng hợp nghỉ
            TH2: Có thiết lập ngày nghỉ toàn cục
                => Số ngày/giờ phải làm trong tháng trừ đi số ngày/giờ nghỉ toàn cục
        """
        # Case 8 / TH2
        RsLeave = self.env['resource.calendar.leaves']
        # 1 days - 8 hours
        RsLeave.create({
            'name': 'Test 1', 'holiday': True,
            # UTC + 2 => 8h-17h
            'date_from': datetime.strptime('2021-9-2 6:00:00', DTF),
            'date_to': datetime.strptime('2021-9-2 15:00:00', DTF),
            'calendar_id': self.contract_open_emp_A.resource_calendar_id.id
        })
        # 0.5 days - 4 hours
        RsLeave.create({
            'name': 'Test 2',
            # UTC + 2 => 8h-12h
            'date_from': datetime.strptime('2021-9-1 6:00:00', DTF),
            'date_to': datetime.strptime('2021-9-1 10:00:00', DTF),
            'calendar_id': self.contract_open_emp_A.resource_calendar_id.id
        })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-9-1'),
            fields.Date.from_string('2021-9-30'),
            self.contract_open_emp_A.id)

        # check
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 20.5,
            'calendar_working_hours': 164,
            'duty_working_days': 20.5,
            'duty_working_hours': 164,
            'worked_days': 20.5,
            'worked_hours': 164,
            'leave_days': 0,
            'leave_hours': 0,
            'unpaid_leave_days': 0,
            'unpaid_leave_hours': 0
        }])

    # 8. Phiếu lương
    def test_payslip_worked_and_working_and_leave_days_12(self):
        """
        Case 3: Test thông tin Thông tin Lịch làm việc và Tổng hợp nghỉ
            TH1: Không thiết lập ngày nghỉ toàn cục
                Output:
                    Giờ làm việc theo lịch = tổng "Số Giờ làm việc theo lịch trong tháng" trên Bảng Chi tiết lịch làm việc (không tính giờ nghỉ toàn cục)
                    Ngày làm việc theo lịch = tổng "Số ngày phải làm theo lịch trong tháng" trên Bảng lịch làm việc tháng (không tính ngày nghỉ toàn cục)
                    Số giờ phải làm việc = tổng "Số giờ phải  làm việc" trên Bảng lịch làm việc tháng
                    Số ngày phải  làm việc = tổng "Số ngày phải  làm việc" trên Bảng lịch làm việc tháng
                    Giờ đã làm việc = Số giờ phải làm - Tổng số giờ nghỉ
                    Ngày đã làm việc = Số ngày phải làm - Tổng số ngày nghỉ
                    Tổng số giờ nghỉ = tổng "Tổng số giờ nghỉ" trên Bảng lịch làm việc tháng
                    Tổng số ngày nghỉ = tổng "Tổng số ngày nghỉ" trên Bảng lịch làm việc tháng
                    Số giờ nghỉ không lương = tổng "Tổng số giờ nghỉ không lương" trên Bảng lịch làm việc tháng
                    Số ngày nghỉ không lương = tổng "Tổng số ngày nghỉ không lương" trên Bảng lịch làm việc tháng

                * Test với Case 4
        Case 4: Test thông tin Ngày đã làm việc (Chế độ debug)
            TH1: Nhân viên làm đầy đủ, không có lịch nghỉ
            TH2: Nhân viên có lịch nghỉ nằm ngoài khoảng thời gian xuất phiếu lương, trong hợp đồng
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)

        # Case 3 / TH1: Không thiết lập ngày nghỉ toàn cục
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

        # Case 4: Test thông tin Ngày đã làm việc (Chế độ debug)
        lines = payslip.worked_days_line_ids
        self.assertEqual(len(lines), 1, 'Test Worked Days (worked_days_line_ids field) not oke')
        self.assertRecordValues(lines, [{
            'code': 'WORK100',
            'contract_id': payslip.contract_id.id,
            'number_of_days': 22,
            'number_of_hours': 176
        }])

    # 8. Phiếu lương
    def test_payslip_worked_and_working_and_leave_days_3(self):
        """
        Case 3: Test thông tin Thông tin Lịch làm việc và Tổng hợp nghỉ
            TH1: Không thiết lập ngày nghỉ toàn cục
                * Test với Case 4
        Case 4: Test thông tin Ngày đã làm việc (Chế độ debug)
            TH3: Nhân viên có lịch nghỉ nhưng chưa được duyệt trong khoảng thời gian xuất phiếu lương, trong hợp đồng: nghỉ có lương, nghỉ không lương,...
        """
        LeaveType = self.env['hr.leave.type']
        unpaid_type_1 = LeaveType.search([('company_id', '=', self.env.company.id),('unpaid', '=', True)], limit=1)
        unpaid_type_2 = LeaveType.create({
            'name': 'Unpaid 2 ',
            'unpaid': True,
            'responsible_id': self.env.user.id
        })
        paid_type = LeaveType.search(
            [('company_id', '=', self.env.company.id),
             ('unpaid', '=', False),
             ('code', '=', 'PaidTimeOff')], limit=1)
        paid_type.write({
            'allocation_type': 'no',
            'validity_start': fields.Date.from_string('2021-7-1')
        })

        # leaves
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            unpaid_type_1.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-1 6:00:00', DTF),
            datetime.strptime('2021-7-2 15:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            unpaid_type_2.id,
            # UTC + 2 => 8h-12h
            datetime.strptime('2021-7-5 6:00:00', DTF),
            datetime.strptime('2021-7-5 10:00:00', DTF))

        hol3 = self.create_holiday(
            'Test Paid Leave 1',
            self.product_emp_A.id,
            paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-23 6:00:00', DTF),
            datetime.strptime('2021-7-23 15:00:00', DTF))

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)

        # Case 3 / TH1: Không thiết lập ngày nghỉ toàn cục
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

        # Case 4: Test thông tin Ngày đã làm việc (Chế độ debug)
        lines = payslip.worked_days_line_ids
        self.assertEqual(len(lines), 1, 'Test Worked Days (worked_days_line_ids field) not oke')
        self.assertRecordValues(lines, [{
            'code': 'WORK100',
            'contract_id': payslip.contract_id.id,
            'number_of_days': 22,
            'number_of_hours': 176
        }])

    # 8. Phiếu lương
    def test_payslip_worked_and_working_and_leave_days_4(self):
        """
        Case 3: Test thông tin Thông tin Lịch làm việc và Tổng hợp nghỉ
            TH1: Không thiết lập ngày nghỉ toàn cục
                * Test với Case 4
        Case 4: Test thông tin Ngày đã làm việc (Chế độ debug)
            TH4: Nhân viên có lịch nghỉ trong khoảng thời gian xuất phiếu lương, trong hợp đồng: nghỉ có lương, nghỉ không lương,...
        """
        LeaveType = self.env['hr.leave.type']
        unpaid_type_1 = LeaveType.search([('company_id', '=', self.env.company.id), ('unpaid', '=', True)], limit=1)
        unpaid_type_2 = LeaveType.create({
            'name': 'Unpaid 2 ',
            'unpaid': True,
            'responsible_id': self.env.user.id
        })
        paid_type = LeaveType.search(
            [('company_id', '=', self.env.company.id),
             ('unpaid', '=', False),
             ('code', '=', 'PaidTimeOff')], limit=1)
        paid_type.write({
            'allocation_type': 'no',
            'validity_start': fields.Date.from_string('2021-7-1')
        })

        # leaves
        hol1 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            unpaid_type_1.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-1 6:00:00', DTF),
            datetime.strptime('2021-7-2 15:00:00', DTF))
        hol2 = self.create_holiday(
            'Test Unpaid Leave 1',
            self.product_emp_A.id,
            unpaid_type_2.id,
            # # UTC + 2 => 8h-12h
            datetime.strptime('2021-7-5 6:00:00', DTF),
            datetime.strptime('2021-7-5 10:00:00', DTF))

        hol3 = self.create_holiday(
            'Test Paid Leave 1',
            self.product_emp_A.id, paid_type.id,
            # UTC + 2 => 8h-17h
            datetime.strptime('2021-7-23 6:00:00', DTF),
            datetime.strptime('2021-7-23 15:00:00', DTF))
        hol1.action_validate()
        hol2.action_validate()
        hol3.action_validate()

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)

        # Case 3 / TH1: Không thiết lập ngày nghỉ toàn cục
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 22,
            'calendar_working_hours': 176,
            'duty_working_days': 22,
            'duty_working_hours': 176,
            'worked_days': 18.5,
            'worked_hours': 148,
            'leave_days': 3.5,
            'leave_hours': 28,
            'unpaid_leave_days': 2.5,
            'unpaid_leave_hours': 20
        }])

        # Case 4: Test thông tin Ngày đã làm việc (Chế độ debug)
        lines = payslip.worked_days_line_ids
        self.assertEqual(len(lines), 4, 'Test Worked Days (worked_days_line_ids field) not oke')
        worked_line = lines.filtered(lambda r:r.code == 'WORK100')
        self.assertRecordValues(worked_line, [{
            'contract_id': payslip.contract_id.id,
            'number_of_days': 18.5,
            'number_of_hours': 148
        }])
        unpaid_1_line = lines.filtered(lambda r:r.code == 'Unpaid')
        self.assertRecordValues(unpaid_1_line, [{
            'contract_id': payslip.contract_id.id,
            'number_of_days': 2,
            'number_of_hours': 16
        }])
        unpaid_2_line = lines.filtered(lambda r:r.code == 'Unpaid2')
        self.assertRecordValues(unpaid_2_line, [{
            'contract_id': payslip.contract_id.id,
            'number_of_days': 0.5,
            'number_of_hours': 4
        }])
        paid_line = lines.filtered(lambda r:r.code == 'PaidTimeOff')
        self.assertRecordValues(paid_line, [{
            'contract_id': payslip.contract_id.id,
            'number_of_days': 1,
            'number_of_hours': 8
        }])

    def test_payslip_worked_days_with_calendar_44h_1(self):
        """
        Test nghỉ vắt ngày vào thứ 7
        Lịch làm việc 44h/tuần (sáng t7 làm từ 8h->12h), không thiết lập nghỉ toàn cục
        Kiểu nghỉ Không lương - theo ngày

        Input:
            Nghỉ 1: nghỉ không lương từ 1/1/2022 đến 3/1/2022 (Thứ 7 -> Thứ 2)
        Output:
            Nghỉ không lương: 2 days - 12 hours
        """
        # Contract
        self.contract_employee_44h.salary_computation_mode = 'day_basis'
        self.contract_employee_44h.action_start_contract()
        # leaves # UTC+1
        hol1 = self.create_holiday(
            'Unpaid Leave 01/01/2022 -> 01/03/2022 ',
            self.employee_44h.id,
            self.unpaid_type.id,
            fields.Datetime.to_datetime('2022-01-01 07:00:00'),
            fields.Datetime.to_datetime('2022-01-03 16:00:00'))
        hol1.action_validate()
        # payslip
        payslip = self.create_payslip(
            self.employee_44h.id,
            fields.Date.to_date('2022-1-1'),
            fields.Date.to_date('2022-1-31'),
            self.contract_employee_44h.id)
        payslip.compute_sheet()

        # check
        # payslip
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 26,
            'calendar_working_hours': 188,
            'duty_working_days': 26,
            'duty_working_hours': 188,
            'worked_days': 24,
            'worked_hours': 176,
            'leave_days': 2,
            'leave_hours': 12,
            'unpaid_leave_days': 2,
            'unpaid_leave_hours': 12
        }])
        # worked days
        self.assertRecordValues(payslip.worked_days_line_ids,
            [{
                'code': 'WORK100',
                'number_of_days': 24,
                'number_of_hours': 176
            },
            {
                'code': self.unpaid_type.code,
                'number_of_days': 2,
                'number_of_hours': 12
            }])

    def test_payslip_worked_days_with_calendar_44h_2(self):
        """
        Test nghỉ vắt ngày vào thứ 7
        Lịch làm việc 44h/tuần (sáng t7 làm từ 8h->12h), không thiết lập nghỉ toàn cục
        Kiểu nghỉ Không lương - theo ngày

        Input:
            Nghỉ 1: nghỉ không lương từ 7/1/2022 đến 10/1/2022 (Thứ 6 -> Thứ 2)
        Output:
            Nghỉ không lương: 3 days - 18 hours
        """
        # Contract
        self.contract_employee_44h.salary_computation_mode = 'day_basis'
        self.contract_employee_44h.action_start_contract()
        # leaves # UTC+1
        hol1 = self.create_holiday(
            'Unpaid Leave 07/01/2022 -> 10/01/2022 ',
            self.employee_44h.id,
            self.unpaid_type.id,
            fields.Datetime.to_datetime('2022-01-07 07:00:00'),
            fields.Datetime.to_datetime('2022-01-10 16:00:00'))
        hol1.action_validate()
        # payslip
        payslip = self.create_payslip(
            self.employee_44h.id,
            fields.Date.to_date('2022-1-1'),
            fields.Date.to_date('2022-1-31'),
            self.contract_employee_44h.id)
        payslip.compute_sheet()

        # check
        # payslip
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 26,
            'calendar_working_hours': 188,
            'duty_working_days': 26,
            'duty_working_hours': 188,
            'worked_days': 23,
            'worked_hours': 168,
            'leave_days': 3,
            'leave_hours': 20,
            'unpaid_leave_days': 3,
            'unpaid_leave_hours': 20
        }])
        # worked days
        self.assertRecordValues(payslip.worked_days_line_ids,
            [{
                'code': 'WORK100',
                'number_of_days': 23,
                'number_of_hours': 168
            },
            {
                'code': self.unpaid_type.code,
                'number_of_days': 3,
                'number_of_hours': 20
            }])

    def test_payslip_worked_days_with_calendar_44h_3(self):
        """
        Test nghỉ vắt ngày vào thứ 7
        Lịch làm việc 44h/tuần (sáng t7 làm từ 8h->12h), không thiết lập nghỉ toàn cục
        Kiểu nghỉ Không lương - theo ngày

        Input:
            Nghỉ 1: nghỉ không lương từ 28/1/2022 đến 31/1/2022 (Thứ 6 -> Thứ 2)
        Output:
            Nghỉ không lương: 3 days - 18 hours
        """
        # Contract
        self.contract_employee_44h.salary_computation_mode = 'day_basis'
        self.contract_employee_44h.action_start_contract()
        # leaves # UTC+1
        hol1 = self.create_holiday(
            'Unpaid Leave 28/01/2022 -> 31/01/2022 ',
            self.employee_44h.id,
            self.unpaid_type.id,
            fields.Datetime.to_datetime('2022-01-28 07:00:00'),
            fields.Datetime.to_datetime('2022-01-31 16:00:00'))
        hol1.action_validate()
        # payslip
        payslip = self.create_payslip(
            self.employee_44h.id,
            fields.Date.to_date('2022-1-1'),
            fields.Date.to_date('2022-1-31'),
            self.contract_employee_44h.id)
        payslip.compute_sheet()

        # check
        # payslip
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 26,
            'calendar_working_hours': 188,
            'duty_working_days': 26,
            'duty_working_hours': 188,
            'worked_days': 23,
            'worked_hours': 168,
            'leave_days': 3,
            'leave_hours': 20,
            'unpaid_leave_days': 3,
            'unpaid_leave_hours': 20
        }])
        # worked days
        self.assertRecordValues(payslip.worked_days_line_ids,
            [{
                'code': 'WORK100',
                'number_of_days': 23,
                'number_of_hours': 168
            },
            {
                'code': self.unpaid_type.code,
                'number_of_days': 3,
                'number_of_hours': 20
            }])

    def test_payslip_worked_days_with_calendar_44h_4(self):
        """
        Test nghỉ vắt ngày vào thứ 7, vắt tháng
        Lịch làm việc 44h/tuần (sáng t7 làm từ 8h->12h), không thiết lập nghỉ toàn cục
        Kiểu nghỉ Không lương - theo ngày

        Input:
            Nghỉ 1: nghỉ không lương từ 28/1/2022 đến 1/2/2022 (Thứ 6 -> Thứ 3 (vắt sang tháng 2))
        Output:
            Nghỉ không lương: 3 days - 18 hours
        """
        # Contract
        self.contract_employee_44h.salary_computation_mode = 'day_basis'
        self.contract_employee_44h.action_start_contract()
        # leaves # UTC+1
        hol1 = self.create_holiday(
            'Unpaid Leave 28/01/2022 -> 01/02/2022 ',
            self.employee_44h.id,
            self.unpaid_type.id,
            fields.Datetime.to_datetime('2022-01-28 07:00:00'),
            fields.Datetime.to_datetime('2022-02-01 16:00:00'))
        hol1.action_validate()
        # payslip
        payslip = self.create_payslip(
            self.employee_44h.id,
            fields.Date.to_date('2022-1-1'),
            fields.Date.to_date('2022-1-31'),
            self.contract_employee_44h.id)
        payslip.compute_sheet()

        # check
        # payslip
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 26,
            'calendar_working_hours': 188,
            'duty_working_days': 26,
            'duty_working_hours': 188,
            'worked_days': 23,
            'worked_hours': 168,
            'leave_days': 3,
            'leave_hours': 20,
            'unpaid_leave_days': 3,
            'unpaid_leave_hours': 20
        }])
        # worked days
        self.assertRecordValues(payslip.worked_days_line_ids,
            [{
                'code': 'WORK100',
                'number_of_days': 23,
                'number_of_hours': 168
            },
            {
                'code': self.unpaid_type.code,
                'number_of_days': 3,
                'number_of_hours': 20
            }])

    def test_payslip_worked_days_with_calendar_44h_5(self):
        """
        Test nghỉ vắt ngày vào thứ 7
        Lịch làm việc 44h/tuần (sáng t7 làm từ 8h->12h), không thiết lập nghỉ toàn cục
        Kiểu nghỉ Không lương - theo ngày
        kiểu nghỉ có lương - theo ngày
        Input:
            Nghỉ 1: nghỉ có lương từ 1/1/2022 đến 3/1/2022 (Thứ 6 -> Thứ 2)
            Nghỉ 2: nghỉ không lương từ 10/1/2022 đến 13/1/2022 (thứ 2 -> thứ 5)
            Nghỉ 2: nghỉ không lương từ 17/1/2022 đến 22/1/2022 (thứ 2 -> thứ 7)
            Nghỉ 4: nghỉ có lương từ 29/1/2022 đến 31/1/2022 (Thứ 6 -> Thứ 2)
        Output:
            Nghỉ không lương: 10 days - 76 hours
            Nghỉ có lương: 4 days - 24 hours
        """
        # Contract
        self.contract_employee_44h.salary_computation_mode = 'day_basis'
        self.contract_employee_44h.action_start_contract()
        # leaves # UTC+1
        hol1 = self.create_holiday(
            'Unpaid Leave 01/01/2022 -> 03/01/2022 ',
            self.employee_44h.id,
            self.paid_type.id,
            fields.Datetime.to_datetime('2022-01-01 07:00:00'),
            fields.Datetime.to_datetime('2022-01-03 16:00:00'))
        hol2 = self.create_holiday(
            'Unpaid Leave 10/01/2022 -> 13/01/2022 ',
            self.employee_44h.id,
            self.unpaid_type.id,
            fields.Datetime.to_datetime('2022-01-10 07:00:00'),
            fields.Datetime.to_datetime('2022-01-13 16:00:00'))
        hol3 = self.create_holiday(
            'Unpaid Leave 17/01/2022 -> 22/01/2022 ',
            self.employee_44h.id,
            self.unpaid_type.id,
            fields.Datetime.to_datetime('2022-01-17 07:00:00'),
            fields.Datetime.to_datetime('2022-01-22 16:00:00'))
        hol4 = self.create_holiday(
            'Unpaid Leave 29/01/2022 -> 31/01/2022 ',
            self.employee_44h.id,
            self.paid_type.id,
            fields.Datetime.to_datetime('2022-01-29 07:00:00'),
            fields.Datetime.to_datetime('2022-01-31 16:00:00'))
        hol1.action_validate()
        hol2.action_validate()
        hol3.action_validate()
        hol4.action_validate()
        # payslip
        payslip = self.create_payslip(
            self.employee_44h.id,
            fields.Date.to_date('2022-1-1'),
            fields.Date.to_date('2022-1-31'),
            self.contract_employee_44h.id)
        payslip.compute_sheet()

        # check
        # payslip
        self.assertRecordValues(payslip, [{
            'calendar_working_days': 26,
            'calendar_working_hours': 188,
            'duty_working_days': 26,
            'duty_working_hours': 188,
            'worked_days': 12,
            'worked_hours': 88,
            'leave_days': 14,
            'leave_hours': 100,
            'unpaid_leave_days': 10,
            'unpaid_leave_hours': 76
        }])
        # worked days
        self.assertRecordValues(payslip.worked_days_line_ids,
            [{
                'code': 'WORK100',
                'number_of_days': 12,
                'number_of_hours': 88
            },
            {
                'code': self.paid_type.code,
                'number_of_days': 4,
                'number_of_hours': 24
            },
            {
                'code': self.unpaid_type.code,
                'number_of_days': 10,
                'number_of_hours': 76
            }])
