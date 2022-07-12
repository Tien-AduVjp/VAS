from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.addons.to_hr_payroll.tests.test_payroll_contribution_register import TestPayrollContributionRegister


@tagged('post_install', '-at_install')
class TestPayrollContributionRegisterRegion(TestPayrollContributionRegister):
    
    @classmethod
    def setUpClass(cls):
        super(TestPayrollContributionRegisterRegion, cls).setUpClass()
        cls.region_1 = cls.env.ref('viin_administrative_region.administrative_region_1')
        cls.social_insurance = cls.env['hr.payroll.contribution.type'].search([('company_id', '=', cls.env.company.id), ('code', '=', 'SOCIAL_INSURANCE')], limit=4)
        cls.contrib_social_insurance_v1 = cls.env['admin.region.payroll.contrib'].with_context(tracking_disable=True).create({
            'administrative_region_id': cls.region_1.id,
            'payroll_contribution_type_id': cls.social_insurance.id,
            'min_contribution_base': 1000,
            'max_contribution_base': 5000,
            'max_contribution_employee': 150,
            'max_contribution_company': 200,
        })
    
    def test_contrains_contribution_amount(self):
        """
        Hợp đồng nhân viên A thiết lập vùng hành chính 1
        Kiểu Đóng góp SOCIAL_INSURANCE có đóng góp lương theo vùng 1
        
        Tạo đăng ký đóng đóng góp từ lương cho nhân viên A kiểu SOCIAL_INSURANCE
            1. cơ sở đóng góp: 6000
                => Lưu không thành công, thông báo ngoại lệ
            2. cơ sở đóng góp: 900
                => Lưu không thành công, thông báo ngoại lệ
            3. cơ sở đóng góp: 1500
                => Lưu thành công
            4. cơ sở đóng góp bởi nhân viên: 160
                => Lưu không thành công, thông báo ngoại lệ
            5. cơ sở đóng góp bởi nhân viên: 150
                => Lưu thành công
            6. cơ sở đóng góp bởi công ty: 250
                => Lưu không thành công, thông báo ngoại lệ
            7. cơ sở đóng góp bởi công ty: 200
                => Lưu thành công
        """
        self.contract_open_emp_A.write({
            'administrative_region_id': self.region_1.id
        })
        register = self.env['hr.payroll.contribution.register'].with_context(tracking_disable=True).create({
            'employee_id': self.product_emp_A.id,
            'type_id': self.type.id,
            'date_from': fields.Date.from_string('2021-1-1'),
            'state': 'draft',
            'employee_contrib_rate': 1.5,
            'company_contrib_rate': 1.5,
            'contribution_base': 1500,
            'max_contribution_employee': 150,
            'max_contribution_company': 200
        })
        self.contract_open_emp_A.write({
            'administrative_region_id': self.region_1.id
        })
        with self.assertRaises(ValidationError):
            register.write({'contribution_base': 6000})
        with self.assertRaises(ValidationError):
            register.write({'contribution_base': 900})
        with self.assertRaises(ValidationError):
            register.write({'max_contribution_employee': 160})
        with self.assertRaises(ValidationError):
            register.write({'max_contribution_company': 250})

    # 12. Lịch sử đăng ký đóng góp từ lương
    def test_contrib_register_history_lines_2(self):
        """
        Test số tiền đóng góp trên lịch sử đóng góp sau khi xác nhận đăng ký đóng góp
        Xác nhận Đăng ký đóng góp từ lương:
            Cơ sở tính toán 10.000
            Số tiền tối đa nhân viên đóng góp: 150
            Số tiền tối đa công ty đóng góp: 200
        """
        register_1 = self.create_contrib_register(self.product_emp_A, self.type, fields.Date.from_string('2021-3-1'))
        register_1.write({
            'contribution_base': 10000,
            'max_contribution_employee': 150,
            'max_contribution_company': 200
        })
        register_1.action_confirm()
        
        self.assertRecordValues(
            register_1.current_history_id,
            [{
                'contribution_base': 10000,
                'max_contribution_employee': 150,
                'max_contribution_company': 200
            }])
