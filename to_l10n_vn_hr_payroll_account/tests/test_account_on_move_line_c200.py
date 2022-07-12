from odoo import fields
from odoo.tests import tagged
from odoo.addons.to_hr_payroll.tests.common import TestPayrollCommon
from .common_c133 import TestCommonC133

@tagged('post_install', '-at_install')
class TestAccountOnEmployee133(TestCommonC133, TestPayrollCommon):

    def test_01_account_on_move_line(self):
        """
        phiếu lương có bút toán điều chỉnh

        'credit_account' trên quy tắc lương là False
        Nhân viên có tài khoản phải trả công nhân viên trên địa chỉ riêng tư
        => lấy mặc định ở địa chỉ riêng tư của nhân viên

        """
        self.product_emp_A.write({
            'company_id': self.company_c133.id
        })
        self.product_emp_A.address_home_id.write({
            'company_id': self.company_c133.id
        })
        self.contract_open_emp_A.write({
            'company_id': self.company_c133.id
        })
        self.contract_open_emp_A.struct_id.write({
            'company_id': self.company_c133.id
        })
        self.contract_open_emp_A.journal_id.write({
            'company_id': self.company_c133.id
        })
        self.contract_open_emp_A.struct_id.rule_ids.write({
            'company_id': self.company_c133.id
        })
        self.company_c133._update_vietnam_salary_rules_accounts()


        self.contract_open_emp_A.struct_id.rule_ids.write({
            'credit_account': False
        })
        payslip = self.env['hr.payslip'].with_context(tracking_disable=True).create({
            'employee_id': self.product_emp_A.id,
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-13'),
            'salary_cycle_id': self.company_c133.salary_cycle_id.id,
            'contract_id': self.contract_open_emp_A.id,
            'company_id': self.company_c133.id,
        })
        payslip.action_payslip_verify()

        pass
