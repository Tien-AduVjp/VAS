from odoo.exceptions import UserError
from odoo.tests.common import tagged
from odoo import fields

from .common import CommonTimesheetApproval


@tagged('-at_install', 'post_install')
class TestTimesheetApprovalRequest(CommonTimesheetApproval):

    def test_01_check_timesheet_approval(self):
        self.assertEqual(self.timesheet_approve_request_employee.approval_type_id.type, 'timesheets')
        self.assertEqual(len(self.timesheet_approve_request_employee.timesheet_line_ids), 2)
        self.assertEqual(self.timesheet_approve_request_employee.timesheet_line_ids.employee_id, self.employee_1)

    def test_02_check_timesheet_approval(self):
        """
        Case 2: Tạo yêu cầu kiểu phê duyệt khác timesheets trên yêu cầu có timesheet
        Input:
            + Tạo Yêu cầu không phải kiểu timesheets có chứa dòng timesheet
        Output: Xảy ra ngoại lệ
        """
        with self.assertRaises(UserError):
            self.env['approval.request'].create({
                'title': 'Timesheet Approval Request Employee 1',
                'employee_id': self.employee_1.id,
                'approval_type_id': self.approve_type_generic.id,
                'company_id': self.env.company.id,
                'currency_id': self.env.company.currency_id.id,
                'timesheet_line_ids': [(4, self.timesheet_1.id, 0)],
                'deadline': fields.Date.today()
            })

    def test_03_check_timesheet_approval(self):
    # The request contains timekeeping of multiple employees
        """
        Case 3: Timesheet trên 1 yêu cầu phê duyệt không cùng một nhân viên
        Input: Yêu cầu phê duyệt có timesheet khác nhân viên
        Output: Xảy ra ngoại lệ
        """
        with self.assertRaises(UserError):
            self.timesheet_approve_request_employee.write({
                'timesheet_line_ids': [(4, self.timesheet_3.id, 0)]
            })

    def test_04_check_timesheet_approval(self):
        """
        Case 4: Xoá timesheet được gán tới đề nghị phê duyệt
        Input: Xoá timesheet được gán tới đề nghị phê duyệt
        Output: Xoá thành công, không còn trong đề nghị phê duyệt
        """
        self.assertIn(self.timesheet_1, self.timesheet_approve_request_employee.timesheet_line_ids)
        self.timesheet_1.unlink()
        self.assertNotIn(self.timesheet_1, self.timesheet_approve_request_employee.timesheet_line_ids)

    """
        Check execution at timekeeping request on model timesheet
    """
    def test_05_check_timesheet_approval(self):
        """
        Thực hiện chọn timesheet không ở trạng thái Draft ấn hành động tạo Yêu cầu Chấm Công
        -Input: Tích chọn timesheet không ở trạng thái Draft -> thực hiện hânh động tạo yêu cầu phê duyệt
        - Output: Thất bại -> Báo lỗi
        """
        self.timesheet_3.write({'timesheet_state': 'validate'})
        with self.assertRaises(UserError):
            timesheet_approval_wizard = self.env['timesheet.approval.request.create'].create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_3.id])],
                'employee_id': self.employee_2.id,
            })

    def test_06_check_timesheet_approval(self):
        """
        Case 6: Thực hiện chọn timesheet của cùng 1 nhân viên ấn hành động tạo Yêu cầu Chấm Công
        -Input: Tích chọn timesheet của cùng 1 nhân viên -> thực hiện hânh động tạo yêu cầu phê duyệt
        - Output: Tạo thành công -> timsheet trên yêu cầu là những timsheet đã tích chọn
        """
        self.env['timesheet.approval.request.create'].create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_3.id])],
                'employee_id': self.employee_2.id,
            })

    def test_07_check_timesheet_approval(self):
        """
        Case Thực hiện chọn timesheet của nhân viên khác nhau ấn hành động tạo Yêu cầu Chấm Công
        -Input: Tích chọn timesheet nhân viên khác nhau -> thực hiện hânh động tạo yêu cầu phê duyệt
        -Output: Thất bại -> Báo lỗi
        """
        with self.assertRaises(UserError):
            self.env['timesheet.approval.request.create'].create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_4.id, self.timesheet_3.id])],
            })

    def test_08_check_timesheet_approval(self):
        """
        Case 8: Thực hiện tạo yêu cầu chấm công cho timesheet của nhân viên cấp dưới
        -Input: Người dùng quản lý thực hiện chọn timesheet của nhân viên cấp dưới -> tạo yêu cầu phê duyệt
        -Output: Tạo thành công
        """
        self.employee_1.write({'user_id': self.user_1.id})
        self.employee_2.write({'parent_id': self.employee_1.id})
        self.env['timesheet.approval.request.create'].with_user(self.user_1).create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_3.id])],
                'employee_id': self.employee_2.id,
            })

    def test_09_check_timesheet_approval(self):
    # Create a request for timesheet approval for non-subordinates
        with self.assertRaises(UserError):
            self.env['timesheet.approval.request.create'].with_user(self.user_1).create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_4.id])],
                'employee_id': self.employee_3.id,
            })
