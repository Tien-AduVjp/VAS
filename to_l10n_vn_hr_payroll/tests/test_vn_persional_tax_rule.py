from odoo.tests.common import tagged

from odoo.addons.to_hr_payroll.tests.common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestPersionalTaxRule(TestPayrollCommon):

    def test_01_flat_rate_for_vietnam(self):
        """Case 1: Test thông tin Quy tắc Thuế TNCN, kiểu Thuế suất cố định:
        Input: Truy cập menu Quy tắc Thuế TNCN
        Output:
            Có 2 bản ghi mới đc tạo:
                Quốc gia: Việt Nam
                Chính sách thuế: Cố định
                Áp dụng giảm trừ: Không
                Thuế suất cố định: 1 cái 10% và 1 cái 20%
        """
        country_vn_id = self.env.ref('base.vn').id
        self.env.company.write({'country_id': country_vn_id})

        flat_rate_rules = self.env['personal.tax.rule'].search([
            ('personal_tax_policy', '=', 'flat_rate'),
            ('country_id', '=', country_vn_id)
            ], limit=2)
        self.assertRecordValues(
            flat_rate_rules,
            [
                {
                    'apply_tax_base_deduction': False,
                    'personal_tax_flat_rate': 10.0,
                    },
                {
                    'apply_tax_base_deduction': False,
                    'personal_tax_flat_rate': 20.0,
                    },
                ]
            )

    def test_02_progressive_tax_table_for_vietnam(self):
        """Case 2: Test thông tin Quy tắc Thuế TNCN,  kiểu Biểu Thuế Lũy Tiến Từng Phần:
        Input: Truy cập menu Quy tắc Thuế TNCN
        Output:
            Có 1 bản ghi mới đc tạo:
                Quốc gia: Việt Nam
                Chính sách thuế: Biểu Thuế Lũy Tiến Từng Phần
                Áp dụng giảm trừ: có
                Giảm trừ cơ sở tính thuế TNCN: 11.000.000
                Giảm trừ cho mỗi người phụ thuộc: 4.400.000
                Biểu lũy thuế từng phần: 7 dòng
                Dòng 1: cơ sở tính thuế : 0, Tỷ lệ: 5%
                Dòng 2: cơ sở tính thuế : 5.000.000, Tỷ lệ: 10%
                Dòng 3: cơ sở tính thuế : 10.000.000, Tỷ lệ: 15%
                Dòng 4: cơ sở tính thuế : 18.000.000, Tỷ lệ: 20%
                Dòng 5: cơ sở tính thuế : 32.000.000, Tỷ lệ: 25%
                Dòng 6: cơ sở tính thuế : 52.000.000, Tỷ lệ: 30%
                Dòng 7: cơ sở tính thuế : 80.000.000, Tỷ lệ: 35%
            """
        country_vn_id = self.env.ref('base.vn').id
        self.env.company.write({'country_id': country_vn_id})

        progressive_rule = self.env['personal.tax.rule'].search([
            ('personal_tax_policy', '=', 'escalation'),
            ('country_id', '=', country_vn_id)
            ], limit=1)

        self.assertRecordValues(
            progressive_rule,
            [
                {
                    'apply_tax_base_deduction': True,
                    'personal_tax_base_ded': 11000000,
                    'dependent_tax_base_ded': 4400000,
                    },
                ]
            )

        self.assertEqual(len(progressive_rule.progress_ids), 7)
        self.assertRecordValues(
            progressive_rule.progress_ids,
            [
                {
                    'base': 0.0,
                    'rate': 5.0,
                    },
                {
                    'base': 5000000,
                    'rate': 10.0,
                    },
                {
                    'base': 10000000,
                    'rate': 15.0,
                    },
                {
                    'base': 18000000,
                    'rate': 20.0,
                    },
                {
                    'base': 32000000,
                    'rate': 25.0,
                    },
                {
                    'base': 52000000,
                    'rate': 30.0,
                    },
                {
                    'base': 80000000,
                    'rate': 35.0,
                    },
                ]
            )
