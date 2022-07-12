from odoo import fields
from odoo.tests import tagged
from odoo.addons.to_hr_payroll.tests.common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestHRContract(TestPayrollCommon):

    @classmethod
    def setUpClass(cls):
        super(TestHRContract, cls).setUpClass()
        cls.region_1 = cls.env.ref('viin_administrative_region.administrative_region_1')
        cls.region_2 = cls.env.ref('viin_administrative_region.administrative_region_2')
        cls.contribution_types = cls.env['hr.payroll.contribution.type'].search([('company_id', '=', cls.env.company.id)], limit=4)

        cls.social_insurance = cls.contribution_types.filtered(lambda r:r.code == 'SOCIAL_INSURANCE')

        cls.contrib_social_insurance_v1 = cls.env['admin.region.payroll.contrib'].with_context(tracking_disable=True).create({
            'administrative_region_id': cls.region_1.id,
            'payroll_contribution_type_id': cls.social_insurance.id,
            'min_contribution_base': 1000,
            'max_contribution_base': 5000,
            'max_contribution_employee': 150,
            'max_contribution_company': 200,
        })

# 3. Hợp đồng: hr.contract
    def test_admin_region_payroll_contrib_ids_1(self):
        """
        Nhân viên: không thiết lập vùng hành chính
        Hợp đồng có 4 kiểu đóng góp từ lương
        Kiểu đóng góp SOCIAL_INSURANCE có Kiểu đóng góp lương theo vùng hành chính: Vùng 1
            Kiểu đóng góp lương theo vùng hành chính: Vùng 1
                Số tiền tối đa cho cơ sở đóng góp: 5000
                Số tiền tối thiểu cho cơ sở đóng góp: 1000
                Số tiền đóng góp tối đa của nhân viên: 150
                Số tiền đóng góp tối đa của công ty: 150
        Hợp đồng Lương : 10000

        Nhấn nút tạo đăng ký đóng góp từ lương
        => sinh ra các dòng đăng ký đóng góp từ lương với:
            số tiền cơ sở đóng góp là 10000
            số tiền nhân viên đóng góp tối đa là 0
            số tiền nhân viên đóng góp tối đa là 0
        """
        self.contract_draft_emp_A.write({
            'wage': 10000,
            'payroll_contribution_type_ids': [(6,0, self.contribution_types.ids)]
        })
        self.contract_draft_emp_A.generate_payroll_contribution_registers()
        self.assertRecordValues(
            self.contract_draft_emp_A.payroll_contribution_register_ids,
            [{
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            }])

    # 3. Hợp đồng: hr.contract
    def test_admin_region_payroll_contrib_ids_2(self):
        """
        Nhân viên: không thiết lập vùng hành chính
        Hợp đồng có 4 kiểu đóng góp từ lương
        Kiểu đóng góp SOCIAL_INSURANCE có Kiểu đóng góp lương theo vùng hành chính: Vùng 1
            Kiểu đóng góp lương theo vùng hành chính: Vùng 1
                Số tiền tối đa cho cơ sở đóng góp: 5000
                Số tiền tối thiểu cho cơ sở đóng góp: 1000
                Số tiền đóng góp tối đa của nhân viên: 150
                Số tiền đóng góp tối đa của công ty: 150
        Hợp đồng Lương : 500

        Nhấn nút tạo đăng ký đóng góp từ lương
        => sinh ra các dòng đăng ký đóng góp từ lương với:
                số tiền cơ sở đóng góp là 500
                số tiền nhân viên đóng góp tối đa là 0
                số tiền nhân viên đóng góp tối đa là 0
        """
        self.contract_draft_emp_A.write({
            'wage': 500,
            'payroll_contribution_type_ids': [(6,0, self.contribution_types.ids)]
        })
        self.contract_draft_emp_A.generate_payroll_contribution_registers()
        self.assertRecordValues(
            self.contract_draft_emp_A.payroll_contribution_register_ids,
            [{
                'contribution_base': 500,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 500,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 500,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 500,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            }])

    # 3. Hợp đồng: hr.contract
    def test_admin_region_payroll_contrib_ids_3(self):
        """
        Nhân viên: Có thiết lập vùng hành chính: Vùng 1
        Hợp đồng có 4 kiểu đóng góp từ lương
        Kiểu đóng góp SOCIAL_INSURANCE có Kiểu đóng góp lương theo vùng hành chính: Vùng 1
            Kiểu đóng góp lương theo vùng hành chính: Vùng 1
                Số tiền tối đa cho cơ sở đóng góp: 5000
                Số tiền tối thiểu cho cơ sở đóng góp: 1000
                Số tiền đóng góp tối đa của nhân viên: 150
                Số tiền đóng góp tối đa của công ty: 200
        Hợp đồng Lương : 10.000

        Nhấn nút tạo đăng ký đóng góp từ lương
        => sinh ra các dòng đăng ký đóng góp từ lương với:
                số tiền cơ sở đóng góp là 10.000
                số tiền nhân viên đóng góp tối đa là 0
                số tiền nhân viên đóng góp tối đa là 0
            Riêng dòng đóng góp kiểu SOCIAL_INSURANCE có:
                số tiền cơ sở đóng góp là 5.000
                số tiền nhân viên đóng góp tối đa là 150
                số tiền nhân viên đóng góp tối đa là 200
        """
        self.product_emp_A.write({
            'administrative_region_id': self.region_1.id
        })
        self.contract_draft_emp_A.write({
            'wage': 10000,
            'payroll_contribution_type_ids': [(6,0, self.contribution_types.ids)]
        })
        self.contract_draft_emp_A.generate_payroll_contribution_registers()
        self.assertRecordValues(
            self.contract_draft_emp_A.payroll_contribution_register_ids,
            [{
                'contribution_base': 5000,
                'max_contribution_employee': 150,
                'max_contribution_company': 200,
            },
            {
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            }])

    # 3. Hợp đồng: hr.contract
    def test_admin_region_payroll_contrib_ids_4(self):
        """
        Nhân viên: Có thiết lập vùng hành chính: Vùng 2
        Hợp đồng có 4 kiểu đóng góp từ lương
        Kiểu đóng góp SOCIAL_INSURANCE có Kiểu đóng góp lương theo vùng hành chính: Vùng 1
            Kiểu đóng góp lương theo vùng hành chính: Vùng 1
                Số tiền tối đa cho cơ sở đóng góp: 5000
                Số tiền tối thiểu cho cơ sở đóng góp: 1000
                Số tiền đóng góp tối đa của nhân viên: 150
                Số tiền đóng góp tối đa của công ty: 200
        Hợp đồng Lương : 10.000

        Nhấn nút tạo đăng ký đóng góp từ lương
        => sinh ra các dòng đăng ký đóng góp từ lương với:
            số tiền cơ sở đóng góp là 10.000
            số tiền nhân viên đóng góp tối đa là 0
            số tiền nhân viên đóng góp tối đa là 0
        """
        self.product_emp_A.write({
            'administrative_region_id': self.region_2.id
        })
        self.contract_draft_emp_A.write({
            'wage': 10000,
            'payroll_contribution_type_ids': [(6,0, self.contribution_types.ids)]
        })
        self.contract_draft_emp_A.generate_payroll_contribution_registers()
        self.assertRecordValues(
            self.contract_draft_emp_A.payroll_contribution_register_ids,
            [{
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            },
            {
                'contribution_base': 10000,
                'max_contribution_employee': 0,
                'max_contribution_company': 0,
            }])

    def test_contract_administrative_region(self):
        """
        Nhân viên: Có thiết lập vùng hành chính: Vùng hành chính 1
        1. Tạo hợp đồng:
            Hợp đồng mặc định có vùng hành chính là Vùng hành chính 1

        2. Chọn kiểu đăng ký đóng góp từ lương
            Hợp đồng đăng ký đóng góp từ lương theo vùng hành chính 1

        3. Thay đổi vùng hành chính trên hợp đồng thành vùng hành chính 2 và xác nhận hợp đồng
            Vùng hành chính của nhân viên cập nhật thành vùng hành chính 2
        """
        self.product_emp_A.write({
            'administrative_region_id': self.region_1.id
        })
        #1
        contract = self.create_contract(self.product_emp_A.id, fields.Date.to_date('2022-01-01'), state='draft')
        self.assertEqual(contract.administrative_region_id, self.region_1)

        # #2
        contract.write({'payroll_contribution_type_ids': [(6,0, self.social_insurance.ids)]})
        self.assertEqual(contract.admin_region_payroll_contrib_ids, self.contrib_social_insurance_v1)

        #3
        contract.write({'administrative_region_id': self.region_2.id})
        contract.action_start_contract()
        self.assertEqual(self.product_emp_A.administrative_region_id, self.region_2)
