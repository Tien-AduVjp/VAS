from odoo.exceptions import ValidationError
from odoo.tests.common import tagged

from .common import CommonMaintenanceApproval


@tagged('-at_install', 'post_install')
class TestMaintenanceApprovals(CommonMaintenanceApproval):

    def test_01_employee_approve_request(self):
        """
        Case 1: Tạo yêu cầu phê duyệt bảo trì cho nhân viên 1, bỏ trống thiết bị
        Input: Tạo yêu cầu phê duyệt bảo trì cho nhân viên 1, bỏ trống thiết bị
        Output: Tạo thành công
        """
        self.assertRecordValues(self.maintenance_approval, [{
            'employee_id': self.employee1.id,
            'equipment_id': False
        }])

    def test_02_employee_approve_request(self):
        """
        Case 1: Yêu cầu phê duyệt bảo trì cho nhân viên 1, bỏ trống thiết bị, Thực hiện phê duyệt
        Input: Yêu cầu phê duyệt bảo trì cho nhân viên 1, bỏ trống thiết bị, Thực hiện phê duyệt
        Output: Xảy ra ngoại lệ
        """
        self.maintenance_approval.action_confirm()
        self.assertEqual(self.maintenance_approval.state, 'confirm')
        with self.assertRaises(ValidationError):
            self.maintenance_approval.action_validate()
