from odoo import fields
from odoo.addons.to_hr_payroll.tests.test_payroll_payslip_register_line import TestPayrollPayslipRegisterLine

"""
    Formulas on salary rules can change in other modules
        so tests related to payslip lines will run with tagged by default (at_install)
"""
class TestPayrollPayslipRegisterLineRegion(TestPayrollPayslipRegisterLine):
    @classmethod
    def setUpClass(cls):
        super(TestPayrollPayslipRegisterLineRegion, cls).setUpClass()

        social_insurance_type = cls.types.filtered(lambda r:r.code == 'SOCIAL_INSURANCE')
        cls.region_1 = cls.env.ref('viin_administrative_region.administrative_region_1')

        cls.contrib_social_insurance_v1 = cls.env['admin.region.payroll.contrib'].with_context(tracking_disable=True).create({
            'administrative_region_id': cls.region_1.id,
            'payroll_contribution_type_id': social_insurance_type.id,
            'min_contribution_base': 4000000,
            'max_contribution_base': 29800000,
            'max_contribution_employee': 0,
            'max_contribution_company': 0
        })

    def test_maximum_contribution_amount_1(self):
        """
        Nhân viên: không thiết lập vùng hành chính
            Kiểu đóng góp lương theo vùng hành chính: Vùng 1
                Số tiền tối đa cho cơ sở đóng góp: 29.800.000
                Số tiền tối thiểu cho cơ sở đóng góp: 4.000.000
                Số tiền đóng góp tối đa của nhân viên: 66666
                Số tiền đóng góp tối đa của công ty: 88888
        Hợp đồng Lương : 15.000.000
        Tạo phiếu lương từ 1/7 đến 31/7

        Output: các dòng đóng góp lương trên phiếu lương
        """

        self.contribution_registers.action_confirm()
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)

        self.assertRecordValues(
            payslip.hr_payslip_contribution_line_ids,
            [{  # by setUp
                'contribution_base': 15000000,
                'employee_contrib_rate': 2,
                'employee_contribution': 300000,
                'company_contrib_rate': 3,
                'company_contribution': 450000
            },
            {  # by setUp
                'contribution_base': 15000000,
                'employee_contrib_rate': 1.5,
                'employee_contribution': 225000,
                'company_contrib_rate': 3,
                'company_contribution': 450000
            },
            {  # by setUp
                'contribution_base': 15000000,
                'employee_contrib_rate': 1,
                'employee_contribution': 150000,
                'company_contrib_rate': 2,
                'company_contribution': 300000
            },
            {  # by setUp
                'contribution_base': 15000000,
                'employee_contrib_rate': 1.5,
                'employee_contribution': 225000,
                'company_contrib_rate': 2.5,
                'company_contribution': 375000
            }])

    def test_maximum_contribution_amount_2(self):
        """
        Nhân viên: Thiết lập vùng hành chính 1
        Hợp đồng có 4 kiểu đóng góp từ lương: kiểu Social Insurance có vùng hành chính 1 như sau:
            Kiểu đóng góp lương theo vùng hành chính (Social Insurance): Vùng 1
                Số tiền tối đa cho cơ sở đóng góp: 29.800.000
                Số tiền tối thiểu cho cơ sở đóng góp: 4.000.000
                Số tiền đóng góp tối đa của nhân viên: 0
                Số tiền đóng góp tối đa của công ty: 0
        Hợp đồng Lương : 15.000.000
        Tạo phiếu lương từ 1/7 đến 31/7

        Output: các dòng đóng góp lương trên phiếu lương
        """
        self.product_emp_A.write({
            'administrative_region_id': self.region_1.id
        })
        self.contribution_registers.action_confirm()
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)

        self.assertRecordValues(
            payslip.hr_payslip_contribution_line_ids,
            [{  # by setUp
                'contribution_base': 15000000,
                'employee_contrib_rate': 2,
                'employee_contribution': 300000,
                'company_contrib_rate': 3,
                'company_contribution': 450000
            },
            {  # by setUp
                'contribution_base': 15000000,
                'employee_contrib_rate': 1.5,
                'employee_contribution': 225000,
                'company_contrib_rate': 3,
                'company_contribution': 450000
            },
            {  # by setUp
                'contribution_base': 15000000,
                'employee_contrib_rate': 1,
                'employee_contribution': 150000,
                'company_contrib_rate': 2,
                'company_contribution': 300000
            },
            {  # by setUp
                'contribution_base': 15000000,
                'employee_contrib_rate': 1.5,
                'employee_contribution': 225000,
                'company_contrib_rate': 2.5,
                'company_contribution': 375000
            }])

    def test_maximum_contribution_amount_3(self):
        """
        Nhân viên: Thiết lập vùng hành chính 1
        Hợp đồng có 4 kiểu đóng góp từ lương: kiểu Social Insurance có vùng hành chính 1 như sau:
            Kiểu đóng góp lương theo vùng hành chính (Social Insurance): Vùng 1
                Số tiền tối đa cho cơ sở đóng góp: 29.800.000
                Số tiền tối thiểu cho cơ sở đóng góp: 4.000.000
                Số tiền đóng góp tối đa của nhân viên: 100000
                Số tiền đóng góp tối đa của công ty: 150000
        Đăng ký đóng góp kiểu Social Insurance của nhân viên :
            Số tiền nhân viên đóng góp tối đa:100000
            Số tiền công ty đóng góp tối đa:150000
        Hợp đồng Lương : 15.000.000
        Tạo phiếu lương từ 1/7 đến 31/7


        Output: các dòng đóng góp lương trên phiếu lương
            Riêng mã SOCIAL INSURANCE có số tiền của nhân viên là 100000, của công ty là 150000
        """
        self.product_emp_A.write({
            'administrative_region_id': self.region_1.id
        })

        self.contrib_social_insurance_v1.write({
            'max_contribution_employee': 100000,
            'max_contribution_company': 150000
        })
        # Social Insurance
        self.contribution_registers[0].write({
            'max_contribution_employee': 100000,
            'max_contribution_company': 150000
        })

        self.contribution_registers.action_confirm()
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-31'),
            self.contract_open_emp_A.id)
        self.assertRecordValues(
            payslip.hr_payslip_contribution_line_ids,
            [{  # by setUp
                'code': "SOCIAL_INSURANCE",
                'contribution_base': 15000000,
                'employee_contrib_rate': 2,
                'employee_contribution': 100000,
                'company_contrib_rate': 3,
                'company_contribution': 150000
            },
            {  # by setUp
                'code': "HEALTH_INSURANCE",
                'contribution_base': 15000000,
                'employee_contrib_rate': 1.5,
                'employee_contribution': 225000,
                'company_contrib_rate': 3,
                'company_contribution': 450000
            },
            {  # by setUp
                'code': "UNEMPLOYMENT_UNSURANCE",
                'contribution_base': 15000000,
                'employee_contrib_rate': 1,
                'employee_contribution': 150000,
                'company_contrib_rate': 2,
                'company_contribution': 300000
            },
            {  # by setUp
                'code': "LABOR_UNION",
                'contribution_base': 15000000,
                'employee_contrib_rate': 1.5,
                'employee_contribution': 225000,
                'company_contrib_rate': 2.5,
                'company_contribution': 375000
            }])
