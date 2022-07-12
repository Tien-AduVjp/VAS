from odoo.exceptions import AccessError
from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install', 'access_rights')
class TestAccessRights(Common):

    def test_payroll_user_access_right_timsheet(self):
        """
        Case : Kiểm tra quyền truy cập của người dùng có quyền Payroll User với Timesheet
        - Input: Người dùng có quyền Payroll User
        - Output: Đọc, tạo, sửa, xoá Timesheet
        """
        self.timesheet_1.with_user(self.user_payroll).read()
        self.env['account.analytic.line'].with_user(self.user_payroll).create({
            'date': '2021-10-11',
            'name': 'Timesheet Employee 1',
            'project_id': self.project_1.id,
            'employee_id': self.employee_1.id,
            'unit_amount': 1,
        })
        self.timesheet_1.with_user(self.user_payroll).write({
            'unit_amount': 2,
        })
        self.timesheet_1.with_user(self.user_payroll).unlink()
