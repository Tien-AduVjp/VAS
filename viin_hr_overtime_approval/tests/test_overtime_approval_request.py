from datetime import date

from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import CommonOverTimeApproval


@tagged('-at_install', 'post_install')
class TestOverTimeApprovalRequest(CommonOverTimeApproval):

    def test_01_check_overtime_approval_request(self):
        """
        Case 1: Tạo đề nghị phê duyệt tăng ca, với 2 kế hoạch tăng ca của cùng một nhân viên
        Input : Đề nghị phê duyệt tăng ca với dữ liệu tiêu chuẩn, kế hoạch cùng một nhân viên
        Output: Tạo thành công
        """
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_2.id])]
        })
        self.assertEqual(len(self.overtime_approval_request.overtime_plan_ids), 2)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.employee_id, self.employee_1)

    def test_02_check_overtime_approval_request(self):
        """
        Case 2: Tạo đề nghị phê duyệt tăng ca, với 2 kế hoạch tăng ca của 2 nhân viên khác nhau
        Input : Đề nghị phê duyệt tăng ca với dữ liệu tiêu chuẩn, kế hoạch của 2 nhân viên khác nhau
        Output: Tạo thành công
        """
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_3.id])]
        })
        self.assertEqual(len(self.overtime_approval_request.overtime_plan_ids), 2)
        self.assertEqual(self.overtime_approval_request.overtime_plan_ids.employee_id, self.employee_1 | self.employee_2)

    def test_03_check_overtime_approval_request(self):
        """
        Case 3: Xoá đề nghị phê duyệt tăng ca trạng thái Dự thảo
        Input: Đề nghị phê duyệt tăng có có dòng kế hoạch tăng ca, đề nghị ở trạng thái Dự thảo
        Output: Xoá thành công -> các dòng kế hoạch cũng bị xoá
        """
        self.assertEqual(self.overtime_approval_request.state, 'draft')
        self.overtime_approval_request.unlink()
        self.assertNotIn(self.overtime_plan_1, self.env['hr.overtime.plan'].search([]))

    def test_04_check_overtime_approval_request(self):
        """
        Case 4: Xác nhận đề nghị phê duyệt với 2 kế hoạch tăng ca cùng 1 nhân viên không trùng thời gian
        Input : Đề nghị phê duyệt tăng ca với dữ liệu tiêu chuẩn, kế hoạch cùng một nhân viên không bị trùng thời gian
        Output:
            + Xác nhận thành công
            + Chuyển trạng thái xác nhận
            + Dòng kế hoạch chuyển trạng thái xác nhận
        """
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_2.id])]
        })
        self.overtime_approval_request.action_confirm()
        self.assertEqual(self.overtime_approval_request.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')

    def test_05_check_overtime_approval_request(self):
        """
        Case 5: Xác nhận đề nghị phê duyệt với 2 kế hoạch tăng ca cùng 1 nhân viên trùng thời gian
        Input : Đề nghị phê duyệt tăng ca với dữ liệu tiêu chuẩn, kế hoạch cùng 1 nhân viên bị trùng thời gian
        Output: Xác nhận thất bại
        """
        overtime_plan_test_data = {
            'employee_id': self.employee_1.id,
            'reason_id': self.reason_general.id,
            'time_start': 17,
            'time_end': 18,
        }
        overtime_approval_request = self.overtime_approval_request.copy()
        overtime_approval_request.write({
            'overtime_plan_ids': [(0, 0, overtime_plan_test_data), (0, 0, overtime_plan_test_data)]
        })
        with self.assertRaises(UserError):
            overtime_approval_request.overtime_plan_ids.action_confirm()

    def test_06_check_overtime_approval_request(self):
        """
        Xác nhận đề nghị phê duyệt với 2 kế hoạch tăng của nhân viên khác nhau trùng thời gian
        Input : Đề nghị phê duyệt tăng ca với dữ liệu tiêu chuẩn, kế hoạch của nhân viên khác nhau bị trùng thời gian
        Output:
            + Xác nhận thành công
            + Chuyển trạng thái xác nhận
            + Dòng kế hoạch chuyển trạng thái xác nhận
        """
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_3.id])]
        })
        self.overtime_approval_request.action_confirm()
        self.assertEqual(self.overtime_approval_request.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_3.state, 'confirm')

    def test_07_check_overtime_approval_request(self):
        """
        Case 7: Kiểm tra phê duyệt đề nghị phê duyệt với 2 dòng kế hoạch tăng ca dữ liệu chuẩn
        Input :
            + Đề nghị phê duyệt tăng ca với dữ liệu tiêu chuẩn ở trạng thái xác nhận
            + Thực hiện hành động từ chối cho dòng kế hoạch 1
            + Thực hiện phê duyệt cho đề nghị tăng ca
        Output:
            + Phê duyệt thành công, đề nghị chuyển trạng thái đã phê duyệt
            + Dòng kế hoạch số 1 giữ nguyên trạng thái từ chối (Approval Status Exception = TRUE)
            + Dòng kế hoạch số 2 chuyển trạng thái đã xác nhận (Approval Status Exception = False)
        """
        self.overtime_approval_request.write({
            'overtime_plan_ids': [(6, 0, [self.overtime_plan_1.id, self.overtime_plan_2.id])],
            'state': 'confirm'
        })
        self.assertEqual(self.overtime_approval_request.state, 'confirm')
        self.assertEqual(self.overtime_plan_1.state, 'confirm')
        self.assertEqual(self.overtime_plan_2.state, 'confirm')

        # refuse the plan to overtime 1
        self.overtime_plan_1.action_refuse()
        # Approve overtime request
        self.overtime_approval_request.with_context(force_approval=True).action_validate()
        self.assertEqual(self.overtime_approval_request.state, 'validate')
        self.assertEqual(self.overtime_plan_1.state, 'refuse')
        self.assertTrue(self.overtime_plan_1.approval_state_exception)
        self.assertEqual(self.overtime_plan_2.state, 'validate')
        self.assertFalse(self.overtime_plan_2.approval_state_exception)

    def test_08_check_overtime_approval_request(self):
        # Plan duplication check is in the draft status overtime approval requirement
        """
        Kiểm tra trùng lặp với kế hoạch tăng ca nằm trong đề nghị tăng ca ở trạng thái Dự thảo
        Input:
            + Kế hoạch tăng ca 1 nằm trong đề nghị tăng ca ở trạng thái draft
            + Tạo kế hoạch tăng ca 2 giống kế hoạch tăng ca 1
        Output: Tạo thành công 2 kế hoạch tăng ca
        """
        overtime_plan_test_data = {
            'employee_id': self.employee_1.id,
            'recognition_mode': 'none',
            'reason_id': self.reason_general.id,
            'time_start': 17,
            'time_end': 18,
            'approval_id': self.overtime_approval_request.id
        }
        self.env['hr.overtime.plan'].create(overtime_plan_test_data)

    def test_09_check_overtime_approval_request(self):
        """
        Kiểm tra trùng lặp với kế hoạch tăng ca nằm trong 2 đề nghị phê duyệt tăng ca khác nhau
        Input:
            + Tạo kế hoạch tăng ca 1 nằm trong đề nghị phê duyệt tăng ca 1 ở trạng thái draft
            + Tạo kế hoạch tăng ca 2 giống kế hoạch tăng ca 1 và nằm ở đề nghị phê duyệt tăng ca 2 ở trạng thái draft
        Thực hiện hành động:
            + Xác nhận đề nghị phê duyệt tăng ca số 1
            + Xác nhận đề nghị phê duyệt tăng ca số 1
        Output:
            + Xác nhận đề nghị phê duyệt tăng ca số 1 thành công
            + Xác nhận đề nghị phê duyệt tăng ca số 1 thất bại
        """
        overtime_plan_test_data = {
            'employee_id': self.employee_1.id,
            'recognition_mode': 'none',
            'reason_id': self.reason_general.id,
            'time_start': 17,
            'time_end': 18,
        }
        overtime_approval_request_2 = self.overtime_approval_request.copy()
        overtime_approval_request_2.write({
            'overtime_plan_ids': [(0, 0, overtime_plan_test_data)]
        })
        # Confirm overtime plan 1
        self.overtime_approval_request.overtime_plan_ids.action_confirm()
        # Confirm overtime plan 2
        with self.assertRaises(UserError):
            overtime_approval_request_2.overtime_plan_ids.action_confirm()

    def test_10_check_overtime_approval_request(self):
        """
        Kiểm trùng lặp với 1 kế hoạch tăng nằm trong đề nghị phê duyệt tăng ca ở trạng thái dự thảo,
        và 1 kế hoạch tăng ca không nằm trong đề nghị phê duyệt
        Input:
            + Kế hoạch tăng ca 1 nằm trong đề nghị phê duyệt ở trạng thái dự thảo
            + Tạo kế hoạch tăng ca 2 giống với kế hoạch 1 không nằm trong đề nghị phê duyệt
        """
        self.assertRecordValues(self.overtime_plan_1, [
                {
                    'employee_id': self.employee_1.id,
                    'recognition_mode': 'none',
                    'reason_id': self.reason_general.id,
                    'time_start': 17,
                    'time_end': 18,
                    'approval_id': self.overtime_approval_request.id,
                    'state': 'draft',
                }
            ])
        self.env['hr.overtime.plan'].create({
            'employee_id': self.employee_1.id,
            'recognition_mode': 'none',
            'reason_id': self.reason_general.id,
            'time_start': 17,
            'time_end': 18,
        })

    def test_11_check_overtime_approval_request(self):
        """
        Case 11:Kiểm trùng lặp với 1 kế hoạch tăng nằm trong đề nghị phê duyệt tăng ca không ở
        trạng thái dự thảo (Confirm, First Approved, Approved, Done ), và 1 kế hoạch tăng ca không nằm trong đề nghị phê duyệt
        Input:
            + Kế hoạch tăng ca 1 nằm trong đề nghị phê duyệt không ở trạng thái dự thảo
            + Tạo kế hôạch tăng ca 2 giống với kế hoạch 1 không nằm trong đề nghị phê duyệt
        Output: kế hoạch tăng ca 2 tạo không thành công
        """
        self.overtime_approval_request.write({'state': 'confirm'})
        self.assertRecordValues(self.overtime_plan_1, [
                {
                    'employee_id': self.employee_1.id,
                    'recognition_mode': 'none',
                    'reason_id': self.reason_general.id,
                    'time_start': 17,
                    'time_end': 18,
                    'approval_id': self.overtime_approval_request.id,
                    'state': 'confirm',
                }
            ])
        with self.assertRaises(UserError):
            self.env['hr.overtime.plan'].create({
            'employee_id': self.employee_1.id,
            'recognition_mode': 'none',
            'reason_id': self.reason_general.id,
            'time_start': 17,
            'time_end': 18,
        })

    def test_12_check_overtime_approval_request(self):
        """
        Tính toán lại kế hoạch tăng ca trên đề nghị phê duyệt tăng ca ( test ví dụ một trường hợp)
        Input:
            + Đề nghị tăng ca có dòng kế hoạch tăng ca của nhân viên có hợp đồng với lương cơ bản 10000000
            + Thực hiện thay đổi lương cơ bản trong hợp đồng nhân viên thành 20000000
            + Thực hiện hành động tính toán lại kế hoạch tăng ca
        Output: Thông tin trên kế hoạch tăng ca thay đổi hợp lệ
        """
        planned_overtime_pay = sum(self.overtime_approval_request.overtime_plan_ids.mapped('planned_overtime_pay'))
        actual_overtime_pay = sum(self.overtime_approval_request.overtime_plan_ids.mapped('actual_overtime_pay'))
        self.assertEqual(sum(self.overtime_approval_request.overtime_plan_ids.contract_ids.mapped('wage')), self.contract_employee_1.wage)
        # Change base salary on employee contract
        self.contract_employee_1.write({'wage': 20000000})
        self.assertEqual(sum(self.overtime_approval_request.overtime_plan_ids.contract_ids.mapped('wage')), 20000000)
        # Recalculate the plan
        self.overtime_approval_request.action_recompute_overtime_plans()
        self.assertNotEqual(sum(self.overtime_approval_request.overtime_plan_ids.mapped('planned_overtime_pay')), planned_overtime_pay)
        self.assertNotEqual(sum(self.overtime_approval_request.overtime_plan_ids.mapped('actual_overtime_pay')), actual_overtime_pay)

    def test_13_check_overtime_approval_request(self):
        """
        Case 13: Kiểm tra đề nghị phê duyệt tăng ca với chức năng tạo kế hoạch hàng loạt
        ( Test ví dụ về chức năng tạo hàng loạt trên đề nghị tăng ca, còn lại sẽ test ở module viin_hr_overtime)
        Input:
            + Đề nghị phê duyệt tăng ca, thực hiện chức năng tạo kế hoạch hàng loạt ,
            trên wizard tạo hàng loạt có đánh dấu yêu cầu phê duyệt (dữ liệu tuỳ chọn)
            + Thực hiện tạo kế hoạch hàng loạt
        Output: Kế hoạch gán với đề nghị phê duyệt
        """
        user_admin = self.env.ref('base.user_admin')
        overtime_approval_request = self.overtime_approval_request.copy()
        context = {'default_approval_required': True, 'default_approval_id': overtime_approval_request.id}
        line_data = {
            'date': date.today(),
            'time_start': 20,
            'time_end': 21
        }
        mass_registration = self.env['hr.overtime.request.mass'].with_context(context).with_user(user_admin).create({
            'mode': 'department',
            'reason_id': self.reason_general.id,
            'line_ids': [(0, 0, line_data)]
        })
        mass_registration.action_schedule()
        plan_of_approval = self.env['hr.overtime.plan'].search([('approval_id','=', overtime_approval_request.id)])
        self.assertTrue(plan_of_approval)

    def test_14_check_overtime_approval_request(self):
        """
        Case 14: Kiểm tra đề nghị phê duyệt tăng ca với chức năng tạo kế hoạch hàng loạt
        ( Test ví dụ về chức năng tạo hàng loạt trên đề nghị tăng ca, còn lại sẽ test ở module viin_hr_overtime)
        Input:
            + Đề nghị phê duyệt tăng ca, thực hiện chức năng tạo kế hoạch hàng loạt ,
            trên wizard tạo hàng loạt không đánh dấu yêu cầu phê duyệt (dữ liệu tuỳ chọn)
            + Thực hiện tạo kế hoạch hàng loạt
        Output: Kế hoạch được tạo ra không gán với đề nghị phê duyệt tăng ca
        """
        user_admin = self.env.ref('base.user_admin')
        overtime_approval_request = self.overtime_approval_request.copy()
        context = {'default_approval_required': False, 'default_approval_id': overtime_approval_request.id}
        line_data = {
            'date': date.today(),
            'time_start': 20,
            'time_end': 21
        }
        mass_registration = self.env['hr.overtime.request.mass'].with_context(context).with_user(user_admin).create({
            'mode': 'department',
            'reason_id': self.reason_general.id,
            'line_ids': [(0, 0, line_data)]
        })

        mass_registration.action_schedule()
        plan_of_approval = self.env['hr.overtime.plan'].search([('approval_id','=', overtime_approval_request.id)])
        self.assertFalse(plan_of_approval)

    def test_15_check_overtime_approval_request(self):
        """
        Case 15: Kiểm tra hủy kế hoạch tăng ca
        Input: Kế hoạch tăng ca nằm trong đề nghị phê duyệt tăng ca
        Output: Huỷ thành công -> kế hoạch chuyển sang trạng thái huỷ
        """
        self.assertEqual(self.overtime_plan_1.approval_id, self.overtime_approval_request)
        self.assertEqual(self.overtime_plan_1.state, 'draft')
        self.overtime_plan_1.action_cancel()
        self.assertEqual(self.overtime_plan_1.state, 'cancel')

    def test_16_check_overtime_approval_request(self):
        """
        Case 16: Kiểm tra hủy kế hoạch tăng ca
        Input: Kế hoạch tăng không nằm trong đề nghị phê duyệt tăng ca
        Output: Huỷ thất bại
        """
        self.assertFalse(self.overtime_plan_2.approval_id)
        # Cancel plan
        with self.assertRaises(UserError):
            self.overtime_plan_2.action_cancel()
