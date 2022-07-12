from odoo.tests.common import tagged

from .common import Common


@tagged('-at_install', 'post_install')
class TestContract(Common):

    def test_01_check_contract(self):
        """
        Case 1: Kiểm tra thay đổi trường "Payroll Timesheet Enabled" khi thay đổi vị trí công việc trên hợp đồng
        - Input:
            + Vị trí công việc có đánh dấu  "Payroll Timesheet Enabled"
            + Thay đổi Vị trí công việc trên hợp đồng nhân viên
        - Output: trường "Payroll Timesheet Enabled" trên hợp đồng được đánh dấu
        """
        self.contract_employee_3.write({'job_id': self.job_payroll_timesheet_enable.id})
        self.assertTrue(self.contract_employee_3.payroll_timesheet_enabled)

    def test_02_check_contract(self):
        """
        Case 1: Kiểm tra thay đổi trường "Payroll Timesheet Enabled" khi thay đổi vị trí công việc trên hợp đồng
        - Input:
            + Vị trí công việc có không đánh dấu  "Payroll Timesheet Enabled"
            + Thay đổi Vị trí công việc trên hợp đồng nhân viên
        - Output: trường "Payroll Timesheet Enabled" trên hợp đồng không được đánh dấu
        """
        self.contract_employee_3.write({'job_id': self.job_payroll_timesheet_disable.id})
        self.assertFalse(self.contract_employee_3.payroll_timesheet_enabled)
