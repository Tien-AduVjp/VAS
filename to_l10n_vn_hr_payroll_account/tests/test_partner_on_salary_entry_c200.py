from odoo import fields
from odoo.tests import tagged

from .common import TestCommonC200


@tagged('post_install', '-at_install')
class TestPartnerOnSalaryEntry200(TestCommonC200):

    @classmethod
    def setUpClass(cls):
        super(TestPartnerOnSalaryEntry200, cls).setUpClass()
        cls.address_home_id = cls.env['res.partner'].with_context(tracking_disable=True).create({
            'name': 'Partner 1',
            'country_id': cls.company_c200.country_id.id,
            'company_id': cls.company_c200.id
        })
        cls.employee = cls.env['hr.employee'].with_context(tracking_disable=True).create({
            'name': 'Employee 1',
            'company_id': cls.company_c200.id,
            'address_home_id': False
        })
        cls.contract = cls.env['hr.contract'].search([('state', '=', 'open')], limit=1)
        struct = cls.env['hr.payroll.structure'].search([('company_id', '=', cls.company_c200.id)], limit=1)
        cls.journal = cls.env['account.journal'].search([('code', '=', 'SAL'), ('company_id', '=', cls.company_c200.id)], limit=1)

        tax_rule = cls.env['personal.tax.rule'].search([('country_id', '=', cls.company_c200.country_id.id)], limit=1)
        cls.contract = cls.env['hr.contract'].create({
            'name': 'New contract',
            'employee_id': cls.employee.id,
            'struct_id': struct.id,
            'journal_id': cls.journal.id,
            'company_id': cls.company_c200.id,
            'date_start': '2021-1-1',
            'state': 'open',
            'kanban_state': 'normal',
            'wage': 10000000,
            'personal_tax_rule_id': tax_rule.id
        })

    def test_01_1_partner_on_salary_entry(self):
        """Case 13: Test đối tác trên phát sinh bút toán khi xác nhận phiếu lương
        TH1: Nhân viên: không thiết lập địa chỉ riêng tư
            Output: Partner hiển thị trống
        """
        payslip = self.env['hr.payslip'].with_context(tracking_disable=True).create({
            'employee_id': self.employee.id,
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'salary_cycle_id': self.company_c200.salary_cycle_id.id,
            'contract_id': self.contract.id,
            'journal_id': self.journal.id,
            'company_id': self.company_c200.id,
        })
        payslip.action_payslip_verify()
        self.assertFalse(payslip.move_id.line_ids.partner_id)

    def test_01_2_partner_on_salary_entry(self):
        """Case 13: Test đối tác trên phát sinh bút toán khi xác nhận phiếu lương
        TH2: Nhân viên: thiết lập điạ chỉ riêng tư
            Output: phát sinh của tài khoản 334: có đối tác đã thiết lập địa chỉ riêng tư của nhân viên
        """
        self.employee.write({
            'address_home_id': self.address_home_id.id
        })
        payslip = self.env['hr.payslip'].with_context(tracking_disable=True).create({
            'employee_id': self.employee.id,
            'date_from': fields.Date.from_string('2021-7-1'),
            'date_to': fields.Date.from_string('2021-7-31'),
            'salary_cycle_id': self.company_c200.salary_cycle_id.id,
            'contract_id': self.contract.id,
            'journal_id': self.journal.id,
            'company_id': self.company_c200.id,
        })
        payslip.action_payslip_verify()

        move_line = payslip.move_id.line_ids.filtered(lambda l: l.account_id.code == '334')
        self.assertEqual(self.employee.address_home_id, move_line.partner_id)
