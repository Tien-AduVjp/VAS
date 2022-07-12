from odoo import fields
from odoo.tests import tagged

from odoo.addons.to_hr_payroll.tests.common import TestPayrollCommon

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestPartnerOnSalaryEntry(TestPayrollCommon, TestCommon):

    def test_01_1_partner_on_salary_entry(self):
        """Case 13: Test đối tác trên phát sinh bút toán khi xác nhận phiếu lương
        TH1: Nhân viên: không thiết lập địa chỉ riêng tư
            Output: Partner hiển thị trống
        """
        self.product_emp_A.write({'address_home_id': False})
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()
        self.assertFalse(payslip.move_id.line_ids.partner_id)

    def test_01_2_partner_on_salary_entry(self):
        """Case 13: Test đối tác trên phát sinh bút toán khi xác nhận phiếu lương
        TH2: Nhân viên: thiết lập điạ chỉ riêng tư
            Output: phát sinh của tài khoản 3341: có đối tác đã thiết lập địa chỉ riêng tư của nhân viên
        """
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()
        self.assertEqual(
            self.product_emp_A.address_home_id,
            payslip.move_id.line_ids.filtered(lambda l: l.account_id.code == '3341').partner_id)
