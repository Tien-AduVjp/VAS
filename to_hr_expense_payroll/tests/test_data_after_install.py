from odoo.tests.common import SavepointCase, tagged


@tagged('-at_install', 'post_install')
class TestDataAfterInstall(SavepointCase):

    def test_01_check_data_salary_rule_category(self):
        """
        Case 1: Kiêm tra nhóm quy tắc lương "Bồi hoàn chi tiêu"
        Input: Truy cập menu nhóm quy tắc lương
        Ouput: Nhóm quy tắc lương "Bồi hoàn chi tiêu" mã EXREIMB đc tạo
        """
        salary_rule_category = self.env['hr.salary.rule.category'].search([('code', '=', 'EXREIMB')], limit=1)
        self.assertRecordValues(
            salary_rule_category,
            [
                {
                    'name': 'HR Expense Reimbursement',
                    'code': 'EXREIMB',
                    }
                ]
            )

        """
        Case 2: Kiểm tra quy tắc lương "Tổng tiền Bồi hoàn chi tiêu"
        Input : Truy cập menu Quy tắc lương
        Output: Nhóm quy tắc lương "Tổng tiền Bồi hoàn chi tiêu", mã 'EXREIMB' đc tạo
        """
        salary_rule = self.env['hr.salary.rule'].search([('code', '=', 'EXREIMB')], limit=1)
        self.assertRecordValues(
            salary_rule,
            [
                {
                    'name': 'HR Expense Reimbursement Amount',
                    'sequence': 170,
                    'code': 'EXREIMB',
                    'category_id': salary_rule_category.id,
                    'condition_select': 'python',
                    'condition_python': 'result = True if payslip.hr_expense_ids else False',
                    'amount_select': 'code',
                    'appears_on_payslip': True,
                    'amount_python_compute': "result = sum(payslip.hr_expense_ids.mapped('total_amount'))",
                    }
                ]
            )
    def test_02_check_data_contribution_register(self):
        """
        Case 3: Kiêm tra Nhóm ghi nhận đóng góp "Bồi hoàn chi tiêu"
        Input : Truy cập menu Nhóm ghi nhận đóng góp
        Output: Nhóm ghi nhận đóng góp "Bồi hoàn chi tiêu" đc tạo
        Case 4: Kiêm tra Ghi nhận đóng góp "Bồi hoàn chi tiêu"
        Input : Truy cập menu ghi nhận đóng góp
        Output: Ghi nhận đóng góp "Bồi hoàn chi tiêu" đc tạo
        """
        contribution_register = self.env['hr.contribution.register'].search([('name', '=', 'HR Expense Reimbursement')], limit=1)
        self.assertRecordValues(
            contribution_register,
            [
                {
                    'name': 'HR Expense Reimbursement',
                    'partner_id': False,
                    'category_id': self.env.ref('to_hr_expense_payroll.hr_contribution_category_reimbursement').id,
                    }])

    def test_03_check_data_salary_rule_NET(self):
        """
        Case 5: Kiểm tra quy tắc lương "NET", mã python có thông tin chi tiêu
        Input: Truy cập quy tắc lương NET
        Output: Quy tắc lương NET
        Mã pyrthon có thêm đoạn code "+ categories.EXREIMB"
        """
        salary_rule_NET = self.env['hr.salary.rule'].search([('code', '=', 'NET')], limit=1)
        self.assertIn('+ categories.EXREIMB', salary_rule_NET.amount_python_compute)
