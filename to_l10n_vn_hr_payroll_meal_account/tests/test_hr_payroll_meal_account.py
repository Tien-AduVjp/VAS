from datetime import date

from odoo.tests.common import SavepointCase, tagged


@tagged('-at_install', 'post_install')
class TestHrPayrollMealAccount(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestHrPayrollMealAccount, cls).setUpClass()
        cls.chart_template_vn = cls.env.ref('l10n_vn.vn_template')
        cls.chart_template_generic = cls.env.ref('l10n_generic_coa.configurable_chart_template')
        
        #Company
        cls.company_demo = cls.env['res.company'].create({
            'name': 'Company Demo',
        })
        cls.env.user.company_ids |= cls.company_demo
        cls.env.company = cls.company_demo
        #Working Time
        working_time = cls.env['resource.calendar'].create({
            'name': 'Working Time Company Demo',
            'company_id': cls.company_demo.id,
            'hours_per_day': 8
        })
        #Employee
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Employee Demo',
            'company_id': cls.company_demo.id,
            'resource_calendar_id': working_time.id
        })
        #Salary structure
        cls.salary_structure = cls.env['hr.payroll.structure'].search(
            [('company_id', '=', cls.company_demo.id), ('code', '=', 'BASE')], limit=1
        )
        #Contract
        cls.contract_employee = cls.env['hr.contract'].create({
            'name': 'Employee Demo',
            'employee_id': cls.employee.id,
            'company_id': cls.company_demo.id,
            'struct_id': cls.salary_structure.id,
            'date_start': '2021-10-10',
            'date_end': date.max,
            'wage': 10000000,
            'pay_per_meal': 30000
        })
        #Open Contract
        cls.contract_employee.action_start_contract()
        
        # Meal type
        cls.meal_type = cls.env.ref('to_hr_meal.lunch_for_everyone')
        
        # Meal line data
        meal_line_data = {
            'employee_id': cls.employee.id,
            'quantity': 1,
            'price': 35000,
            'meal_type_id': cls.meal_type.id,
            'company_id': cls.company_demo.id
        }
        #Meal Orders
        cls.meal_order = cls.env['hr.meal.order'].create({
            'meal_type_id': cls.meal_type.id,
            'scheduled_hour': 12,
            'company_id': cls.company_demo.id,
            'order_line_ids': [(0, 0, meal_line_data)],
            'state': 'confirmed'
        })
    
    def test_01_hr_payroll_meal_account(self):
        """
        Case 1: Kiểm tra quy tắc lương "Tổng khẩu trừ suất ăn" (Mã: MODER)
        - Input: Công ty không thiết lập COA Việt Nam
        - Output: Tài khoản ghi nợ và Tài khoản ghi có của quy tắc lương "Tổng khẩu trừ suất ăn" (Mã: MODED) 
        không được thiết lập là '1388 Phải thu khác', '3341 Phải trả công nhân viên'
        """
        self.chart_template_generic.try_loading(company = self.company_demo)
        self.assertEqual(self.chart_template_generic, self.company_demo.chart_template_id)
        meal_salary_rule = self.env['hr.salary.rule'].search([('code','=', 'MODED'), ('company_id', '=', self.company_demo.id)])
        self.assertRecordValues(
            meal_salary_rule, 
            [{'account_debit': False, 'account_credit': False}]
        )
    
    def test_02_hr_payroll_meal_account(self):
        """
        Case 2: Kiểm tra quy tắc lương "Tổng khẩu trừ suất ăn" (Mã: MODER)
        - Input: Công ty thiết lập COA là Việt Nam
        - Output: Tài khoản ghi nợ và Tài khoản ghi có của quy tắc lương "Tổng khẩu trừ suất ăn" (Mã: MODED) 
        thiết lập lần lượt là '1388 Phải thu khác', '3341 Phải trả công nhân viên'
        """
        self.chart_template_vn.try_loading(company = self.company_demo)
        self.assertEqual(self.chart_template_vn, self.company_demo.chart_template_id)
        meal_salary_rule = self.env['hr.salary.rule'].search([('code','=', 'MODED'), ('company_id', '=', self.company_demo.id)])
        account3341 = self.env['account.account'].search([('code', '=', '3341'), ('company_id', '=', self.company_demo.id)], limit=1)
        account1388 = self.env['account.account'].search([('code', '=', '1388'), ('company_id', '=', self.company_demo.id)], limit=1)
        self.assertRecordValues(
            meal_salary_rule, 
            [{'account_debit': account1388.id, 'account_credit': account3341.id}]
        )
    
    def test_03_hr_payroll_meal_account(self):
        """
        Case 3: Kiểm tra bút toán kế toán sinh ra sau khi xác nhận phiếu lương
        - Input:
            + Công ty thiết lập COA là Việt Nam
            + Đánh dấu phát sinh kế toán trên quy tắc lương "Tổng khẩu trừ suất ăn" (Mã: MODED)"
            + Thiết lập đối tác partner_meal trên Ghi nhận Đóng góp
            + Tài khoản ghi nợ và Tài khoản ghi có của quy tắc lương "Tổng khẩu trừ suất ăn" (Mã: MODED) 
        thiết lập lần lượt là '1388 Phải thu khác', '3341 Phải trả công nhân viên'
            + Xác nhận phiếu lương có dòng suất ăn hợp lệ, nhân viên phải trả là 30000
        - Output:
            - Sinh ra bút toán Có 1388 30000/ Nợ 3341 30000
            - Phát sinh của tài khoản 1388 có đối tác là partner_meal
        """
        self.chart_template_vn.try_loading(company = self.company_demo)
        self.assertEqual(self.chart_template_vn, self.company_demo.chart_template_id)

        partner_meal = self.env.ref('base.res_partner_18')

        self.env['hr.contribution.register'].search([
            ('category_id', '=', self.env.ref('to_hr_payroll_meal.hr_contribution_category_deduction').id),
            ('company_id', '=', self.company_demo.id)
            ], limit=1)\
            .write({'partner_id': partner_meal.id})

        #Payslip
        payslip_employee = self.env['hr.payslip'].create({
            'employee_id': self.employee.id,
            'contract_id' : self.contract_employee.id,
            'struct_id': self.salary_structure.id,
            'company_id': self.company_demo.id
        })
        meal_salary_rule = self.env['hr.salary.rule'].search([('code','=', 'MODED'), ('company_id', '=', self.company_demo.id)])
        meal_salary_rule.write({'generate_account_move_line': True})
        payslip_employee.compute_sheet()
        self.assertTrue(payslip_employee.meal_order_line_ids)
        payslip_employee.action_payslip_verify()
        
        journal_entry_account_1388 = payslip_employee.move_id.line_ids.filtered(
            lambda a: a.salary_rule_id.code == 'MODED' and a.account_id.code == '1388'
        )
        journal_entry_account_3341 = payslip_employee.move_id.line_ids.filtered(
            lambda a: a.salary_rule_id.code == 'MODED' and a.account_id.code == '3341'
        )
        self.assertRecordValues(
            (journal_entry_account_1388 | journal_entry_account_3341), 
            [
                {
                    'debit': 0,
                    'credit': 30000,
                },
                {
                    'debit': 30000,
                    'credit': 0,
                }
            ]
        )
        self.assertEqual(journal_entry_account_1388.partner_id, partner_meal)
