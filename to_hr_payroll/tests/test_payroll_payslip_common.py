from psycopg2 import IntegrityError
from unittest.mock import patch
from odoo import fields
from odoo.exceptions import ValidationError, UserError
from odoo.tests import Form
from odoo.tools import mute_logger
from odoo.tests import tagged
from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestPayrollPayslip(TestPayrollCommon):

    # 4. Form Phiếu Lương
    def test_form_payslip_date_from(self):
        """
        Case 2: Test chọn lại ngày bắt đầu của phiếu lương
            => Ngày kết thúc thay đổi thành ngày tương ứng của tháng sau nhưng trừ đi 1 ngày.
        """
        f = Form(self.env['hr.payslip'])
        f.date_from = fields.Date.from_string('2021-07-01')
        self.assertEqual(fields.Date.from_string('2021-07-31'), f.date_to, 'Test default date from, date to not oke')

        f.date_from = fields.Date.from_string('2021-06-01')
        self.assertEqual(fields.Date.from_string('2021-06-30'), f.date_to, 'Test default date from, date to not oke')

    # 4. Form Phiếu Lương
    def test_form_payslip_cycle(self):
        """
        Case 12: Test trường Chu kỳ lương
            Output: Trường Chu kỳ lương hiển thị đúng theo Chu kỳ lương được thiết lập trên công ty
        """
        salalry_cycle_1 = self.env['hr.salary.cycle'].search([], limit=1)
        salalry_cycle_2 = self.env['hr.salary.cycle'].create({'name': 'Slalary Cycle 2'})

        self.env.company.write({'salary_cycle_id': salalry_cycle_2.id})
        f = Form(self.env['hr.payslip'])
        self.assertEqual(f.salary_cycle_id, salalry_cycle_2, 'Test default salary_cycle_id field not oke')

        self.env.company.write({'salary_cycle_id': salalry_cycle_1.id})
        f = Form(self.env['hr.payslip'])
        self.assertEqual(f.salary_cycle_id, salalry_cycle_1, 'Test default salary_cycle_id field not oke')

    # 4. Form Phiếu Lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-4'))
    def test_form_payslip_default_date_1(self):
        """
        Case 1: Mặc định ngày bắt đầu, ngày kết thúc khi mở form phiếu lương
            Case 1.1: Test Ngày bắt đầu và kết thúc mặc định, chu kỳ lương không lệch chuẩn
                Output: hiển thị ngày bắt đầu và kết thúc phải ứng với ngày bắt đầu và kết thúc của tháng hiện hành

        """
        f = Form(self.env['hr.payslip'])
        self.assertEqual(
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string(f.date_from),
            'Test default date from not oke')
        self.assertEqual(
            fields.Date.from_string('2021-7-31'),
            fields.Date.from_string(f.date_to),
            'Test default date from not oke')

    # 4. Form Phiếu Lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-4'))
    def test_form_payslip_default_date_3(self):
        """
        Case 1: Mặc định ngày bắt đầu, ngày kết thúc khi mở form phiếu lương
            Case 1.3: Test Ngày bắt đầu và kết thúc mặc định, chu kỳ lương không lệch chuẩn, đánh dấu lương tháng 13
                Output: hiển thị ngày bắt đầu và kết thúc phải ứng với ngày bắt đầu và kết thúc của năm hiện hành
        """
        f = Form(self.env['hr.payslip'])
        f.thirteen_month_pay = True
        self.assertEqual(
            fields.Date.from_string('2020-1-1'),
            fields.Date.from_string(f.date_from),
            'Test default date from not oke')
        self.assertEqual(
            fields.Date.from_string('2020-12-31'),
            fields.Date.from_string(f.date_to),
            'Test default date from not oke')
        self.assertEqual(f.thirteen_month_pay_year, 2020, 'Test default thirteen_month_pay_year to not oke')

    # 4. Form Phiếu Lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-4'))
    def test_form_payslip_default_date_2B(self):
        """
        Case 1: Mặc định ngày bắt đầu, ngày kết thúc khi mở form phiếu lương
            Case 1.2: Test Ngày bắt đầu và kết thúc mặc định, chu kỳ lương có lệch chuẩn
                        * ngày hiện tại < ngày bắt đầu (đã cộng ngày lệch chuẩn) (4/7 < 6/7)
                TH1: ngày = 5, tháng = 0
                TH2: ngày = -5, tháng = 0
                TH3: ngày = 5, tháng = 1
                TH4: ngày = 5, tháng = -1
        """
        # TH1: Lệch: ngày = 5, tháng = 0
        self.env.company.salary_cycle_id.write({
            'start_day_offset': 5,
            'start_month_offset':0
        })
        f = Form(self.env['hr.payslip'])
        self.assertEqual(
            fields.Date.from_string('2021-6-6'),
            fields.Date.from_string(f.date_from),
            'Test default date from, date to not oke')
        self.assertEqual(
            fields.Date.from_string('2021-7-5'),
            fields.Date.from_string(f.date_to),
            'Test default date from, date to not oke')

        # TH2: Lệch: ngày = -5, tháng = 0
        self.env.company.salary_cycle_id.write({
            'start_day_offset': -5,
        })
        f = Form(self.env['hr.payslip'])
        self.assertEqual(
            fields.Date.from_string('2021-6-26'),
            fields.Date.from_string(f.date_from),
            'Test default date from, date to not oke')
        self.assertEqual(
            fields.Date.from_string('2021-7-25'),
            fields.Date.from_string(f.date_to),
            'Test default date from, date to not oke')

        #  TH3: Lệch: ngày = 5, tháng = 1
        self.env.company.salary_cycle_id.write({
            'start_day_offset': 5,
            'start_month_offset':1
        })
        f= Form(self.env['hr.payslip'])
        self.assertEqual(
            fields.Date.from_string('2021-7-6'),
            fields.Date.from_string(f.date_from),
            'Test default date from, date to not oke')
        self.assertEqual(
            fields.Date.from_string('2021-8-5'),
            fields.Date.from_string(f.date_to),
            'Test default date from, date to not oke')

        # TH4: Lệch: ngày = 5, tháng = -1
        self.env.company.salary_cycle_id.write({
            'start_day_offset': 5,
            'start_month_offset':-1
        })
        f= Form(self.env['hr.payslip'])
        self.assertEqual(
            fields.Date.from_string('2021-5-6'),
            fields.Date.from_string(f.date_from),
            'Test default date from, date to not oke')
        self.assertEqual(
            fields.Date.from_string('2021-6-5'),
            fields.Date.from_string(f.date_to),
            'Test default date from, date to not oke')

    # 4. Form Phiếu Lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-7'))
    def test_form_payslip_default_date_2A(self):
        """
        Case 1: Mặc định ngày bắt đầu, ngày kết thúc khi mở form phiếu lương
            Case 1.2: Test Ngày bắt đầu và kết thúc mặc định, chu kỳ lương có lệch chuẩn
                    * ngày hiện tại > ngày bắt đầu (đã cộng ngày lệch chuẩn) (7/7 > 6/7)
                TH1: ngày = 5, tháng = 0
                TH2: ngày = -5, tháng = 0
                TH3: ngày = 5, tháng = 1
                TH4: ngày = 5, tháng = -1
        """
        # TH1: Lệch: ngày = 5, tháng = 0
        self.env.company.salary_cycle_id.write({
            'start_day_offset': 5,
            'start_month_offset':0
        })
        f = Form(self.env['hr.payslip'])
        self.assertEqual(
            fields.Date.from_string('2021-7-6'),
            fields.Date.from_string(f.date_from),
            'Test default date from, date to not oke')
        self.assertEqual(
            fields.Date.from_string('2021-8-5'),
            fields.Date.from_string(f.date_to),
            'Test default date from, date to not oke')

        # TH2: Lệch: ngày = -5, tháng = 0
        self.env.company.salary_cycle_id.write({
            'start_day_offset': -5,
        })
        f = Form(self.env['hr.payslip'])
        self.assertEqual(
            fields.Date.from_string('2021-6-26'),
            fields.Date.from_string(f.date_from),
            'Test default date from, date to not oke')
        self.assertEqual(
            fields.Date.from_string('2021-7-25'),
            fields.Date.from_string(f.date_to),
            'Test default date from, date to not oke')

        #  TH3: Lệch: ngày = 5, tháng = 1
        self.env.company.salary_cycle_id.write({
            'start_day_offset': 5,
            'start_month_offset':1
        })
        f= Form(self.env['hr.payslip'])
        self.assertEqual(
            fields.Date.from_string('2021-8-6'),
            fields.Date.from_string(f.date_from),
            'Test default date from, date to not oke')
        self.assertEqual(
            fields.Date.from_string('2021-9-5'),
            fields.Date.from_string(f.date_to),
            'Test default date from, date to not oke')

        # TH4: Lệch: ngày = 5, tháng = -1
        self.env.company.salary_cycle_id.write({
            'start_day_offset': 5,
            'start_month_offset':-1
        })
        f= Form(self.env['hr.payslip'])
        self.assertEqual(
            fields.Date.from_string('2021-6-6'),
            fields.Date.from_string(f.date_from),
            'Test default date from, date to not oke')
        self.assertEqual(
            fields.Date.from_string('2021-7-5'),
            fields.Date.from_string(f.date_to),
            'Test default date from, date to not oke')

    # 4. Form Phiếu Lương
    @patch.object(fields.Date, 'today', lambda: fields.Date.from_string('2021-7-4'))
    def test_form_payslip_default_date_4(self):
        """
        Case 1: Mặc định ngày bắt đầu, ngày kết thúc khi mở form phiếu lương
            Case 1.4: Test Ngày bắt đầu và kết thúc mặc định, chu kỳ lương có lệch chuẩn, đánh dấu lương tháng 13
                TH1: ngày = 5, tháng = -1
                    => 6/12/2019 - 5/12/2020
        """
        self.env.company.salary_cycle_id.write({
            'start_day_offset': 5,
            'start_month_offset': -1
        })
        f = Form(self.env['hr.payslip'])
        f.thirteen_month_pay = True
        self.assertEqual(
            fields.Date.from_string(f.date_from),
            fields.Date.from_string('2019-12-6'),
            'Test default date from, date to not oke')
        self.assertEqual(
            fields.Date.from_string(f.date_to),
            fields.Date.from_string('2020-12-5'),
            'Test default date from, date to not oke')
        self.assertEqual(f.thirteen_month_pay_year, 2020, 'Test default thirteen_month_pay_year to not oke')

    # 4. Form Phiếu Lương
    def test_payslip_name_1(self):
        """
        Case 14: Test trường Tên phiếu lương khi thay đổi Chu kỳ (Từ ngày - Đến ngày)
            Output: "Đến ngày" rơi vào tháng nào thì Tên phiếu lương thay đổi bằng tháng đó.
        """
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)

        self.assertEqual(payslip_1.name, 'Salary Slip of Product Employee 1 for July-2021', 'Test name field not oke')
        payslip_1.write({
            'date_from': fields.Date.from_string('2021-5-1'),
            'date_to': fields.Date.from_string('2021-6-30')
        })
        self.assertEqual(payslip_1.name, 'Salary Slip of Product Employee 1 for June-2021', 'Test name field not oke')

    # 4. Form Phiếu Lương
    def test_payslip_name_2(self):
        """
        Case 13: Test trường Tên phiếu lương khi thay đổi Nhân viên
            Output: Tên phiếu lương thay đổi theo tên của nhân viên mới được chọn
        """
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-12-31'), 'open')
        payslip_1.write({
            'employee_id': self.product_dep_manager.id,
            'date_from': fields.Date.from_string('2021-5-1'),
            'date_to': fields.Date.from_string('2021-6-30')
            })

        self.assertEqual(payslip_1.name, 'Salary Slip of Product Department Manager for June-2021', 'Test name field not oke')

    # 4. Form Phiếu Lương
    def test_payslip_name_3(self):
        """
        Case 15: Tên phiếu lương khi phiếu lương đánh dấu lương tháng 13
        """
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        payslip_1.write({
            'thirteen_month_pay': True,
            'thirteen_month_pay_year': 2020
        })
        self.assertEqual(payslip_1.name, '13th-Month Salary of Product Employee 1 for the year 2020', 'Test name field not oke')

    @mute_logger('odoo.sql_db')
    def test_payslip_contract_1(self):
        """
        Case 3: Test trường "Hợp đồng" khi thay đổi Nhân viên / khoảng thời gian chu kỳ lương
            TH 1: Nhân viên không có hợp đồng nào ở trạng thái "Đang chạy" / "Hết hạn"
                => Output: Không có hợp đồng / lưu không thành công
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        with self.assertRaises(IntegrityError):
                payslip.write({'employee_id': self.product_dep_manager})

#     @mute_logger('odoo.sql_db')
#     def test_payslip_contract_2(self): ???
#         """
#         Case 3: Test trường "Hợp đồng" khi thay đổi Nhân viên / khoảng thời gian chu kỳ lương
#             TH 2: nhân viên có hợp đồng ở trạng thái "Đang chạy" / "Hết hạn",
#                     Thời gian bắt đầu / Kết thúc không hợp lệ với thời gian trên phiếu lương phiếu lương
#         """
#         payslip = self.create_payslip(self.product_emp_A.id,
#                                       fields.Date.from_string('2021-7-1'),
#                                       fields.Date.from_string('2021-7-31'),
#                                       self.contract_open_emp_A.id)
#         with self.assertRaises(IntegrityError):
#         payslip.write({
#                     'date_from': fields.Date.from_string('2019-12-1'),
#                     'date_to': fields.Date.from_string('2019-12-31')
#                     })

    def test_payslip_contract_3(self):
        """
        Case 3: Test trường "Hợp đồng" khi thay đổi Nhân viên / khoảng thời gian chu kỳ lương
            TH 3: nhân viên có hợp đồng ở trạng thái "Đang chạy" / "Hết hạn",
                Thời gian bắt đầu / Kết thúc không hợp lệ với thời gian trên phiếu lương phiếu lương

                => Output: Hợp đồng được điền tự động trên phiếu lương / lưu thành công
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        payslip.write({
            'date_from': fields.Date.from_string('2020-12-1'),
            'date_to': fields.Date.from_string('2020-12-31')
        })
        self.assertEqual(payslip.contract_id, self.contract_close_emp_A, 'Test compute contract not oke')

        # change employee
        new_contract = self.create_contract(self.product_dep_manager.id, fields.Date.from_string('2019-1-1'))
        payslip.write({
            'employee_id': self.product_dep_manager.id
        })
        self.assertEqual(payslip.contract_id, new_contract, 'Test compute contract not oke')

    def test_payslip_contract_4(self):
        """
        Case 3: Test trường "Hợp đồng" khi thay đổi Nhân viên / khoảng thời gian chu kỳ lương
            TH 4: Nhân viên có nhiều hợp đồng ở trạng thái "Đang chạy" / "Hết hạn",
                    Thời gian bắt đầu / Kết thúc hợp lệ với thời gian trên phiếu lương phiếu lương

                Output: lưu thành công:
                    Hợp đồng có ngày bắt đầu muộn nhất tính trong khoảng thời gian bắt đầu - kết thúc phiếu lương được điền tự động trên phiếu lương
        """
        contract_1 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-10'), 'close')
        contract_2 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-21'),
            fields.Date.from_string('2021-7-31'), 'open')
        contract_3 = self.create_contract(
            self.product_dep_manager.id,
            fields.Date.from_string('2021-7-11'),
            fields.Date.from_string('2021-7-20'), 'open')
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)

        payslip.write({'employee_id': self.product_dep_manager.id})
        self.assertEqual(payslip.contract_id, contract_2, 'Test compute contract not oke')
        self.assertIn(contract_1, payslip.contract_ids, 'Test compute contract not oke')
        self.assertIn(contract_3, payslip.contract_ids, 'Test compute contract not oke')

    def test_salary_structure_1(self):
        """
        Case 4: Test trường "Cấu trúc lương" thay đổi khi thay đổi hợp đồng / đánh dấu Lương tháng 13
            TH 1: Không đánh dấu "Lương tháng 13", có hợp đồng
                => Cấu trúc lương tháng 13 trên hợp đồng
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        self.assertEqual(payslip.struct_id, self.contract_open_emp_A.struct_id, 'Test compute salary structure not oke')

    def test_salary_structure_2(self):
        """
        Case 4: Test trường "Cấu trúc lương" thay đổi khi thay đổi hợp đồng / đánh dấu Lương tháng 13
            TH 2: Đánh dấu "Lương tháng 13", có hợp đồng, hợp đồng không có cấu trúc lương tháng 13
                => Cấu trúc lương tháng 13 trên hợp đồng
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-12-31'),
            self.contract_open_emp_A.id,
            thirteen_month_pay=True)
        self.assertEqual(payslip.struct_id, self.contract_open_emp_A.struct_id, 'Test compute salary structure not oke')

    def test_salary_structure_3(self):
        """
        Case 4: Test trường "Cấu trúc lương" thay đổi khi thay đổi hợp đồng / đánh dấu Lương tháng 13
            TH 3: Đánh dấu "Lương tháng 13", có hợp đồng, hợp đồng có cấu trúc lương tháng 13
                => Cấu trúc lương tháng 13 trên hợp đồng
        """
        struct_13th = self.structure_base.copy()
        self.contract_open_emp_A.write({
            'thirteen_month_struct_id': struct_13th.id
        })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-12-31'),
            self.contract_open_emp_A.id,
            thirteen_month_pay=True)
        self.assertEqual(payslip.struct_id, struct_13th, 'Test compute salary structure not oke')

    # 8. Phiếu lương
    def test_payslip_date_for_13th_month_1(self):
        """
        Case 7: Test ngày bắt đầu, ngày kết thúc khi đánh dấu lương tháng 13
            Input: Điền số năm vào Năm tính lương tháng 13
                TH1: Chu kỳ lương không lệch chuẩn
                    Output: Chu kỳ phiếu lương tự động điền ngày từ đầu năm đến cuối năm
        """
        f = Form(self.env['hr.payslip'])
        f.employee_id = self.product_dep_manager
        f.thirteen_month_pay = True
        f.thirteen_month_pay_year = 2020
        self.assertEqual(fields.Date.from_string('2020-1-1'), f.date_from, 'Test date from & date to with 13th month salary not oke')
        self.assertEqual(fields.Date.from_string('2020-12-31'), f.date_to, 'Test date from & date to with 13th month salary not oke')

    # 8. Phiếu lương
    def test_payslip_date_for_13th_month_2(self):
        """
        Case 7: Test ngày bắt đầu, ngày kết thúc khi đánh dấu lương tháng 13
            Input: Điền số năm vào Năm tính lương tháng 13
                TH2: Chu kỳ lương có lệch chuẩn, lệch 5 ngày
                    Output: Chu kỳ phiếu lương lương có lệch chuẩn, lệch 5 ngày
        """
        cycle_salary = self.env['hr.salary.cycle'].search([], limit=1)
        cycle_salary.write({'start_day_offset': 5})

        f = Form(self.env['hr.payslip'])
        f.employee_id = self.product_dep_manager
        f.thirteen_month_pay = True
        f.thirteen_month_pay_year = 2019
        self.assertEqual(fields.Date.from_string('2019-1-6'), f.date_from, 'Test date from & date to with 13th month salary not oke')
        self.assertEqual(fields.Date.from_string('2020-1-5'), f.date_to, 'Test date from & date to with 13th month salary not oke')

    # 8. Phiếu lương
    def test_payslip_date_for_13th_month_3(self):
        """
        Case 7: Test ngày bắt đầu, ngày kết thúc khi đánh dấu lương tháng 13
            Input: Điền số năm vào Năm tính lương tháng 13
                TH3: chu kỳ lương có lệch chuẩn, lệch -5 ngày
                    Output: Chu kỳ phiếu lương lương có lệch chuẩn, lệch -5 ngày
        """
        cycle_salary = self.env['hr.salary.cycle'].search([], limit=1)
        cycle_salary.write({'start_day_offset': -5})

        f = Form(self.env['hr.payslip'])
        f.employee_id = self.product_dep_manager
        f.thirteen_month_pay = True
        f.thirteen_month_pay_year = 2020
        self.assertEqual(fields.Date.from_string('2019-12-27'), f.date_from, 'Test date from & date to with 13th month salary not oke')
        self.assertEqual(fields.Date.from_string('2020-12-26'), f.date_to, 'Test date from & date to with 13th month salary not oke')

    # 8. Phiếu lương
    def test_payslip_date_from_date_to(self):
        """
        8.1. Test ngày bắt đầu, ngày kết thúc, trùng lặp, nhân bản...
            Case 1: Test Ngày bắt đầu phải lớn hơn ngày kết thúc
                TH1: Ngày kết thúc >= Ngày bắt đầu
                    => tạo phiếu lương thành công
                TH2: Ngày kết thúc < Ngày bắt đầu
                    => Tạo phiếu lương thất bại, Thông báo ngoại lệ
        """

        # TH2
        with self.assertRaises(ValidationError):
            self.create_payslip(
                self.product_emp_A.id,
                fields.Date.from_string('2021-7-1'),
                fields.Date.from_string('2021-6-1'),
                self.contract_open_emp_A.id)

        # TH1
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        self.assertTrue(payslip, 'Test Date from <= Date to not oke')

    # 8. Phiếu lương
    def test_payslip_date_overtlap_1(self):
        """
        8.1. Test ngày bắt đầu, ngày kết thúc, trùng lặp, nhân bản...
            Case 2: Test trùng lặp phiếu lương, Phiếu lương không liên quan đến bảng lương
                =>  Tạo thành công
        """
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-1'),
            fields.Date.from_string('2021-6-30'),
            self.contract_open_emp_A.id)
        payslip_2 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-1'),
            fields.Date.from_string('2021-6-30'),
            self.contract_open_emp_A.id)
        self.assertTrue(payslip_1, 'Test Date from <= Date to not oke')
        self.assertTrue(payslip_2, 'Test Date from <= Date to not oke')

    # 8. Phiếu lương
    def test_payslip_date_overtlap_2(self):
        """
        8.1. Test ngày bắt đầu, ngày kết thúc, trùng lặp, nhân bản...
            Case 3: Test trùng lặp phiếu lương, Phiếu lương liên quan đến bảng lương không đánh dấu lương tháng 13
                TH1: Phiếu lương của nhân viên là duy nhất trên bảng lương
                TH2: Nhân viên có nhiều hơn 1 phiếu lương trên bảng lương, các phiếu lương không trùng khoảng thời gian của nhau
                TH3: Nhân viên có nhiều hơn 1 phiếu lương trên bảng lương, có phiếu lương trùng khoảng thời gian của nhau

            Output:
                TH1+2: tạo/lưu thành công
                TH3: Thông báo lỗi
        """
        # TH1+2
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-1'),
            fields.Date.from_string('2021-6-30'),
            self.contract_open_emp_A.id)
        payslip_2 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-1'),
            fields.Date.from_string('2021-6-30'),
            self.contract_open_emp_A.id)
        payslip_run = self.env['hr.payslip.run'].create({
            'name': 'Payslip Batch',
            'date_start': fields.Date.from_string('2021-6-1'),
            'date_end': fields.Date.from_string('2021-6-30'),
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
        })

        # TH3
        payslip_1.write({'payslip_run_id': payslip_run.id})
        with self.assertRaises(UserError):
            payslip_2.write({'payslip_run_id': payslip_run.id})

    # 8. Phiếu lương
    def test_payslip_date_overtlap_3(self):
        """
        8.1. Test ngày bắt đầu, ngày kết thúc, trùng lặp, nhân bản...
            Case 4: Test trùng lặp phiếu lương, Phiếu lương liên quan bến bảng lương có đánh dấu lương tháng 13
                Input: Bảng lương với các phiếu lương cảu nhân viên
                    TH1: Phiếu lương của nhân viên là duy nhất trên bảng lương
                    TH2: Nhân viên có nhiều hơn 1 phiếu lương trên bảng lương
                Output:
                    TH1: Tạo/lưu thành công
                    TH2: Thông báo lỗi
        """
        # TH1
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-1'),
            fields.Date.from_string('2021-6-30'),
            self.contract_open_emp_A.id)
        payslip_2 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        payslip_run = self.env['hr.payslip.run'].create({
            'name': 'Payslip Batch',
            'date_start': fields.Date.from_string('2021-6-1'),
            'date_end': fields.Date.from_string('2021-6-30'),
            'thirteen_month_pay': True,
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
        })

        # TH2
        payslip_1.write({'payslip_run_id': payslip_run.id})
        with self.assertRaises(UserError):
            payslip_2.write({'payslip_run_id': payslip_run.id})

    # 8. Phiếu lương
    def test_payslip_duplicate_1(self):
        """
        8.1. Test ngày bắt đầu, ngày kết thúc, trùng lặp, nhân bản...
            Case 5: Test nhân bản phiếu lương, Phiếu lương không liên quan đến bảng lương nào
                Output: Nhân bản thành công
        """
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-1'),
            fields.Date.from_string('2021-6-30'),
            self.contract_open_emp_A.id)
        payslip_copy = payslip_1.copy()
        self.assertTrue(payslip_copy, 'Test Duplicate not oke')

    # 8. Phiếu lương
    def test_payslip_duplicate_2(self):
        """
        8.1. Test ngày bắt đầu, ngày kết thúc, trùng lặp, nhân bản...
            Case 6: Test nhân bản phiếu lương, Phiếu lương có liên quan đến 1 bảng lương
                Output: Không thành công
        """
        payslip_1 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-6-1'),
            fields.Date.from_string('2021-6-30'),
            self.contract_open_emp_A.id)
        payslip_run = self.env['hr.payslip.run'].create({
            'name': 'Payslip Batch',
            'date_start': fields.Date.from_string('2021-6-1'),
            'date_end': fields.Date.from_string('2021-6-30'),
            'thirteen_month_pay': True,
            'salary_cycle_id': self.env.company.salary_cycle_id.id,
        })
        payslip_1.write({'payslip_run_id': payslip_run.id})

        with self.assertRaises(UserError):
            payslip_1.copy()

    # 8. Phiếu lương
    def test_thirteen_month_pay_year_1(self):
        """
        Tạo phiếu lương tháng 13 với năm < 1970 hoặc năm >= 9999

        => Tạo không thành công
        """
        with self.assertRaises(UserError):
            self.env['hr.payslip'].with_context(tracking_disable=True).create({
                'employee_id': self.product_emp_A.id,
                'date_from': fields.Date.from_string('2021-1-1'),
                'date_to': fields.Date.from_string('2021-12-31'),
                'salary_cycle_id': self.env.company.salary_cycle_id.id,
                'thirteen_month_pay': True,
                'thirteen_month_pay_year': 9999,
                'contract_id': self.contract_open_emp_A.id,
                'company_id': self.env.company.id,
            })

        with self.assertRaises(UserError):
            self.env['hr.payslip'].with_context(tracking_disable=True).create({
                'employee_id': self.product_emp_A.id,
                'date_from': fields.Date.from_string('2021-1-1'),
                'date_to': fields.Date.from_string('2021-12-31'),
                'salary_cycle_id': self.env.company.salary_cycle_id.id,
                'thirteen_month_pay': True,
                'thirteen_month_pay_year': 1969,
                'contract_id': self.contract_open_emp_A.id,
                'company_id': self.env.company.id,
            })

    # 8. Phiếu lương
    def test_thirteen_month_pay_year_2(self):
        """
        Sửa phiếu lương tháng 13 với năm < 1970 hoặc năm >= 9999

        => Thông báo ngoại lệ
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-1-1'),
            fields.Date.from_string('2021-12-31'),
            self.contract_open_emp_A.id,
            thirteen_month_pay=True)

        with self.assertRaises(UserError):
            payslip.write({
                'thirteen_month_pay_year': 1969
            })
        with self.assertRaises(UserError):
            payslip.write({
                'thirteen_month_pay_year': 9999
            })

    def test_payslip_timeoff(self):
        """
        Work/leave information of payslip recording time off with leave type is 'leave'
        Input:
            Timeoff Type 1: time_type field is 'leave'
            Timeoff Type 2: time_type field is 'other'
            Create timeoff with this 2 timeoff type
            Create the payslip
        Output:
            Work/leave information of payslip recording time off with leave type is 'leave'
        """
        unpaid_type = self.env.ref('hr_holidays.holiday_status_unpaid')
        paid_type = self.env.ref('hr_holidays.holiday_status_cl')
        paid_type.time_type = 'other'
        
        timeoff_1 = self.create_holiday(
            'Time off: 2021/07/06 - 2021/07/09',
            self.product_emp_A.id,
            unpaid_type.id,
            fields.Datetime.to_datetime('2021-07-06 06:00:00'),
            fields.Datetime.to_datetime('2021-07-09 15:00:00'),
        )
        timeoff_1.action_validate()
        timeoff_2 = self.create_holiday(
            'Time off: 2021/07/13 - 2021/07/16',
            self.product_emp_A.id,
            paid_type.id,
            fields.Datetime.to_datetime('2021-07-13 06:00:00'),
            fields.Datetime.to_datetime('2021-07-16 15:00:00'),
        )
        timeoff_2.action_validate()

        payslip_t7 = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.to_date('2021-07-1'),
            fields.Date.to_date('2021-07-31'),
            self.contract_open_emp_A.id,
        )

        self.assertRecordValues(
            payslip_t7,
            [
                {
                    'calendar_working_hours': 176,
                    'calendar_working_days': 22,
                    'duty_working_hours':176,
                    'duty_working_days':22,
                    'worked_hours':144,
                    'worked_days':18,
                    'leave_hours': 32,
                    'leave_days': 4,
                    'unpaid_leave_hours': 32,
                    'unpaid_leave_days': 4,
                }
            ]
        )
