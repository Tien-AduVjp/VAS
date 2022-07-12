from unittest.mock import patch
from datetime import timedelta

from odoo.tests import SavepointCase,tagged, Form
from odoo import fields
from odoo.exceptions import UserError
from locale import currency


@tagged('post_install','-at_install')
class TestHrOvertimePayroll(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHrOvertimePayroll, cls).setUpClass()
        cls.employee_01 = cls.env.ref('hr.employee_qdp').copy()
        cls.contract_emp_01 = cls.env.ref('hr_contract.hr_contract_qdp').copy()
        cls.contract_emp_01.date_start = fields.date(2021, 3, 4)
        cls.contract_emp_01.employee_id = cls.employee_01
        cls.contract_emp_01.action_start_contract()
        cls.travel_allowance = cls.env['hr.advantage.template'].search([('code','=','TRAVEL')], limit=1)
        cls.phone_allowance = cls.env['hr.advantage.template'].search([('code','=','PHONE')], limit=1)
        cls.meal_allowance = cls.env['hr.advantage.template'].search([('code','=','MEAL')], limit=1)
        cls.travel_allowance.update({
            'upper_bound':50.0
        })
        cls.phone_allowance.update({
            'upper_bound':50.0
        })
        cls.meal_allowance.update({
            'upper_bound':50.0
        })
        cls.not_ot_allowance = cls.env['hr.advantage.template'].create({
            'name': 'Not Overtime Allowance',
            'code': 'NOTOT',
            'lower_bound': 0.0,
            'upper_bound': 50.0,
            'overtime_base_factor': False
        })
        cls.start_of_oct = fields.date(2021, 10, 1)
        cls.end_of_oct = fields.date(2021, 10, 31)

    def test_01_compute_overtime_plan_line_ids(self):
        """
            Testcase 1: Kiểm tra tính toán dòng tăng ca trên phiếu lương.
            Input: Khoảng thời gian xuất phiếu lương không có dòng tăng ca.
            Expect: Dòng tăng ca trên phiếu lương không có dữ liệu.
        """
        payslip = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        payslip.compute_sheet()
        self.assertFalse(payslip.overtime_plan_line_ids)

    def test_02_compute_overtime_plan_line_ids(self):
        """
            Testcase 1: Kiểm tra tính toán dòng tăng ca trên phiếu lương.
            Input: Trong khoảng thời gian của phiếu lương có dòng tăng ca.
            Expect: Trên phiếu lương có dữ liệu dòng tăng ca.
                    Tạo một phiếu lương khác có thời gian có thời gian tăng ca đó thì dữ liệu dòng tăng ca sẽ xuất hiện trên cả 2 phiếu lương.
        """
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 14),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':fields.date(2021,10,17),
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        payslip_02 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':fields.date(2021,10,13),
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        payslip_01.compute_sheet()
        payslip_02.compute_sheet()
        self.assertTrue(payslip_01.overtime_plan_line_ids and overtime_plan_emp_01.line_ids == payslip_01.overtime_plan_line_ids)
        self.assertTrue(payslip_02.overtime_plan_line_ids and overtime_plan_emp_01.line_ids == payslip_02.overtime_plan_line_ids)

    def test_03_compute_overtime_base_amount(self):
        """
            Test case 3: Kiểm tra tính toán số tiền cơ sở tăng ca trên hợp đồng lao động.
            Input: 3.1. Chế độ tiền cơ sở tính tăng ca: Lương tổng.
                   3.2. Chế độ tiền cơ sở tính tăng ca: Lương cơ bản.
                   3.3. Chế độ tiền cơ sở tính tăng ca: Lương nhập thủ công.
                   3.4. Chế độ tiền cơ sở tính tăng ca: Lương cơ bản + chế độ đãi ngộ theo cấu hình
            Expect:3.1. Số tiền tính tăng ca cơ sở bằng lương tổng (bao gồm những khoản phụ cấp có nhân tố tăng ca và không có nhân tố tăng ca)
                   3.2. Số tiền tính tăng ca cơ sở bằng lương cơ bản (không bao gồm khoản phụ cấp nào)
                   3.3. Số tiền tính tăng ca cơ sở được nhập thủ công (trường overtime_base_amount ở trạng thái editable)
                   3.4. Số tiền tính tăng ca cơ sở bằng lương cơ bản và những khoản phụ cấp có đánh dấu nhân tố tăng ca.
        """
        self.contract_emp_01.update({
            'advantage_ids': [
                (0, 0, {
                'template_id': self.travel_allowance.id,
                'amount':50.0
                }),
                (0, 0, {
                    'template_id': self.phone_allowance.id,
                    'amount':50.0
                }),
                (0, 0, {
                    'template_id': self.meal_allowance.id,
                    'amount':50.0
                }),
                (0, 0, {
                    'template_id': self.not_ot_allowance.id,
                    'amount':50.0
                })
            ]
        })
        contract_form = Form(self.contract_emp_01)
        contract_form.overtime_base_mode = 'wage'
        self.assertTrue(contract_form._get_modifier('overtime_base_amount', 'readonly'))
        self.assertEqual(contract_form.overtime_base_amount, contract_form.wage)
        contract_form.overtime_base_mode = 'gross'
        self.assertTrue(contract_form._get_modifier('overtime_base_amount', 'readonly'))
        self.assertEqual(contract_form.overtime_base_amount, contract_form.wage + 200.0)
        contract_form.overtime_base_mode = 'manual'
        self.assertFalse(contract_form._get_modifier('overtime_base_amount', 'readonly'))
        contract_form.overtime_base_mode = 'wage_and_advantages'
        self.assertTrue(contract_form._get_modifier('overtime_base_amount', 'readonly'))
        self.assertEqual(contract_form.overtime_base_amount, contract_form.wage + 150.0)

    def test_04_taxed_ot_untaxed_ot(self):
        """
            Test case 04: Tính tiền tăng ca chịu thuế và không chịu thuế.
            Expect: Tiền tăng ca chịu thuế bằng tổng số tiền tăng ca chi theo giờ chuẩn
                    Tiền tăng ca không chịu thuế bằng tiền tăng ca thực tế trừ số tiền chi theo giờ tiêu chuẩn của tất cả các dòng tăng ca trên phiếu lương.
        """
        self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 14),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        currency = payslip_01.currency_id
        payslip_01.compute_sheet()
        ot_standard_pay = sum(payslip_01.overtime_plan_line_ids.mapped('standard_pay'))
        ot_actual_ot_pay = sum(payslip_01.overtime_plan_line_ids.mapped('actual_overtime_pay'))
        taxed_ot = payslip_01.line_ids.filtered(lambda r : r.code == 'TAXED_OT').amount
        untaxed_ot = payslip_01.line_ids.filtered(lambda r : r.code == 'UNTAXED_OT').amount
        self.assertEqual(currency.round(taxed_ot), currency.round(ot_standard_pay))
        self.assertEqual(currency.round(untaxed_ot), currency.round(ot_actual_ot_pay - taxed_ot))

    def test_05_get_overtime_data(self):
        """
            Test case 05: Kiểm tra tính toán dòng tăng ca trên phiếu lương khi dữ liệu dòng tăng ca thay đổi.
            Input: Tạo kế hoạch tăng ca hợp lệ trong khoảng thời gian của phiêu lương.
            Expect: Khi thay đổi dữ liệu tăng ca (Thời gian tăng ca) hoặc cập nhật thêm dòng tăng ca mới trong khoảng thời gian này.
                    thì dữ liệu tăng ca ở trên phiếu lương sẽ được cập nhật.
        """
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 11, 1),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        self.assertTrue(overtime_plan_emp_01.line_ids)
        self.assertFalse(payslip_01.overtime_plan_line_ids)
        overtime_plan_emp_01.update({
            'date':fields.date(2021, 10, 13)
        })
        overtime_plan_emp_02 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 14),
            'time_start':17.0,
            'time_end':22.0
        })
        self.assertTrue(overtime_plan_emp_02.line_ids and overtime_plan_emp_01.line_ids)
        self.assertEqual(overtime_plan_emp_02.line_ids | overtime_plan_emp_01.line_ids ,payslip_01.overtime_plan_line_ids)
        payslip_01.action_compute_overtime_plan_line_ids()
        self.assertEqual(overtime_plan_emp_02.line_ids | overtime_plan_emp_01.line_ids ,payslip_01.overtime_plan_line_ids)

    def test_06_test_compute_sheet(self):
        """
            Test case 06: Kiểm tra hành động tính toán phiếu lương khi kế hoạch tăng ca thay đổi.
        """
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 13),
            'time_start':17.0,
            'time_end':22.0
        })
        currency= payslip_01.currency_id
        #Khi chưa thực hiện tính toán phiếu lương thì số tiền tăng ca chịu thuế và không chịu thuế bằng 0.0
        self.assertEqual(payslip_01.line_ids.filtered(lambda r : r.code == 'TAXED_OT').amount , 0.0)
        self.assertEqual(payslip_01.line_ids.filtered(lambda r : r.code == 'UNTAXED_OT').amount , 0.0)
        payslip_01.compute_sheet()
        taxed_ot = payslip_01.line_ids.filtered(lambda r : r.code == 'TAXED_OT').amount
        untaxed_ot = payslip_01.line_ids.filtered(lambda r : r.code == 'UNTAXED_OT').amount
        ot_01_standard_pay = sum(overtime_plan_emp_01.line_ids.mapped('standard_pay'))
        ot_01_actual_ot_pay = sum(overtime_plan_emp_01.line_ids.mapped('actual_overtime_pay'))
        self.assertNotEqual(payslip_01.line_ids.filtered(lambda r : r.code == 'TAXED_OT').amount , 0.0)
        self.assertNotEqual(payslip_01.line_ids.filtered(lambda r : r.code == 'UNTAXED_OT').amount , 0.0)
        self.assertEqual(currency.round(taxed_ot), currency.round(ot_01_standard_pay))
        self.assertEqual(currency.round(untaxed_ot), currency.round(ot_01_actual_ot_pay - taxed_ot))
        #Thêm kế hoạch tăng ca để kiểm tra tính toán phiếu lương, số tiền tăng ca chịu thuế và không chịu thuế sẽ được cộng thêm bởi dòng tăng ca hợp lệ được thêm vào.
        overtime_plan_emp_02 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 14),
            'time_start':17.0,
            'time_end':22.0
        })
        ot_02_standard_pay = sum(overtime_plan_emp_02.line_ids.mapped('standard_pay'))
        ot_02_actual_ot_pay = sum(overtime_plan_emp_02.line_ids.mapped('actual_overtime_pay'))
        self.assertEqual(payslip_01.overtime_plan_line_ids, overtime_plan_emp_01.line_ids | overtime_plan_emp_02.line_ids)
        payslip_01.compute_sheet()
        taxed_ot = payslip_01.line_ids.filtered(lambda r : r.code == 'TAXED_OT').amount
        untaxed_ot = payslip_01.line_ids.filtered(lambda r : r.code == 'UNTAXED_OT').amount
        self.assertEqual(currency.round(taxed_ot), currency.round(ot_01_standard_pay + ot_02_standard_pay))
        self.assertEqual(currency.round(untaxed_ot), currency.round(ot_01_actual_ot_pay + ot_02_actual_ot_pay - taxed_ot))

    def test_07_unlink_overtime_line(self):
        """
        Test 07: Kiểm tra xóa kế hoạch tăng ca.
        Input: Dòng tăng ca không tham chiếu đến phiếu lương nào ở trạng thái khác dự thảo.
        Expect: Có thể xóa thành công kế hoạch tăng ca.
        """
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 13),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        payslip_01.compute_sheet()
        self.assertEqual(overtime_plan_emp_01.line_ids, payslip_01.overtime_plan_line_ids)
        overtime_plan_emp_01.unlink()
        self.assertFalse(overtime_plan_emp_01.line_ids)

    def test_08_unlink_overtime_line(self):
        """
            Test case 8: Kiểm tra xóa kế hoạch tăng ca.
            Input: Dòng tăng ca đang tham chiếu đến phiếu lương ở trạng thái khác dự thảo.
            Expect: Hiển thị thông báo lỗi và không cho xóa dòng tăng ca.
        """
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 13),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        payslip_01.compute_sheet()
        payslip_01.action_payslip_verify()
        self.assertTrue(overtime_plan_emp_01.has_non_draft_payslips)
        self.assertEqual(payslip_01.overtime_plan_line_ids, overtime_plan_emp_01.line_ids)
        with self.assertRaises(UserError):
            overtime_plan_emp_01.unlink()
        payslip_01.action_payslip_done()

    def test_09_recompute_plan_line(self):
        """
            Test case 09: Kiểm tra hoạt động nạp lại/ khớp phiếu lương.
            Expect: Phiếu lương ở trạng thái dự thảo, có thể tính lại dòng tăng ca
                    Phiếu lương ở trạng thái khác dự thảo, không cho tính lại
        """
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 13),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        overtime_plan_emp_01.action_recompute_plan_lines()
        payslip_01.action_payslip_verify()
        with self.assertRaises(UserError):
            overtime_plan_emp_01.action_recompute_plan_lines()
        payslip_01.action_payslip_done()
        with self.assertRaises(UserError):
            overtime_plan_emp_01.action_recompute_plan_lines()
        payslip_01.action_payslip_cancel()
        with self.assertRaises(UserError):
            overtime_plan_emp_01.action_recompute_plan_lines()

    def test_10_payslip_run(self):
        """
            Test case 10: Kiểm tra tạo bảng lương theo chế độ chu ký bản lương.
        """
        self.contract_emp_01.date_start = fields.date(2021, 10, 15)
        overtime_plan_emp_00 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 10),
            'time_start':17.0,
            'time_end':22.0
        })
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 16),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_run_01 = self.env['hr.payslip.run'].create({
            'name':'Payslip run October 2021',
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_start':self.start_of_oct,
            'date_end':self.end_of_oct
        })
        hr_payslip_employee_01 = self.env['hr.payslip.employees'].create({
            'batch_id':payslip_run_01.id,
            'mode':'batch_period',
            'employee_ids':[(6,0,[self.employee_01.id])]
        })
        hr_payslip_employee_01.compute_sheet()
        payslip_run_01.slip_ids.compute_sheet()
        self.assertTrue(payslip_run_01.slip_ids[0].overtime_plan_line_ids)
        self.assertEqual(payslip_run_01.slip_ids[0].overtime_plan_line_ids, overtime_plan_emp_01.line_ids)

    def test_11_payslip_run(self):
        """
            Thực hiện tạo bảng lương theo thời hạn hợp đồng. OT nằm trong chu kỳ bảng lương nhưng không nằm trong hợp đồng.
        """
        self.contract_emp_01.date_start = fields.date(2021, 10, 15)
        overtime_plan_emp_00 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 10),
            'time_start':17.0,
            'time_end':22.0
        })
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 16),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_run_01 = self.env['hr.payslip.run'].create({
            'name':'Payslip run October 2021',
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_start':self.start_of_oct,
            'date_end':self.end_of_oct
        })
        hr_payslip_employee_01 = self.env['hr.payslip.employees'].create({
            'batch_id':payslip_run_01.id,
            'mode':'contract_period',
            'employee_ids':[(6,0,[self.employee_01.id])]
        })
        hr_payslip_employee_01.compute_sheet()
        payslip_run_01.slip_ids.compute_sheet()
        self.assertTrue(payslip_run_01.slip_ids[0].overtime_plan_line_ids)
        self.assertEqual(payslip_run_01.slip_ids[0].overtime_plan_line_ids, overtime_plan_emp_01.line_ids)

    def test_12_auto_generate_payslip(self):
        """
            Test 12: Kiểm tra chế độ tự động tạo bảng lương.
            Expect: Các dòng tăng ca trong thời gian tạo bảng lương tự động sẽ được tính vào phiếu lương tạo ra với dữ liệu tính toán đúng về các khoản tiền
                    tăng ca chịu thuế và không chịu thuế.
        """
        with patch.object(fields.Date, 'today', lambda:fields.date(2021, 10, 14)):
            self.employee_01.company_id.payslips_auto_generation = True
            self.contract_emp_01.payslips_auto_generation = True
            overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
                'employee_id':self.employee_01.id,
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none',
                'date':fields.date(2021, 9, 16),
                'time_start':17.0,
                'time_end':22.0
            })
            self.env.ref('to_hr_payroll.ir_cron_generate_payslips').method_direct_trigger()
            payslip = self.env['hr.payslip'].search([('employee_id','=',self.employee_01.id)])
            currency = payslip.currency_id
            payslip.compute_sheet()
            self.assertTrue(len(payslip) == 1 and payslip.overtime_plan_line_ids == overtime_plan_emp_01.line_ids)
            ot_standard_pay = sum(payslip.overtime_plan_line_ids.mapped('standard_pay'))
            ot_actual_ot_pay = sum(payslip.overtime_plan_line_ids.mapped('actual_overtime_pay'))
            taxed_ot = payslip.line_ids.filtered(lambda r : r.code == 'TAXED_OT').amount
            untaxed_ot = payslip.line_ids.filtered(lambda r : r.code == 'UNTAXED_OT').amount
            self.assertEqual(currency.round(taxed_ot), currency.round(ot_standard_pay))
            self.assertEqual(currency.round(untaxed_ot), currency.round(ot_actual_ot_pay - taxed_ot))

    def test_13_thirteen_month_pay(self):
        """
            Test case 13: Kiểm tra tạo phiếu lương tháng 13.
            Expect: Phiếu lương không có dòng tăng ca và các khoản tăng ca có thuế và không có thuế.
        """
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 16),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':fields.date(2021,10,17),
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id,
            'thirteen_month_pay': True
        })
        payslip_01.compute_sheet()
        self.assertEqual(overtime_plan_emp_01.line_ids, payslip_01.overtime_plan_line_ids)
        taxed_ot = payslip_01.line_ids.filtered(lambda r : r.code == 'TAXED_OT').amount
        untaxed_ot = payslip_01.line_ids.filtered(lambda r : r.code == 'UNTAXED_OT').amount
        self.assertEqual(taxed_ot, 0.0)
        self.assertEqual(untaxed_ot, 0.0)

    #-----------------------------------------------------Method Test--------------------------------------------------------------#

    def test_14_action_cancel_contract_resolve_mismatch_contract(self):
        """
            Testcase 14: Kiểm tra hành động hủy hợp đồng và khớp hợp đồng.
            Expect: Khi hủy hợp đồng hoặc khớp hợp đồng của nhân viên có dòng tăng ca ở trong phiếu lương ở trạng thái xác nhận sẽ có thông báo lỗi.
        """
        overtime_plan_emp_01 = self.env['hr.overtime.plan'].create({
            'employee_id':self.employee_01.id,
            'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
            'recognition_mode':'none',
            'date':fields.date(2021, 10, 13),
            'time_start':17.0,
            'time_end':22.0
        })
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        payslip_01.compute_sheet()
        payslip_01.action_payslip_verify()
        with self.assertRaises(UserError):
            self.contract_emp_01.action_cancel()
            overtime_plan_emp_01.action_resolve_contract_mismatch()

    def test_15_get_overtime_data(self):
        """
            Test case 15: Dòng tăng ca tự động được thêm vào phiếu lương ở trạng thái dự thảo
            Input:
                Tạo phiếu lương ở trạng thái dự thảo
                Tạo kế hoạch tăng ca hợp lệ trước/trong/sau khoảng thời gian của phiêu lương.
            Expect:
                Các dòng tăng ca trước và trong khoảng chu kỳ phiếu lương được thêm vào phiếu lương
        """
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        self.assertFalse(payslip_01.overtime_plan_line_ids)

        overtime_plan_emp_01, overtime_plan_emp_02, overtime_plan_emp_03 = self.env['hr.overtime.plan'].create([
            {
                'employee_id':self.employee_01.id,
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none',
                'date':fields.date(2021, 9, 10),
                'time_start':17.0,
                'time_end':22.0
            },
            {
                'employee_id':self.employee_01.id,
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none',
                'date':fields.date(2021, 10, 10),
                'time_start':17.0,
                'time_end':22.0
            },
            {
                'employee_id':self.employee_01.id,
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none',
                'date':fields.date(2021, 11, 1),
                'time_start':17.0,
                'time_end':22.0
            }])
        self.assertEqual(overtime_plan_emp_01.line_ids | overtime_plan_emp_02.line_ids, payslip_01.overtime_plan_line_ids)

    def test_16_get_overtime_data(self):
        """
            Test case 15: Dòng tăng ca không được thêm vào phiếu lương ở trạng thái khác dự thảo
            Input:
                Tạo phiếu lương ở trạng thái dự thảo và xác nhận
                Tạo kế hoạch tăng ca hợp lệ trước/trong/sau khoảng thời gian của phiêu lương.
            Expect:
                Các dòng tăng ca trước và trong khoảng chu kỳ phiếu lương không được thêm vào phiếu lương
        """
        payslip_01 = self.env['hr.payslip'].create({
            'employee_id':self.employee_01.id,
            'salary_cycle_id':self.env.ref('to_hr_payroll.hr_salary_cycle_default').id,
            'date_from':self.start_of_oct,
            'date_to':self.end_of_oct,
            'company_id':self.employee_01.company_id.id,
            'contract_id':self.employee_01.contract_id.id
        })
        payslip_01.action_payslip_verify()
        self.assertFalse(payslip_01.overtime_plan_line_ids)

        self.env['hr.overtime.plan'].create([
            {
                'employee_id':self.employee_01.id,
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none',
                'date':fields.date(2021, 9, 10),
                'time_start':17.0,
                'time_end':22.0
            },
            {
                'employee_id':self.employee_01.id,
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none',
                'date':fields.date(2021, 10, 10),
                'time_start':17.0,
                'time_end':22.0
            },
            {
                'employee_id':self.employee_01.id,
                'reason_id':self.env.ref('viin_hr_overtime.hr_overtime_reason_project').id,
                'recognition_mode':'none',
                'date':fields.date(2021, 11, 1),
                'time_start':17.0,
                'time_end':22.0
            }])
        self.assertFalse(payslip_01.overtime_plan_line_ids)
