from odoo import fields
from odoo.tests import tagged

from odoo.addons.to_hr_payroll.tests.common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestVNPayrollContribution(TestPayrollCommon):

    def test_01_vn_contribution_type_with_SOCIAL_INSURANCE_code(self):
        """Case 1:  Test thông tin Kiểu đăng ký đóng góp từ lương, mã SOCIAL_INSURANCE
        Input: Truy cập kiểu đống góp từ lương Social Insurance, công ty quốc gia Việt nam
        Output: Các thông tin được cập nhật
            Tỷ lệ đóng góp của nhân viên: 8.0
            Tỷ lệ đóng góp của công ty: 17.5
            Phương pháp tính toán: Giới hạn số ngày không hưởng lương
            Số ngày không hưởng lương tối đa: 14.0
        """
        social_insurance_type = self.env['hr.payroll.contribution.type'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', 'SOCIAL_INSURANCE')
            ], limit=1)

        social_insurance_register_draft = self.create_contrib_register(
            self.product_emp_A,
            social_insurance_type,
            fields.Date.from_string('2021-3-1')
            )
        social_insurance_register_confirm = self.create_contrib_register(
            self.product_emp_A,
            social_insurance_type,
            fields.Date.from_string('2021-2-1')
            )
        social_insurance_register_confirm.action_confirm()

        expected_values = [
            {
                'employee_contrib_rate': 8.0,
                'company_contrib_rate': 17.5,
                'computation_method': 'max_unpaid_days',
                'max_unpaid_days': 14.0,
                },
            {
                'employee_contrib_rate': social_insurance_register_confirm.employee_contrib_rate,
                'company_contrib_rate': social_insurance_register_confirm.company_contrib_rate,
                'computation_method': social_insurance_register_confirm.computation_method,
                'max_unpaid_days': social_insurance_register_confirm.max_unpaid_days,
                }
            ]

        self.env.company.write({'country_id': self.env.ref('base.vn').id})

        self.assertRecordValues(
            social_insurance_type,
            expected_values[:1]
            )

        """Case 2: Tets thông tin Đăng ký đóng góp từ lương, có kiểu là Social Insurance
        Input: Truy cập các bản ghi đăng ký đóng góp từ lương, có kiểu là Social Insurance
            TH1: ở trạng thái dự thảo
            TH2: Khác trạng thái dự thảo
        Output:
            TH1: Các đăng ký tăng ca ở trạng thái dự thảo sẽ cập nhật các thông tin giống case 1
            TH2: Không thay đổi
        """
        self.assertRecordValues(
            social_insurance_register_draft | social_insurance_register_confirm,
            expected_values
            )

    def test_03_vn_contribution_type_with_HEALTH_INSURANCE_code(self):
        """Case 3:  Test thông tin Kiểu đăng ký đóng góp từ lương, mã HEALTH_INSURANCE
        Input: Truy cập kiểu đống góp từ lương Health Insurance, công ty quốc gia Việt nam
        Output: 
            Tỷ lệ đóng góp của nhân viên: 1.5
            Tỷ lệ đóng góp của công ty: 3.0
            Phương pháp tính toán: Giới hạn số ngày không hưởng lương
            Số ngày không hưởng lương tối đa: 14.0
        """
        health_insurance_type = self.env['hr.payroll.contribution.type'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', 'HEALTH_INSURANCE')
            ], limit=1)

        health_insurance_register_draft = self.create_contrib_register(
            self.product_emp_A,
            health_insurance_type,
            fields.Date.from_string('2021-3-1')
            )
        health_insurance_register_confirm = self.create_contrib_register(
            self.product_emp_A,
            health_insurance_type,
            fields.Date.from_string('2021-2-1')
            )
        health_insurance_register_confirm.action_confirm()

        expected_values = [
            {
                'employee_contrib_rate': 1.5,
                'company_contrib_rate': 3.0,
                'computation_method': 'max_unpaid_days',
                'max_unpaid_days': 14.0,
                },
            {
                'employee_contrib_rate': health_insurance_register_confirm.employee_contrib_rate,
                'company_contrib_rate': health_insurance_register_confirm.company_contrib_rate,
                'computation_method': health_insurance_register_confirm.computation_method,
                'max_unpaid_days': health_insurance_register_confirm.max_unpaid_days,
                }
            ]

        self.env.company.write({'country_id': self.env.ref('base.vn').id})

        self.assertRecordValues(
            health_insurance_type,
            expected_values[:1]
            )

        """Case 4: Tets thông tin Đăng ký đóng góp từ lương, có kiểu là Health Insurance
        Input: Truy cập các bản ghi đăng ký đóng góp từ lương, có kiểu là Health Insurance
            TH1: ở trạng thái dự thảo
            TH2: Khác trạng thái dự thảo
        Output:
            TH1: Các đăng ký tăng ca ở trạng thái dự thảo sẽ cập nhật các thông tin giống case 3
            TH2: Không thay đổi
        """
        self.assertRecordValues(
            health_insurance_register_draft | health_insurance_register_confirm,
            expected_values
            )

    def test_05_vn_contribution_type_with_UNEMPLOYMENT_UNSURANCE_code(self):
        """Case 5:  Test thông tin Kiểu đăng ký đóng góp từ lương, mã UNEMPLOYMENT_UNSURANCE
        Input: Truy cập kiểu đống góp từ lương Unemployment Insurance, công ty quốc gia Việt nam
        Output: 
            Tỷ lệ đóng góp của nhân viên: 1.0
            Tỷ lệ đóng góp của công ty: 1.0
            Phương pháp tính toán: Giới hạn số ngày không hưởng lương
            Số ngày không hưởng lương tối đa: 14.0
        """
        unemployment_insurance_type = self.env['hr.payroll.contribution.type'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', 'UNEMPLOYMENT_UNSURANCE')
            ], limit=1)

        unemployment_insurance_register_draft = self.create_contrib_register(
            self.product_emp_A,
            unemployment_insurance_type,
            fields.Date.from_string('2021-3-1')
            )
        unemployment_insurance_register_confirm = self.create_contrib_register(
            self.product_emp_A,
            unemployment_insurance_type,
            fields.Date.from_string('2021-2-1')
            )
        unemployment_insurance_register_confirm.action_confirm()

        expected_values = [
            {
                'employee_contrib_rate': 1.0,
                'company_contrib_rate': 1.0,
                'computation_method': 'max_unpaid_days',
                'max_unpaid_days': 14.0,
                },
            {
                'employee_contrib_rate': unemployment_insurance_register_confirm.employee_contrib_rate,
                'company_contrib_rate': unemployment_insurance_register_confirm.company_contrib_rate,
                'computation_method': unemployment_insurance_register_confirm.computation_method,
                'max_unpaid_days': unemployment_insurance_register_confirm.max_unpaid_days,
                }
            ]

        self.env.company.write({'country_id': self.env.ref('base.vn').id})

        self.assertRecordValues(
            unemployment_insurance_type,
            expected_values[:1]
            )
        """Case 6: Tets thông tin Đăng ký đóng góp từ lương, có kiểu là UnEmployment Unsurance
        Input: Truy cập các bản ghi đăng ký đóng góp từ lương, có kiểu là Health Insurance
            TH1: ở trạng thái dự thảo
            TH2: Khác trạng thái dự thảo
        Output:
            TH1: Các đăng ký tăng ca ở trạng thái dự thảo sẽ cập nhật các thông tin giống case 5
            TH2: Không thay đổi
        """
        self.assertRecordValues(
            unemployment_insurance_register_draft | unemployment_insurance_register_confirm,
            expected_values
            )

    def test_07_vn_contribution_type_with_LABOR_UNION_code(self):
        """Case 7:  Test thông tin Kiểu đăng ký đóng góp từ lương, mã LABOR_UNION
        Input: Truy cập kiểu đống góp từ lương Labor Union, công ty quốc gia Việt nam
        Output:
            Tỷ lệ đóng góp của nhân viên: 1.0
            Tỷ lệ đóng góp của công ty: 2.0
            Phương pháp tính toán: Giới hạn số ngày không hưởng lương
            Số ngày không hưởng lương tối đa: 14.0
        """
        labor_union_type = self.env['hr.payroll.contribution.type'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', 'LABOR_UNION')
            ], limit=1)

        labor_union_register_draft = self.create_contrib_register(
            self.product_emp_A,
            labor_union_type,
            fields.Date.from_string('2021-3-1')
            )
        labor_union_register_confirm = self.create_contrib_register(
            self.product_emp_A,
            labor_union_type,
            fields.Date.from_string('2021-2-1')
            )
        labor_union_register_confirm.action_confirm()

        expected_values = [
            {
                'employee_contrib_rate': 1.0,
                'company_contrib_rate': 2.0,
                'computation_method': 'max_unpaid_days',
                'max_unpaid_days': 14.0,
                },
            {
                'employee_contrib_rate': labor_union_register_confirm.employee_contrib_rate,
                'company_contrib_rate': labor_union_register_confirm.company_contrib_rate,
                'computation_method': labor_union_register_confirm.computation_method,
                'max_unpaid_days': labor_union_register_confirm.max_unpaid_days,
                }
            ]

        self.env.company.write({'country_id': self.env.ref('base.vn').id})

        self.assertRecordValues(
            labor_union_type,
            expected_values[:1]
            )
        """Case 8: Tets thông tin Đăng ký đóng góp từ lương, có kiểu là Labor Union
        Input: Truy cập các bản ghi đăng ký đóng góp từ lương, có kiểu là Labor Union
            TH1: ở trạng thái dự thảo
            TH2: Khác trạng thái dự thảo
        Output:
            TH1: Các đăng ký tăng ca ở trạng thái dự thảo sẽ cập nhật các thông tin giống case 7
            TH2: Không thay đổi
        """
        self.assertRecordValues(
            labor_union_register_draft | labor_union_register_confirm,
            expected_values
            )
