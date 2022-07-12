from odoo.tests.common import tagged

from odoo.addons.to_hr_payroll.tests.common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestSalaryRule(TestPayrollCommon):

    def test_04_1_phone_allowance_for_tax_base_deduction_vietnam(self):
        """Case 1:Tets quy tắc lương Personal Tax Base Deduction có mã là "TBDED", mã python được cập nhật
        Input: Truy cập các quy tắc lương có mã là "TBDED", thuộc công ty quốc gia Việt Nam
            TH1: Các quy tắc lương trước khi cài đặt đã có đoạn mã "categories.PHONE" trong mã python
        Output:
            TH1: Mã python của quy tắc lương này không thay đổi
        """
        TBDED_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'TBDED'),
            ('company_id', '=', self.env.company.id),
            ])
        if 'categories.PHONE' not in TBDED_rule.amount_python_compute:
            TBDED_rule.write({
                'amount_python_compute': '%s%s' % (TBDED_rule.amount_python_compute, ' + categories.PHONE')
                })

        old_amount_python_compute = TBDED_rule.amount_python_compute

        self.env.company.write({'country_id': self.env.ref('base.vn').id})
        self.assertEqual(old_amount_python_compute, TBDED_rule.amount_python_compute)

    def test_04_2_phone_allowance_for_tax_base_deduction_vietnam(self):
        """Case 1:Tets quy tắc lương Personal Tax Base Deduction có mã là "TBDED", mã python được cập nhật
        Input: Truy cập các quy tắc lương có mã là "TBDED", thuộc công ty quốc gia Việt Nam
            Th2: Các quy tắc lương trước khi cài đặt chưa có đoạn mã "categories.PHONE" trong mã python
        Output:
            TH2: Mã python của quy tắc lương này  được cập nhật: cộng thêm đoạn mã "categories.PHONE"
        """
        TBDED_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'TBDED'),
            ('company_id', '=', self.env.company.id),
            ])
        if 'categories.PHONE' in TBDED_rule.amount_python_compute:
            TBDED_rule.write({
                'amount_python_compute': TBDED_rule.amount_python_compute.replace(' + categories.PHONE', '')
                })

        self.env.company.write({'country_id': self.env.ref('base.vn').id})
        self.assertIn('categories.PHONE', TBDED_rule.amount_python_compute)
