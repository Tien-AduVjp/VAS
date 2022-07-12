from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import CommonOverTimeApproval


@tagged('-at_install', 'post_install')
class TestOverTimePlan(CommonOverTimeApproval):

    def test_01_check_overtime_plan(self):
        """
        Case 1: Tạo kế hoạch tăng ca không gán với yêu cầu phê duyệt tăng ca nào
        Input: Tạo kế hoạch tăng ca của nhân viên có đủ dữ liệu chuẩn hợp đồng đang chạy, không gán với yêu cầu phê duyệt
        Output: Trạng thái của kế hoạch bằng False
        """
        self.assertFalse(self.overtime_plan_2.approval_id)
        self.assertFalse(self.overtime_plan_2.state)

    def test_02_check_overtime_plan(self):
        """
        Case 2: Tạo kế hoạch tăng ca gán với yêu cầu phê duyệt tăng ca
        Input: Tạo kế hoạch tăng ca của nhân viên có đủ dữ liệu chuẩn hợp đồng đang chạy, gán với yêu cầu phê duyệt
        Output: Trạng thái của kế hoạch bằng với trạng thái của yêu cầu phê duyệt
        """
        self.assertRecordValues(self.overtime_plan_1, [
                {
                    'approval_id': self.overtime_approval_request.id,
                    'state': self.overtime_approval_request.state
                }
            ])

    def test_03_check_overtime_plan(self):
        """
        Case 3: Tạo kế hoạch tăng ca gán với yêu cầu phê duyệt không phải kiểu tăng ca
        Input: Tạo kế hoạch tăng ca của nhân viên có đủ dữ liệu chuẩn hợp đồng đang chạy, gán với yêu cầu
        phê duyệt không phải kiểu tăng ca
        Output: Xảy ra ngoại lệ
        """
        with self.assertRaises(UserError):
            self.overtime_plan_2.write({
                'approval_id': self.generic_approval_request.id
            })

    def test_04_check_overtime_plan(self):
        """
        Case 4: Kiểm tra thay đổi trạng thái của kế hoạch tăng ca khi thay đổi yêu cầu phê duyệt tăng
        Input:
            + Kế hoạch tăng ca của nhân viên có đủ dữ liệu chuẩn hợp đồng đang chạy, gán với yêu cầu
            phê duyệt kiểu tăng ca ở trạng thái Dự thảo
            + Trường kỹ thuật 'Phê duyệt ngoại lệ' đánh dấu là False
            + Thực hiện xác nhận yêu cầu phê duyệt tăng ca
        Output: Kế hoạch tăng ca và yêu cầu phê duyệt tăng chuyển sang trạng thái Xác nhận
        """
        self.assertEqual(self.overtime_approval_request.state, 'draft')
        self.assertRecordValues(self.overtime_plan_1, [
                {
                    'approval_id': self.overtime_approval_request.id,
                    'state': 'draft',
                    'approval_state_exception': False
                }
            ])
        # change approval request to confirmed status
        self.overtime_approval_request.write({'state': 'confirm'})
        # status of overtime plan changed
        self.assertEqual(self.overtime_plan_1.state, 'confirm')

    def test_05_check_overtime_plan(self):
        """
        Case 5: Kiểm tra thay đổi trạng thái của kế hoạch tăng ca khi thay đổi yêu cầu phê duyệt tăng
        Input:
            + Kế hoạch tăng ca của nhân viên có đủ dữ liệu chuẩn hợp đồng đang chạy, gán với yêu cầu
            phê duyệt kiểu tăng ca ở trạng thái Dự thảo
            + Trường kỹ thuật 'Phê duyệt ngoại lệ' đánh dấu là True
            + Thực hiện xác nhận yêu cầu tăng ca
        Output: Kế hoạch tăng ca vẫn ở trạng thái 'Dự thảo', yêu cầu phê duyệt chuyển sang trạng thái Xác nhận
        """
        self.assertEqual(self.overtime_approval_request.state, 'draft')
        # 'approval_state_exception' field is ticked
        self.overtime_plan_1.write({'approval_state_exception': True})
        self.assertRecordValues(self.overtime_plan_1, [
                {
                    'approval_id': self.overtime_approval_request.id,
                    'state': 'draft',
                    'approval_state_exception': True
                }
            ])
        # change approval request to confirmed status
        self.overtime_approval_request.write({'state': 'confirm'})
        # status of overtime plan unchanged
        self.assertEqual(self.overtime_plan_1.state, 'draft')

    def test_06_check_overtime_plan(self):
        """
        Case 6: Xoá kế hoạch tăng ca không gán với yêu cầu phê duyệt tăng ca nào
        Input: Xoá kế hoạch tăng ca không gán với yêu cầu phê duyệt tăng ca nào
        Output: Xoá thành công
        """
        self.overtime_plan_2.unlink()

    def test_07_check_overtime_plan(self):
        """
        Case 7: Xoá kế hoạch tăng ca gán với yêu cầu phê duyệt tăng ca ở trạng thái dự thảo
        Input: Xoá kế hoạch tăng ca gán với yêu cầu phê duyệt tăng ca ở trạng thái dự thảo
        Output: Xoá thành công
        """
        self.assertRecordValues(self.overtime_plan_1, [
                {
                    'approval_id': self.overtime_approval_request.id,
                    'state': 'draft',
                }
            ])
        self.assertEqual(self.overtime_approval_request.state, 'draft')
        self.overtime_plan_1.unlink()

    def test_08_check_overtime_plan(self):
        """
        Case 8: Xoá kế hoạch tăng ca gán với yêu cầu phê duyệt tăng ca khác trạng thái dự thảo
        Input: Xoá kế hoạch tăng ca gán với yêu cầu phê duyệt tăng ca ở trạng thái dự thảo
        Output: Xoá thành công
        """
        self.assertEqual(self.overtime_plan_1.approval_id, self.overtime_approval_request)
        self.overtime_approval_request.write({'state': 'confirm'})
        self.assertEqual(self.overtime_approval_request.state, 'confirm')
        with self.assertRaises(UserError):
            self.overtime_plan_1.unlink()
