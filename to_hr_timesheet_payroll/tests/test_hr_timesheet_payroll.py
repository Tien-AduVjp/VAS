from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestHrTimesheetPayroll(Common):
    
    def test_01_hr_timesheet_payroll(self):
        """
        Case 1: Kiểm tra Thông tin chấm công khi thay đổi trường nhân viên/khoảng thời gian phiếu lương
        Input: 
            + Nhân viên 1 có : 
            + chấm công 1 vào ngày 10/10/2021, thời lượng 1 giờ
            + chấm công 2 vào ngày 31/10/2021, thời lượng 1 giờ
            + Tạo phiếu lương cho nhân viên 1 thời gian bắt đầu từ ngày 01/10/2021 - 15/10/2021
            + Thực hiện tính toán
        Ouput: 
            + Chấm công 1 được tính vào phiếu lương
            + Chấm công 2 không được tính vào phiếu lương
            + Số lượng chấm công : 1
            + Chi phí chấm công nằm trong tab Accounting Information:
                Chi phí chấm công = Số giờ chấm công * ( chi phí công ty / số giờ phải làm) * tỷ lệ chi chả của công ty 
                hoặc = 0 nếu số giờ phải làm = 0
        """
        self.payslip_employee_1.compute_sheet()
        self.assertIn(self.timesheet_1, self.payslip_employee_1.timesheet_line_ids)
        self.assertNotIn(self.timesheet_2, self.payslip_employee_1.timesheet_line_ids)
        self.assertEqual(self.payslip_employee_1.timesheet_lines_count, 1)
        timesheet_cost = self.payslip_employee_1.timesheet_lines_count * \
                         round(self.payslip_employee_1.company_cost / self.payslip_employee_1.duty_working_hours * self.env.company.general_overhead, 2)
        self.assertEqual(self.payslip_employee_1.timesheet_cost, timesheet_cost)
    
    def test_02_hr_timesheet_payroll(self):
        """
        Case 1: Kiểm tra Thông tin chấm công khi thay đổi trường nhân viên/khoảng thời gian phiếu lương
        Input: 
            + Dữ liệu như case 1
            + Thực hiện thay đổi khoảng thời gian phiếu lương từ 01/10/2021 - 31/10/2021
        Ouput: 
            + Chấm công 2 được tính vào phiếu lương
            + Số lượng chấm công : 2
            + Chi phí chấm công nằm trong tab Accounting Information thay đổi:
                Chi phí chấm công = Số giờ chấm công * ( chi phí công ty / số giờ phải làm) * tỷ lệ chi chả của công ty 
                hoặc = 0 nếu số giờ phải làm = 0
        """
        self.payslip_employee_1.write({'date_to': '2021-10-31'})
        self.assertIn(self.timesheet_2, self.payslip_employee_1.timesheet_line_ids)
        self.assertEqual(self.payslip_employee_1.timesheet_lines_count, 2)
        timesheet_cost = self.payslip_employee_1.timesheet_lines_count * \
                         round(self.payslip_employee_1.company_cost / self.payslip_employee_1.duty_working_hours * self.env.company.general_overhead, 2)
        self.assertEqual(self.payslip_employee_1.timesheet_cost, timesheet_cost)
    
    def test_03_hr_timesheet_payroll(self):
        """
        Case 3: Kiểm tra Chi phí cho Bảng chấm công trên thông tin nhân viên, khi nhân vien chưa có phiếu lương nào
        Input: Nhân viên chưa có phiếu lương
            Truy cập vào thông tin nhân viên, tab "Cài đặt nhân sự"
        Output: Chi phí cho Bảng chấm công: 0
        """
        self.assertEqual(self.employee_2.payslips_count, 0)
        self.assertEqual(self.employee_2.timesheet_cost, 0)
    
    def test_04_hr_timesheet_payroll(self):
        """
        Case 4: Kiểm tra Chi phí cho Bảng chấm công trên thông tin nhân viên, khi nhân viên đã có một phiếu lương ở trạng thái dự thảo
        Input: Nhân viên có một phiếu lương đang ở trang thái dự thảo
            Truy cập vào thông tin nhân viên, tab "Cài đặt nhân sự"
        Output: Chi phí cho Bảng chấm công: 0

        """
        self.assertEqual(self.payslip_employee_1.state, 'draft')
        self.assertEqual(self.employee_1.payslips_count, 1)
        self.assertEqual(self.employee_1.timesheet_cost, 0)
    
    def test_05_hr_timesheet_payroll(self):
        """
        Case 5: Kiểm tra Chi phí cho Bảng chấm công trên thông tin nhân viên, 
        khi nhân viên đã có một phiếu lương ở trạng thái xác nhận/ hoàn thành
        Input: Nhân viên có một phiếu lương đang ở trang thái dự thảo
            Truy cập vào thông tin nhân viên, tab "Cài đặt nhân sự"
        Output: Chi phí cho Bảng chấm công: chi phí công ty / số giờ phải làm của phiếu lương * hệ số chi phí công ty

        """
        self.payslip_employee_1.compute_sheet()
        self.payslip_employee_1.action_payslip_verify()
        self.assertEqual(self.payslip_employee_1.state, 'verify')
        self.assertEqual(self.employee_1.payslips_count, 1)
        cost_employee = round(self.payslip_employee_1.company_cost / self.payslip_employee_1.duty_working_hours * self.env.company.general_overhead, 2) 
        self.assertEqual(self.employee_1.timesheet_cost, cost_employee)
    
    def test_06_hr_timesheet_payroll(self):
        """
        Case 6: Kiểm tra Chi phí cho Bảng chấm công trên thông tin nhân viên, khi nhân viên có 2 phiếu lương ở trạng thái xác 
        Input: Nhân viên có 2 phiếu lương đã xác nhân:
            + Phiếu lương 1: phiếu lương tháng 9
            + Phiếu lương 2: phiếu lương tháng 10
            Truy cập vào thông tin nhân viên, tab "Cài đặt nhân sự"
        Output: Chi phí cho Bảng chấm công: chi phí công ty / số giờ phải làm của phiếu lương tháng 10 * hệ số chi phí 

        """
        payslip_sep = self.env['hr.payslip'].create({
            'employee_id': self.employee_2.id,
            'contract_id' : self.employee_2.contract_id.id,
            'struct_id': self.salary_structure.id,
            'date_from': '2021-09-01',
            'date_to': '2021-09-30',
            'company_id': self.env.company.id,
        })
        payslip_sep.compute_sheet()
        payslip_sep.action_payslip_verify()
        
        payslip_oct = self.env['hr.payslip'].create({
            'employee_id': self.employee_2.id,
            'contract_id' : self.employee_2.contract_id.id,
            'struct_id': self.salary_structure.id,
            'date_from': '2021-10-01',
            'date_to': '2021-10-31',
            'company_id': self.env.company.id,
        })
        payslip_oct.compute_sheet()
        payslip_oct.action_payslip_verify()
        
        self.assertEqual(payslip_sep.state, 'verify')
        self.assertEqual(payslip_oct.state, 'verify')
        
        cost_employee = round(payslip_oct.company_cost / payslip_oct.duty_working_hours, 2)
        self.assertEqual(self.employee_2.timesheet_cost, cost_employee)
    
    def test_07_hr_timesheet_payroll(self):
        """
        Case 7: Kiểm số tiền trên các bản ghi chấm công của nhân viên đã xác nhận / hoàn thành
        Input: 
            + Chấm công tháng 10 thời gian là 1 tiếng
            + Phiếu lương tháng 10 của nhân viên đã được xác nhận, đã có chấm công dc ghi nhận vào phiếu 
            + Truy cập các bản ghi chấm trông trong menu Tài khoản quản trị của Kế toán, chọn dự án tương ứng chấm công,
            + Nhấn vào chi phí và doanh thu
        Output: Số tiền của các bản ghi chấm công , số tiền = số giờ chấm công * chi phí nhân viên tương ứng với phiếu lương
        """
        payslip_oct = self.env['hr.payslip'].create({
            'employee_id': self.employee_2.id,
            'contract_id' : self.employee_2.contract_id.id,
            'struct_id': self.salary_structure.id,
            'date_from': '2021-10-01',
            'date_to': '2021-10-31',
            'company_id': self.env.company.id,
        })
        payslip_oct.compute_sheet()
        payslip_oct.action_payslip_verify()
        
        self.assertEqual(payslip_oct.state, 'verify')
        self.assertIn(self.timesheet_3, payslip_oct.timesheet_line_ids)
        amount_timesheet_3 = self.timesheet_3.unit_amount * self.employee_2.timesheet_cost
        self.assertEqual(self.timesheet_3.amount, -amount_timesheet_3)
    
    def test_08_hr_timesheet_payroll(self):
        """
        Case 8: Kiểm thông tin chi phí mỗi giờ sau khi thay đổi hệ số chi phí công ty là 2
        Input: 
            + Nhân viên đã có phiếu lương được trong thời gian gần nhất được xác nhận/hoàn thành
            + Chi phí trên thông tin nhân viên được cập nhật
            + Thực hiện thay đổi hệ số công ty là 2
            + Thực hiện ấn Nút "Calculate Timsheet Cost" Trên thông tin nhân viên
        Output: Chi phí mỗi giờ thay đổi: chi phí = chi phí công ty / thời gian phải làm * hệ số công ty 
                của phiếu lương gần nhất theo hệ số 2
        """
        self.payslip_employee_1.compute_sheet()
        self.payslip_employee_1.action_payslip_verify()
        self.assertEqual(self.payslip_employee_1.state, 'verify')
        cost_employee_1 = round(self.payslip_employee_1.company_cost / self.payslip_employee_1.duty_working_hours * self.env.company.general_overhead, 2) 
        self.assertEqual(self.employee_1.timesheet_cost, cost_employee_1)
        
        #Thay đổi hệ số chi phí công ty là 2
        self.env.company.write({'general_overhead': 2})
        cost_employee_2 = round(self.payslip_employee_1.company_cost / self.payslip_employee_1.duty_working_hours * self.env.company.general_overhead, 2) 
        
        self.assertNotEqual(cost_employee_1, cost_employee_2)
        self.employee_1.action_update_timesheet_cost_from_payslips()
        self.assertEqual(self.employee_1.timesheet_cost, cost_employee_2)
    
    
    """
        Dữ liệu Case 9, 10, 11: 
        Nhân viên có 2 hợp đồng trong tháng 10.
        Hợp đồng 1: từ 1/10/2021 -> 22/10/2021, lương cơ bản 5000 €
        Hợp đồng 2: từ 23/10/2021 -> nay, lương cơ bản 10.000 €
        Nhân viên có khung giờ làm việc: 40h/ tuần. Đã thực hiện chấm công vào 2 ngày 24,25/10/2021 mỗi ngày 8 tiếng
        Tạo phiếu lương chu kì  1/10->31/10/2021
        Thực hiện tính toán và xác nhận phiếu 
        
    """
    def test_09_hr_timesheet_payroll(self):
        """
        Case 9: Kiểm tra dữ liệu chấm công được tính toán vào phiếu lương, chi phí chấm công
                và chi phí mỗi giờ nhân viên khi có nhiều hợp đồng trong một chu kì lương
        - Input: Hợp đồng 1 đã huỷ, Hợp đồng 2 (Đang chạy/Hết hạn)
        - Output:
            + Timesheet 4,5 hợp lệ được tính vào phiếu lương
            + Chi phí mỗi giờ không tính toán theo hợp đồng 1, tính theo hợp đồng 2
            + Chi phí chấm công là: 952.38 €
            + Chi phí mỗi giờ của nhân viên: 59,52€
        """
        self.contract_1_employee_4.write({'state': 'cancel'})
        self.contract_2_employee_4.write({'state': 'open'})
        self.assertEqual(self.contract_1_employee_4.state, 'cancel')
        self.assertEqual(self.contract_2_employee_4.state, 'open')
        
        payslip_oct = self.env['hr.payslip'].create({
            'employee_id': self.employee_4.id,
            'contract_id' : self.employee_4.contract_id.id,
            'struct_id': self.salary_structure.id,
            'date_from': '2021-10-01',
            'date_to': '2021-10-31',
            'company_id': self.env.company.id,
        })
        payslip_oct.compute_sheet()
        payslip_oct.action_payslip_verify()
        
        self.assertRecordValues(
            payslip_oct, 
            [{
                'timesheet_line_ids': [self.timesheet_4.id, self.timesheet_5.id], 
                'timesheet_cost': 952.38
            }]
        )
        self.assertEqual(self.employee_4.timesheet_cost, 59.52)
    
    def test_10_hr_timesheet_payroll(self):
        """
        Case 10: Kiểm tra dữ liệu chấm công được tính toán vào phiếu lương, chi phí chấm công
                và chi phí mỗi giờ nhân viên khi có nhiều hợp đồng trong một chu kì lương
        - Input: Hợp đồng 1 ,2 đều ở trạng thái hợp lệ (Đang chạy/ Hết hạn)
        - Output:
            + Timesheet 4,5 hợp lệ được tính vào phiếu lương
            + Chi phí chấm công là: 589.57 €
            + Chi phí mỗi giờ của nhân viên: 36.85 € 
        """
        self.contract_2_employee_4.write({'state': 'open'})
        payslip_oct = self.env['hr.payslip'].create({
            'employee_id': self.employee_4.id,
            'contract_id' : self.employee_4.contract_id.id,
            'struct_id': self.salary_structure.id,
            'date_from': '2021-10-01',
            'date_to': '2021-10-31',
            'company_id': self.env.company.id,
        })
        self.assertEqual(self.contract_1_employee_4.state, 'open')
        self.assertEqual(self.contract_2_employee_4.state, 'open')
        
        payslip_oct.compute_sheet()
        payslip_oct.action_payslip_verify()
        
        self.assertRecordValues(
            payslip_oct, 
            [{
                'timesheet_line_ids': [self.timesheet_4.id, self.timesheet_5.id], 
                'timesheet_cost': 589.57
            }]
        )
        self.assertEqual(self.employee_4.timesheet_cost, 36.85)
    
    def test_11_hr_timesheet_payroll(self):
        """
        Case 11: Kiểm tra dữ liệu chấm công được tính toán vào phiếu lương, chi phí chấm công
                và chi phí mỗi giờ nhân viên khi có nhiều hợp đồng trong một chu kì lương
        - Input: Hợp đồng 1 đang chạy, hợp đồng 2 bị huỷ
        - Output:
            + Timesheet 4,5 khôn hợp lệ không được tính vào phiếu lương
            + Chi phí chấm công không dược tính vì không có chấm công nào 0 € 
            + Chi phí mỗi giờ của nhân viên: 29.76 €
        """
        self.contract_2_employee_4.action_start_contract()
        self.contract_2_employee_4.action_cancel()
        self.assertEqual(self.contract_1_employee_4.state, 'open')
        self.assertEqual(self.contract_2_employee_4.state, 'cancel')
        
        payslip_oct = self.env['hr.payslip'].create({
            'employee_id': self.employee_4.id,
            'contract_id' : self.employee_4.contract_id.id,
            'struct_id': self.salary_structure.id,
            'date_from': '2021-10-01',
            'date_to': '2021-10-31',
            'company_id': self.env.company.id,
        })
        payslip_oct.compute_sheet()
        payslip_oct.action_payslip_verify()
        
        self.assertRecordValues(
            payslip_oct, 
            [{
                'timesheet_line_ids': [], 
                'timesheet_cost': 0
            }]
        )
        self.assertEqual(self.employee_4.timesheet_cost, 29.76)
    
    def test_12_01_hr_timesheet_payroll(self):
        """
        Case 12-TH1: Kiểm tra tạo chấm công khi đã có phiếu lương ở trạng thái Xác nhận/Hoàn thành
        - Input: 
            + Phiếu lương nhân viên 1 đã xác nhận thời gian 01-10-2021 đến 22/10/2021 
            + Nhân viên 1 chấm công ngày 23/10/2021
        - Output: Tạo thành công
        """
        self.payslip_employee_1.action_payslip_verify()
        timesheet = self.env['account.analytic.line'].create({
            'date': '2021-10-23',
            'name': 'Timesheet Employee 1',
            'project_id': self.project_1.id,
            'employee_id': self.employee_1.id,
            'unit_amount': 1,
        })
    
    def test_12_02_hr_timesheet_payroll(self):
        """
        Case 12-TH2: Kiểm tra tạo chấm công khi đã có phiếu lương ở trạng thái Dự thảo
        - Input: 
            + Phiếu lương nhân viên 1 đã xác nhận thời gian 01-10-2021 đến 22/10/2021 
            + Nhân viên 1 chấm công ngày 20/10/2021
        - Output: Tạo thành công, chấm công được tính toán vào phiếu lương
        """
        self.assertEqual(self.payslip_employee_1.state, 'draft')
        timesheet = self.env['account.analytic.line'].create({
            'date': '2021-10-20',
            'name': 'Timesheet Employee 1',
            'project_id': self.project_1.id,
            'employee_id': self.employee_1.id,
            'unit_amount': 1,
        })
        self.assertIn(timesheet, self.payslip_employee_1.timesheet_line_ids)
    
    def test_12_03_hr_timesheet_payroll(self):
        """
        Case 12-TH3: Kiểm tra tạo chấm công khi đã có phiếu lương ở trạng thái Xác nhận/Hoàn thành
        - Input: 
            + Phiếu lương nhân viên 1 đã xác nhận thời gian 01-10-2021 đến 22/10/2021 
            + Nhân viên 1 chấm công ngày 20/10/2021
        - Output: Tạo thất bại -> Xảy ra ngoại lệ đã có phiếu lương được xác nhận/ hoàn thành không thể chấm công
        """
        self.payslip_employee_1.action_payslip_verify()
        with self.assertRaises(UserError):
            timesheet = self.env['account.analytic.line'].create({
                'date': '2021-10-20',
                'name': 'Timesheet Employee 1',
                'project_id': self.project_1.id,
                'employee_id': self.employee_1.id,
                'unit_amount': 1,
            })
    
    def test_13_01_hr_timesheet_payroll(self):
        """
        Case 13: Kiểm tra Sửa thông tin chấm công khi đã liên kết với một phiếu lương
        TH1:
            - Input: 
                + Chấm công nhân viên 1 liên kết với phiếu lương ở trạng thái Dự thảo/ Huỷ bỏ
                + Thực hiện sửa thông tin chấm công: employee_id, amount, task_id, project_id
            - Output: Sửa thành công
        """
        self.assertIn(self.timesheet_1, self.payslip_employee_1.timesheet_line_ids)
        self.timesheet_1.write({'employee_id': self.employee_2.id})
    
    def test_13_02_hr_timesheet_payroll(self):
        """
        Case 13: Kiểm tra Sửa thông tin chấm công khi đã liên kết với một phiếu lương
        TH2:
            - Input: 
                + Chấm công nhân viên 1 liên kết với phiếu lương ở trạng thái Xác nhận/Hoàn thành
                + Thực hiện sửa thông tin chấm công: employee_id, amount, task_id, project_id
            - Output: Sửa thất bại -> Xảy ra ngoại lệ
        """
        self.assertIn(self.timesheet_1, self.payslip_employee_1.timesheet_line_ids)
        self.payslip_employee_1.action_payslip_verify()
        with self.assertRaises(UserError):
            self.timesheet_1.write({'employee_id': self.employee_2.id})
    
    def test_14_01_hr_timesheet_payroll(self):
        """
        Case 14: Kiểm tra Xoá chấm công khi đã liên kết với một phiếu lương
        TH1:
            - Input: 
                + Xoá Chấm công nhân viên 1 liên kết với phiếu lương ở trạng thái Dự thảo/ Huỷ bỏ
                + Thực hiện xoá chấm công
            - Output: Xoá thành công
        """
        self.assertIn(self.timesheet_1, self.payslip_employee_1.timesheet_line_ids)
        self.timesheet_1.unlink()
    
    def test_14_02_hr_timesheet_payroll(self):
        """
        Case 14: Kiểm tra Sửa thông tin chấm công khi đã liên kết với một phiếu lương
        TH2:
            - Input: 
                + Chấm công nhân viên 1 liên kết với phiếu lương ở trạng thái Xác nhận/Hoàn thành
                + Thực hiện sửa thông tin chấm công: employee_id, amount, task_id, project_id
            - Output: Sửa thất bại -> Xảy ra ngoại lệ
        """
        self.assertIn(self.timesheet_1, self.payslip_employee_1.timesheet_line_ids)
        self.payslip_employee_1.action_payslip_verify()
        with self.assertRaises(UserError):
            self.timesheet_1.unlink()
    
    def test_15_hr_timesheet_payroll(self):
        """
        Case 15: Kiểm tra cập nhật thông tin chi phí chấm công trên thông tin nhân viên và trên 
                chấm công với phiếu lương đánh dấu phiếu lương tháng 13
        - Input: Tạo phiếu lương nhân viên 1 đánh dấu là lương tháng 13
        - Output: Không cập nhật lại thông tin chi phí chấm công trên nhân viên và timesheet
        """
        timesheet_cost_employee = self.employee_1.timesheet_cost
        amount_timesheet_1 = self.timesheet_1.amount
        amount_timesheet_2 = self.timesheet_1.amount
        
        payslip_13th = self.env['hr.payslip'].create({
            'employee_id': self.employee_1.id,
            'contract_id' : self.employee_1.contract_id.id,
            'struct_id': self.salary_structure.id,
            'date_from': '2021-01-01',
            'date_to': '2021-12-31',
            'thirteen_month_pay_year': 2021,
            'thirteen_month_pay': True,
            'company_id': self.env.company.id,
        })
        payslip_13th.compute_sheet()
        payslip_13th.action_payslip_verify()
        self.assertEqual(self.employee_1.timesheet_cost, timesheet_cost_employee)
        self.assertRecordValues(
            self.timesheet_1 | self.timesheet_2, 
            [{'amount': amount_timesheet_1}, {'amount': amount_timesheet_2}]
        )
    
    def test_16_hr_timesheet_payroll(self):
        """
        Case 16: Kiểm tra cập nhật thông tin chi phí chấm công trên thông tin nhân viên và trên 
                chấm công với cấu trúc lương không đánh dấu "Update Employee Timesheet Cost"
        - Input: 
            + Phiếu lương nhân viên 1 với cấu trúc lương không đánh dấu "Update Employee Timesheet Cost"
        - Output: Không cập nhật thông tin chi phí chấm công trên nhân viên và timesheet
        """
        self.salary_structure.write({'update_employee_timesheet_cost': False})
        self.payslip_employee_1.compute_sheet()
        self.payslip_employee_1.action_payslip_verify()
        
        self.assertEqual(self.employee_1.timesheet_cost, 0)
        self.assertRecordValues(
            self.timesheet_1 | self.timesheet_2, 
            [{'amount': 0}, {'amount': 0}]
        )
    
    def test_17_hr_timesheet_payroll(self):
        """
        Case 17: Kiểm tra cập nhật thông tin chi phí chấm công bằng hành đồng "Update Employees Timesheet Cost" 
                trên thiết lập cấu hình Bảng lương
        Input: 
            + Thực hiện thay đổi hệ số chi phí công ty là 2
            + Thực hiện ấn "Update Employees Timesheet Cost"
        Output: Tất cả các phiếu lương đã được Xác nhận/ Hoàn thành được cập nhật lại chi phí chấm công, 
                cập nhật chi phí cho chấm công được giới thiệu bởi phiếu lương
        """
        self.payslip_employee_1.compute_sheet()
        self.payslip_employee_1.action_payslip_verify()
        self.assertEqual(self.payslip_employee_1.state, 'verify')
        #Thay đổi hệ số chi phí công ty là 2
        self.env.company.write({'general_overhead': 2})
        self.env.company._update_employee_timesheet_cost_from_payslips()
        timesheet_cost_payslip = round(self.payslip_employee_1.company_cost / self.payslip_employee_1.duty_working_hours * 2, 2) \
                                 * sum(self.payslip_employee_1.timesheet_line_ids.mapped('unit_amount'))
        amount_timesheet_1 = -1 * round(self.payslip_employee_1.company_cost / self.payslip_employee_1.duty_working_hours * 2, 2) \
                             * self.timesheet_1.unit_amount
        
        self.assertEqual(self.payslip_employee_1.timesheet_cost, timesheet_cost_payslip)
        self.assertEqual(self.timesheet_1.amount, amount_timesheet_1)
