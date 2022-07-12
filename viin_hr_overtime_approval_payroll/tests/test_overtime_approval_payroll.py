from odoo.exceptions import UserError
from odoo.tests.common import tagged, Form

from odoo.addons.viin_hr_overtime_approval.tests.common import CommonOverTimeApproval


@tagged('-at_install', 'post_install')
class TestOvertimeApprovalPayroll(CommonOverTimeApproval):
    
    @classmethod
    def setUpClass(cls):
        super(TestOvertimeApprovalPayroll, cls).setUpClass()
        # Overtime Approval Request
        cls.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, cls.overtime_plan_1.ids)]
        })
        
        #Salary structure
        salary_structure = cls.env['hr.payroll.structure'].search([('code', '=', 'BASE')], limit=1)
        
        #Payslip Form
        cls.payslip_form = Form(cls.env['hr.payslip'])
        cls.payslip_form.employee_id = cls.employee_1
        cls.payslip_form.struct_id= salary_structure
        cls.payslip_employee_1 = cls.payslip_form.save()
    
    def test_01_overtime_approval_payroll(self):
        """
        Case 1: Kiểm tra kế hoạch tăng ca được nhận diện vào phiếu lương
        - Input: 
            + Tạo phiếu lương cho employee_1, với kế hoạch tăng ca không tham chiếu tới đề nghị phê duyệt tăng ca nào
            + Thời gian kế hoạch hợp lệ với phiếu lương   
        - Output: Tạo thành công phiếu lương, kế hoạch tăng ca hợp lệ được nhận diện vào phiếu lương 
        """
        payslip_employee_1 = self.payslip_form.save()
        self.assertIn(self.overtime_plan_2, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
        
    def test_02_overtime_approval_payroll(self):
        """
        Case 2: Kiểm tra kế hoạch tăng ca được nhận diện vào phiếu lương
        - Input: 
            + Tạo phiếu lương cho employee_1, với kế hoạch tăng ca được tham chiếu tới đề nghị phê duyệt tăng ca, ở trạng thái Dự thảo
            + Thời gian kế hoạch hợp lệ với phiếu lương   
        - Output: Tạo thành công phiếu lương, kế hoạch tăng ca không hợp lệ, không được nhận diện vào phiếu lương 
        """
        payslip_employee_1 = self.payslip_form.save()
        self.assertEqual(self.overtime_plan_1.state, 'draft')
        self.assertNotIn(self.overtime_plan_1, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
    
    def test_03_overtime_approval_payroll(self):
        """
        Case 3: Kiểm tra kế hoạch tăng ca được nhận diện vào phiếu lương
        - Input: 
            + Tạo phiếu lương cho employee_1, với kế hoạch tăng ca được tham chiếu tới đề nghị phê duyệt tăng ca, ở trạng thái Xác nhận
            + Thời gian kế hoạch hợp lệ với phiếu lương   
        - Output: Tạo thành công phiếu lương, kế hoạch tăng ca không hợp lệ, không được nhận diện vào phiếu lương 
        """
        self.overtime_approval_request.with_context(approval_action_call=True).write({'state': 'confirm'})
        payslip_employee_1 = self.payslip_form.save()
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertNotIn(self.overtime_plan_1, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
    
    def test_04_overtime_approval_payroll(self):
        """
        Case 4: Kiểm tra kế hoạch tăng ca được nhận diện vào phiếu lương
        - Input: 
            + Tạo phiếu lương cho employee_1, với kế hoạch tăng ca được tham chiếu tới đề nghị phê duyệt tăng ca, ở trạng thái Phê duyệt lần 1
            + Thời gian kế hoạch hợp lệ với phiếu lương   
        - Output: Tạo thành công phiếu lương, kế hoạch tăng ca không hợp lệ, không được nhận diện vào phiếu lương 
        """
        self.overtime_approval_request.with_context(approval_action_call=True).write({'state': 'validate1'})
        payslip_employee_1 = self.payslip_form.save()
        self.assertEqual(self.overtime_plan_1.state, 'validate1')
        self.assertNotIn(self.overtime_plan_1, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
    
    def test_05_overtime_approval_payroll(self):
        """
        Case 5: Kiểm tra kế hoạch tăng ca được nhận diện vào phiếu lương
        - Input: 
            + Tạo phiếu lương cho employee_1, với kế hoạch tăng ca được tham chiếu tới đề nghị phê duyệt tăng ca, ở trạng thái Đã huỷ
            + Thời gian kế hoạch hợp lệ với phiếu lương   
        - Output: Tạo thành công phiếu lương, kế hoạch tăng ca không hợp lệ, không được nhận diện vào phiếu lương 
        """
        self.overtime_approval_request.with_context(approval_action_call=True).write({'state': 'cancel'})
        payslip_employee_1 = self.payslip_form.save()
        self.assertEqual(self.overtime_plan_1.state, 'cancel')
        self.assertNotIn(self.overtime_plan_1, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
    
    def test_06_overtime_approval_payroll(self):
        """
        Case 6: Kiểm tra kế hoạch tăng ca được nhận diện vào phiếu lương
        - Input: 
            + Tạo phiếu lương cho employee_1, với kế hoạch tăng ca được tham chiếu tới đề nghị phê duyệt tăng ca, ở trạng thái Đã phê duyệt
            + Thời gian kế hoạch hợp lệ với phiếu lương   
        - Output: Tạo thành công phiếu lương, kế hoạch tăng ca hợp lệ được nhận diện vào phiếu lương 
        """
        self.overtime_approval_request.with_context(approval_action_call=True).write({'state': 'validate'})
        payslip_employee_1 = self.payslip_form.save()
        self.assertEqual(self.overtime_plan_1.state, 'validate')
        self.assertIn(self.overtime_plan_1, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
    
    def test_07_overtime_approval_payroll(self):
        """
        Case 7: Kiểm tra kế hoạch tăng ca được nhận diện vào phiếu lương
        - Input: 
            + Tạo phiếu lương cho employee_1, với kế hoạch tăng ca được tham chiếu tới đề nghị phê duyệt tăng ca, ở trạng thái Đã hoàn thành
            + Thời gian kế hoạch hợp lệ với phiếu lương   
        - Output: Tạo thành công phiếu lương, kế hoạch tăng ca hợp lệ được nhận diện vào phiếu lương 
        """
        self.overtime_approval_request.with_context(approval_action_call=True).write({'state': 'done'})
        payslip_employee_1 = self.payslip_form.save()
        self.assertEqual(self.overtime_plan_1.state, 'done')
        self.assertIn(self.overtime_plan_1, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
    
    def test_08_overtime_approval_payroll(self):
        """
        Case 8: Kiểm tra huỷ đề nghị phê duyệt tăng ca khi Kế hoạch tham đã tham chiếu tới phiếu lương ở trạng thái Dự thảo
        - Input: 
            + Phiếu lương employee_1 ở trạng thái dự thảo và có dòng tăng ca được tham chiếu tới đề nghị phê duyệt 
            đang ở trạng thái Đã phê duyệt/Hoàn Thành
            + Thực hiện từ chối kế hoạch tăng ca
        - Output: 
            + Từ chối thành công, dòng tăng ca không còn trên phiếu lương
        """
        self.overtime_approval_request.with_context(approval_action_call=True).write({'state': 'validate'})
        payslip_employee_1 = self.payslip_form.save()
        self.assertEqual(self.overtime_plan_1.state, 'validate')
        self.overtime_approval_request.action_refuse()
        self.assertNotIn(self.overtime_plan_1, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
    
    def test_09_overtime_approval_payroll(self):
        """
        Case 9: Kiểm tra huỷ đề nghị phê duyệt tăng ca khi Kế hoạch tham đã tham chiếu tới phiếu lương không ở trạng thái Dự thảo
        - Input: 
            + Phiếu lương employee_1 không ở trạng thái Dự thảo và có dòng tăng ca được tham chiếu tới đề nghị phê duyệt 
            đang ở trạng thái Đã phê duyệt/Hoàn Thành
            + Thực hiện từ chối kế hoạch tăng ca
        - Output: 
            + Từ chối thất bại -> Ngoại lệ xảy ra
        """
        self.overtime_approval_request.with_context(approval_action_call=True).write({'state': 'validate'})
        payslip_employee_1 = self.payslip_form.save()
        payslip_employee_1.action_payslip_verify()
        self.assertEqual(payslip_employee_1.state, 'verify')
        self.assertEqual(self.overtime_plan_1.state, 'validate')
        with self.assertRaises(UserError):
            self.overtime_approval_request.action_refuse()
    
    def test_10_overtime_approval_payroll(self):
        """
        Case 10: Xoá kế hoạch tăng ca tham chiếu tới phiếu lương ở trạng thái Dự thảo
        - Input: 
            + Kế hoạch tăng ca đã được nhận diện vào phiếu lương ở trạng thái Dự thảo
            + Thực hiện xoá kế hoạch tăng ca
        - Output: 
            + Xoá thành công, dòng tăng ca không còn trên phiếu lương
        """
        payslip_employee_1 = self.payslip_form.save()
        self.assertIn(self.overtime_plan_2, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
        self.overtime_plan_2.unlink()
        self.assertNotIn(self.overtime_plan_2, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
    
    def test_11_overtime_approval_payroll(self):
        """
        Case 11: Xoá kế hoạch tăng ca tham chiếu tới phiếu lương không ở trạng thái Dự thảo
        - Input: 
            + Kế hoạch tăng ca đã được nhận diện vào phiếu lương không ở trạng thái Dự thảo
        - Output: 
            + Xoá thất bại -> Xảy ra ngoại lệ
        """
        payslip_employee_1 = self.payslip_form.save()
        payslip_employee_1.action_payslip_verify()
        self.assertEqual(payslip_employee_1.state, 'verify')
        self.assertIn(self.overtime_plan_2, payslip_employee_1.overtime_plan_line_ids.overtime_plan_id)
        with self.assertRaises(UserError):
            self.overtime_plan_2.unlink()
