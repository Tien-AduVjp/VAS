from odoo.tests.common import tagged

from .common import CommonTimesheetApproval


@tagged('-at_install', 'post_install')
class TestTimesheetApprovals(CommonTimesheetApproval):

    def test_01_employee_approve_request(self):
        """
        Case 1: Thay đổi trạng thái của đề nghị phê duyệt, trạng thái của timesheet thay đổi tương ứng
        -Input:
            + Đề nghị phê duyệt có kiểu timesheets, có dòng timesheet ở trạng thái draft
            + Thực hiện xác nhận đề nghị
        -Output: Đề nghị chuyển trạng thái xác nhận, timesheet chuyển sang trạng thái xác nhận
        """
        self.timesheet_approve_request_employee.action_confirm()
        self.assertEqual(self.timesheet_approve_request_employee.state, 'confirm')
        self.assertFalse(self.timesheet_approve_request_employee.timesheet_line_ids.filtered(lambda t: t.timesheet_state != 'confirm'))

    def test_02_employee_approve_request(self):
        """
        Case 2: Kiểm tra trạng thái của timesheet khi approval_state_exception = True
        -Input:
            + timesheet có đề nghị phê duyệt được đánh dấu approval_state_exception = True
            + Thay đổi trạng thái của đề nghị phê duyệt
        Output: trạng thái timesheet không thay đổi theo trạng thái của đề nghị phê duyệt
        """
        self.assertEqual(self.timesheet_1.approval_id, self.timesheet_approve_request_employee)
        self.timesheet_1.write({'approval_state_exception': True})
        self.timesheet_approve_request_employee.write({'state': 'confirm'})
        self.assertNotEqual(self.timesheet_1.timesheet_state, 'confirm')
