from odoo import fields
from odoo.tests.common import tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestPartner(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestPartner, cls).setUpClass()

        partner = cls.create_partner('Partner ABC')
        cls.register = cls.env['hr.contribution.register'].search([('company_id', '=', cls.env.company.id)], limit = 1)
        cls.register.write({
            'partner_id': partner.id
        })

        cls.rules_generate_account.write({
            'register_id': False
        })

    def test_priority_partner_1(self):
        """
        Quy tắc Lương có Đăng ký đóng góp có thiết lập đối tác
        Nhân viên không thiết lập địa chỉ cá nhân

        => Phát sinh sẽ có đối tác lấy từ đăng ký đóng góp trên quy tắc lương tương ứng
        """
        self.rule_babic = self.rules_generate_account.filtered(lambda r: r.code == 'BASIC')
        self.rule_babic.write({
            'register_id': self.register.id
        })
        self.product_emp_A.write({
            'address_home_id': False
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        move_lines = payslip.move_id.line_ids.filtered(lambda r:r.salary_rule_id == self.rule_babic)
        self.assertEqual(move_lines.partner_id, self.rule_babic.register_id.partner_id)

    def test_priority_partner_2(self):
        """
        Quy tắc Lương có Đăng ký đóng góp có thiết lập đối tác
        Nhân viên có thiết lập địa chỉ cá nhân

        => Phát sinh sẽ có đối tác lấy từ đăng ký đóng góp trên quy tắc lương tương ứng
        """
        self.rule_babic = self.rules_generate_account.filtered(lambda r: r.code == 'BASIC')
        self.rule_babic.write({
            'register_id': self.register.id
        })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        move_lines = payslip.move_id.line_ids.filtered(lambda r: r.salary_rule_id == self.rule_babic)
        self.assertEqual(move_lines.partner_id, self.rule_babic.register_id.partner_id)

    def test_priority_partner_3(self):
        """
        Quy tắc Lương không có Đăng ký đóng góp
        Nhân viên có thiết lập địa chỉ cá nhân
        Tài khoản Nợ-Có nằm trong nhóm Payable/Receivable

        => Phát sinh sẽ có đối tác lấy từ địa chỉ cá nhân của nhân viên
        """

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        for rule in self.rules_generate_account:
            move_lines = payslip.move_id.line_ids.filtered(lambda r: r.salary_rule_id in rule)
            self.assertTrue(move_lines.partner_id, 'Test partner on journal item not oke')
            self.assertEqual(
                move_lines.partner_id,
                payslip.employee_id.address_home_id,
                'Test partner on journal item not oke')

    def test_priority_partner_4(self):
        """
        Quy tắc Lương không có Đăng ký đóng góp
        Nhân viên có thiết lập địa chỉ cá nhân
        Tài khoản Nợ-Có không nằm trong nhóm Payable/Receivable

        => phát sinh kế toán liên quan không có đối tác
        """
        # account not in receivable/payable
        accounts = self.env['account.account'].search([
            ('user_type_id', 'not in', (self.account_type_receivable | self.account_type_payable).ids),
            ('company_id', '=', self.env.company.id)
            ], limit=2)

        rule_basic = self.rules_generate_account.filtered(lambda r: r.code == 'BASIC')
        rule_basic.write({
            'generate_account_move_line': True,
            'account_debit': accounts[0].id,
            'account_credit': accounts[1].id
        })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()
        move_lines = payslip.move_id.line_ids.filtered(lambda r: r.salary_rule_id in rule_basic)

        self.assertTrue(move_lines, 'Test journal item not oke')
        self.assertFalse(move_lines.partner_id, 'Test partner on journal item not oke')

    def test_priority_partner_5(self):
        """
        Quy tắc Lương không có Đăng ký đóng góp
        Nhân viên không thiết lập địa chỉ cá nhân

        => phát sinh kế toán liên quan không có đối tác
        """
        self.product_emp_A.write({
            'address_home_id': False
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()
        self.assertFalse(payslip.move_id.line_ids.partner_id, 'Test partner on journal item not oke')
