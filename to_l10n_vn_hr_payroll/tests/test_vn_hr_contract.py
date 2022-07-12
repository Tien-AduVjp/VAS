from odoo.tests.common import tagged

from odoo.addons.to_hr_payroll.tests.common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestHrContract(TestPayrollCommon):

    def test_03_vn_contract(self):
        """Case 3: Test Hợp đồng nhân viên được cập nhật quy tắc thuế TNCN
        Input: Truy cập hợp đồng nhân viên quốc gia Việt Nam
        Output:
            TH1: Các hợp đồng chưa có thiết lập quy tắc thuế TNCN sẽ được thiết lập quy tắc thuế TNCN ở case 2
            TH2: CÁc hợp đồng đã thiết lập quy tắc Thuế TNCN không thay đổi
        """
        country_vn_id = self.env.ref('base.vn').id

        contract1 = self.contract_open_emp_A
        contract2 = self.contract_draft_emp_A
        address_home = contract1.employee_id.address_home_id
        contract1.employee_id.write({'address_id': address_home.id})
        address_home.write({'country_id': country_vn_id})
        contract2.write({'personal_tax_rule_id': False})

        expected_values = [
            {
                'country_id': contract1.personal_tax_rule_id.country_id.id,
                'personal_tax_policy': contract1.personal_tax_rule_id.personal_tax_policy,
                'apply_tax_base_deduction': contract1.personal_tax_rule_id.apply_tax_base_deduction,
                },
            {
                'country_id': country_vn_id,
                'personal_tax_policy': 'escalation',
                'apply_tax_base_deduction': True,
                'personal_tax_base_ded': 11000000,
                'dependent_tax_base_ded': 4400000,
                },
            ]

        self.env.company.write({'country_id': country_vn_id})
        self.env.company._generate_personal_tax_rules()

        self.assertRecordValues(
            (contract1 | contract2).personal_tax_rule_id,
            expected_values
            )
