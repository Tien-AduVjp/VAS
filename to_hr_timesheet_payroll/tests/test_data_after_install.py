from odoo.tests.common import tagged, SavepointCase


@tagged('-at_install', 'post_install')
class TestDataAfterInstall(SavepointCase):

    def test_01_data_after_install(self):
        """
        Case 1: Kiểm tra nhóm quy tắc lương "HR Timesheet Amount"
        - Input: Truy cập nhóm quy tắc lương
        - Output: Nhóm quy tắc lương "HR Timesheet Amount" được tạo ra mã là TIMESHEET
        """
        salary_rule_category = self.env['hr.salary.rule.category'].search([('code', '=', 'TIMESHEET')], limit=1)
        self.assertTrue(salary_rule_category)

    def test_02_data_after_install(self):
        """
        Case 1: Kiểm tra quy tắc lương "HR Timesheet Amount"
        - Input: Truy cập quy tắc lương
        - Output: Quy tắc lương "HR Timesheet Amount" được tạo ra mã là TIMESHEET
        """
        salary_rule_category = self.env['hr.salary.rule.category'].search([('code', '=', 'TIMESHEET')], limit=1)
        self.assertTrue(salary_rule_category)

    def test_03_check_data_after_install(self):
        """
        Case 3: Kiểm tra nhóm ghi nhận đóng góp "HR Timesheet"
        - Input: Truy cập nhóm ghi nhận đóng góp
        - Output: Nhóm ghi nhận đóng góp "HR Timesheet" được tạo ra
        """
        contribution_category = self.env.ref('to_hr_timesheet_payroll.hr_contribution_category_timesheet')
        self.assertTrue(contribution_category)

    def test_04_check_data_after_install(self):
        """
        Case 4: Kiểm tra ghi nhận đóng góp "HR Timesheet"
        - Input: Truy cập ghi nhận đóng góp
        - Output: Ghi nhận đóng góp "HR Timesheet" được tạo ra
        """
        contribution_category = self.env.ref('to_hr_timesheet_payroll.hr_contribution_category_timesheet')
        contribution= self.env['hr.contribution.register'].search([('category_id', '=', contribution_category.id)], limit=1)
        self.assertTrue(contribution)

    def test_05_check_data_after_install(self):
        """
        Case 4: Kiêm tra Hệ số chi phí quản lý chung phần Timesheet trong thiết lập chung của Payroll
        - Input: Truy cập Thiết lập -> Payroll -> khéo xuống phần Timesheet
        - Output: Hệ số chi phí quản lý chung mặc định là 1
        """
        self.assertEqual(self.env.company.general_overhead, 1)
