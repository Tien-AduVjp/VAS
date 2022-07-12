from psycopg2 import IntegrityError
from odoo import fields
from odoo.exceptions import ValidationError, UserError
from odoo.tools import mute_logger
from odoo.tests import tagged
from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestPayrollSalaryRule(TestPayrollCommon):
    
    # 5A. Nhóm Quy tắc lương
    def test_salary_rule_category_recusion(self):
        """
        Case 1: Test đệ quy
        """
        Category = self.env['hr.salary.rule.category']
        # Case 1: Test đệ quy
        category1 = Category.create({'name': 'Test 1', 'code': 'TEST1'})
        category2 = Category.create({'name': 'Test 2', 'code': 'TEST2', 'parent_id': category1.id})
        category3 = Category.create({'name': 'Test 3', 'code': 'TEST3', 'parent_id': category2.id})
        with self.assertRaises(ValidationError):
            with self.cr.savepoint():
                category1.write({'parent_id': category2.id})
                category1.write({'parent_id': category3.id})
                category2.write({'parent_id': category3.id})
    
    # 5A. Nhóm Quy tắc lương
    @mute_logger('odoo.sql_db')
    def test_salary_rule_category_code_unique_1(self):
        """
        Case 2: Test trường Mã  (Code) là duy nhất theo công ty
            TH1: Tạo 1 nhóm quy tắc lương mới, trùng với mã của nhóm quy tắc trên hệ thống cùng công ty
                => Ngoại lệ
        """
        Category = self.env['hr.salary.rule.category']
        Category.create({'name': 'Test 1', 'code': 'TEST1'})
        with self.assertRaises(IntegrityError):
            Category.create({'name': 'Test 4', 'code': 'TEST1'})
    
    # 5A. Nhóm Quy tắc lương
    def test_salary_rule_category_code_unique_2(self):
        """
        Case 2: Test trường Mã  (Code) là duy nhất theo công ty
            TH2: Tạo 1 nhóm quy tắc lương mới, trùng với mã của nhóm quy tắc trên hệ thống khác công ty
                => Thành công
        """
        Category = self.env['hr.salary.rule.category']
        Category.create({'name': 'Test 1', 'code': 'TEST1'})
        company2 = self.env['res.company'].create({'name': 'Company 2'})
        
        category = Category.create({'name': 'Test 3', 'code': 'TEST1', 'company_id': company2.id})
        self.assertTrue(category, 'Test rule category code not oke')
    
    # 5A. Nhóm Quy tắc lương
    def test_salary_rule_category_rule_count(self):
        """
        Case 3: Test số lượng quy tắc lương
        """
        Category = self.env['hr.salary.rule.category']
        category1 = Category.create({'name': 'Test 1', 'code': 'TEST1'})
        category2 = Category.create({'name': 'Test 2', 'code': 'TEST2'})
        
        vals = [
            self.prepare_rule_data('Test Rule 1', 'R1', self.structure_base.id, category1.id),
            self.prepare_rule_data('Test Rule 2', 'R2', self.structure_base.id, category2.id),
            self.prepare_rule_data('Test Rule 3', 'R3', self.structure_base.id, category1.id),
            self.prepare_rule_data('Test Rule 4', 'R4', self.structure_base.id, category2.id),
            self.prepare_rule_data('Test Rule 5', 'R5', self.structure_base.id, category2.id), 
        ]
        self.env['hr.salary.rule'].create(vals)
        self.assertEqual(2, category1.salary_rules_count, 'Test the number of salary rules of the category not oke')
        self.assertEqual(3, category2.salary_rules_count, 'Test the number of salary rules of the category not oke')
    
    # 5B. Quy tắc lương
    def test_salary_rule_reset(self):
        """
        Case 1: Test nút "Reset"
        Output: 
            Đặt lại quy tắc lương này về giá trị mặc định như khi cài mới, 
            tất cả các tùy chỉnh sẽ bị mất đi, 
            áp dụng cho 1 số trường sau: Điều kiện dựa trên, điều kiện Python, Kiểu tổng, Mã Python, Xuất hiện trong phiếu lương
        """
        structure_base = self.structure_base
        rules = structure_base.rule_ids
        rule_data = self.env.company._parepare_salary_rules_vals_list(structure_base)
        rules.write({
            'condition_select': 'range',
            'condition_python': 'Test condition_python',
            'amount_select': 'code',
            'appears_on_payslip': False,
            'amount_python_compute': 'Test amount_python_compute',
        })
        rules.action_reset()
        
        # test
        for data in rule_data:
            rule = rules.filtered(lambda r:r.code == data['code'])
            if rule:
                vals = {}
                if data.get('condition_select', False):
                    vals['condition_select'] = data['condition_select']
                if data.get('condition_python', False):
                    vals['condition_python'] = data['condition_python']
                if data.get('amount_select', False):
                    vals['amount_select'] = data['amount_select']
                if data.get('appears_on_payslip', False):
                    vals['appears_on_payslip'] = data['appears_on_payslip']
                if data.get('amount_python_compute', False):
                    vals['amount_python_compute'] = data['amount_python_compute']
                if vals:
                    self.assertRecordValues(rule, [vals])
    
    # 5B. Quy tắc lương
    def test_salary_rule_unlink_1(self):
        """
        Case 3: Test Xóa quy tắc lương
            TH1: quy tắc lương có liên quan đến dòng phiếu lương
                => Thất bại, thông báo ngoại lệ
        """
        payslip1 = self.create_payslip(
            self.product_emp_A.id, 
            fields.Date.from_string('2021-07-01'), 
            fields.Date.from_string('2021-07-30'), 
            self.contract_open_emp_A.id)
        payslip1.compute_sheet()
        
        rule_ids = payslip1.line_ids.salary_rule_id
        self.assertRaises(UserError, rule_ids.unlink)
    
    # 5B. Quy tắc lương
    def test_salary_rule_unlink_2(self):
        """
        Case 3: Test Xóa quy tắc lương
            TH2: Quy tắc lương không liên quan đến bất kỳ dòng phiếu lương nào
                => Thành công
        """
        rules = self.env['hr.salary.rule'].search([('payslip_line_ids', '=', False)])
        self.assertTrue(rules) # ensure we have rules found
        self.assertTrue(rules.unlink(), 'Test unlink Salary Rule not oke')
    
    # 5B. Quy tắc lương
    def test_salary_rule_unlink_3(self):
        """
        Case 3: Test Xóa quy tắc lương
            TH3: Test unlink with input rule lines
                => Thành công, các quy tắc nhập ngoài cũng sẽ bị xóa
        """
        deletable_rule = self.env['hr.salary.rule'].search([('payslip_line_ids', '=', False)], limit=1)
        self.assertTrue(deletable_rule) # ensure we have a rule found
        rule_input = self.env['hr.rule.input'].create({'name': 'Test 1', 'code': 'T1', 'salary_rule_id': deletable_rule.id})
        deletable_rule.unlink()
        self.assertFalse(rule_input.exists(), 'Test unlink Salary Rule not oke')

    # 5B. Quy tắc lương
    def test_salary_rule_contribution_register_1(self):
        """
        Case 2: Test Tạo bản ghi với trường "Ghi nhận đóng góp"
            TH1: Tạo quy tắc lương, không chọn đăng ký đóng góp
                => Tạo thành công
        """
        rule_category = self.env['hr.salary.rule.category'].search([('company_id', '=', self.env.company.id)], limit=1)
        rule = self.create_rule('Test Rule 1', 'T1', self.structure_base.id, rule_category.id)
        self.assertTrue(rule, 'Test create Rule with Contribution Register not oke')
    
    # 5B. Quy tắc lương
    def test_salary_rule_contribution_register_2(self):
        """
        Case 2: Test Tạo bản ghi với trường "Ghi nhận đóng góp"
            TH2: Input:
                    Tạo quy tắc lương, chọn đăng ký đóng góp. 
                    Nhóm của Ghi nhận đóng góp không đánh dấu là "bắt buộc yêu cầu đối tác"
            Output: Tạo thành công
        """
        rule_category = self.env['hr.salary.rule.category'].search([('company_id', '=', self.env.company.id)], limit=1)
        contribution = self.env['hr.contribution.register'].search([('company_id', '=', self.env.company.id)], limit=1)
        contribution.category_id.write({'partner_required': False})
        
        rule = self.create_rule('Test Rule 1', 'T1', self.structure_base.id, rule_category.id, register_id=contribution.id)
        self.assertTrue(rule, 'Test create Rule with Contribution Register not oke')
    
    # 5B. Quy tắc lương
    def test_salary_rule_contribution_register_3(self):
        """
        Case 2: Test Tạo bản ghi với trường "Ghi nhận đóng góp"
            TH3: Input:
                    Tạo quy tắc lương, chọn đăng ký đóng góp. 
                    Nhóm của Ghi nhận đóng góp đánh dấu là "bắt buộc yêu cầu đối tác", và có chọn đối tác
            Output: Tạo thành công
        """
        rule_category = self.env['hr.salary.rule.category'].search([('company_id', '=', self.env.company.id)], limit=1)
        contribution = self.env['hr.contribution.register'].search([('company_id', '=', self.env.company.id)], limit=1)
        contribution.category_id.write({'partner_required': True})
        partner = self.env['res.partner'].sudo().create({'name': 'Test Partner 1'})
        contribution.write({'partner_id': partner.id})
        
        rule = self.create_rule('Test Rule 1', 'T1', self.structure_base.id, rule_category.id, register_id=contribution.id)
        self.assertTrue(rule, 'Test create Rule with Contribution Register not oke')
    
    # 5B. Quy tắc lương
    def test_salary_rule_contribution_register_4(self):
        """
        Case 2: Test Tạo bản ghi với trường "Ghi nhận đóng góp"
            TH4: Input:
                    Tạo quy tắc lương, chọn đăng ký đóng góp. 
                    Nhóm của Ghi nhận đóng góp đánh dấu là "bắt buộc yêu cầu đối tác", và có không chọn đối tác
            Output: Tạo không thành công
        """
        rule_category = self.env['hr.salary.rule.category'].search([('company_id', '=', self.env.company.id)], limit=1)
        contribution = self.env['hr.contribution.register'].search([('company_id', '=', self.env.company.id)], limit=1)
        contribution.category_id.write({'partner_required': True})
        
        with self.assertRaises(ValidationError):
            self.create_rule('Test Rule 1', 'T1', self.structure_base.id, rule_category.id, register_id=contribution.id)
