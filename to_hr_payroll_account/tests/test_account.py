from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestAccount(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestAccount, cls).setUpClass()

        Analytic = cls.env['account.analytic.tag']
        analytic_accounts = cls.env['account.analytic.account'].search([('company_id', '=', cls.env.company.id)], limit=3)

        # set accounts on salary rules
        cls.analytic_tag_1 = Analytic.create([{'name': 'Tag 1'}]) 
        cls.analytic_account_1 = analytic_accounts[0]
        cls.rules_generate_account.write({
            'generate_account_move_line': True,
            'account_debit': cls.account_payable.id,
            'account_credit': cls.account_receivable.id,
            'anylytic_option': 'debit_account',
            'analytic_account_id': cls.analytic_account_1.id,
            'analytic_tag_ids': [(6, 0, cls.analytic_tag_1.ids)],
            })

        # set accounts on contracts
        cls.analytic_tag_2 = Analytic.create({'name': 'Tag 2'})
        cls.analytic_account_2 = analytic_accounts[1]
        cls.contract_open_emp_A.write({
            'analytic_account_id': cls.analytic_account_2.id,
            'analytic_tag_ids': [(6, 0, cls.analytic_tag_2.ids)],
            'account_expense_id': cls.account_payable.id,
            })

        # set accounts on Department
        cls.analytic_tag_3 = Analytic.create({'name': 'Tag 3'})
        cls.analytic_account_3 = analytic_accounts[2]
        cls.contract_open_emp_A.department_id.write({
            'analytic_account_id': cls.analytic_account_3.id,
            'analytic_tag_ids': [(6, 0, cls.analytic_tag_3.ids)],
            'account_expense_id': cls.account_payable.id,
            })

        cls.salary_journal = cls.env['account.journal'].search([
            ('company_id', '=', cls.env.company.id),
            ('code', '=', 'SAL')
            ], limit = 1)
        cls.salary_journal.write({
            'default_debit_account_id': cls.account_payable.id,
            'default_credit_account_id': cls.account_receivable.id,
            })

    def test_priority_account_1(self):
        """
        Quy tắc lương, hợp đồng, phòng ban thiết lập đầy đủ tài khoản kế toán, tài khoản quản trị, thẻ quản trị
        Quy tắc lương thiết lập 'Tùy chọn phân tích' là Tài khoản ghi có
        => Ưu tiên lấy tài khoản nợ-có, tài khoản quản trị, thẻ quản trị trên  quy tắc lương
            dòng phát sinh ghi có sẽ có thông tin tài khoản quản trị, thẻ quản trị
        """
        self.rules_generate_account.write({
            'anylytic_option': 'credit_account',
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        # account move lines
        move_lines = payslip.move_id.line_ids
        for line in move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account):
            account_id = line.salary_rule_id.account_debit.id if line.debit > 0 else line.salary_rule_id.account_credit.id

            self.assertRecordValues(
                line,
                [
                    {
                        'account_id': account_id,
                        'analytic_account_id': False if line.debit > 0 else line.salary_rule_id.analytic_account_id.id,
                        'analytic_tag_ids': [] if line.debit > 0 else line.salary_rule_id.analytic_tag_ids.ids,
                        }
                    ]
                )

    def test_priority_account_2(self):
        """
        Quy tắc lương, hợp đồng, phòng ban thiết lập đầy đủ tài khoản kế toán, tài khoản quản trị, thẻ quản trị
        Quy tắc lương thiết lập 'Tùy chọn phân tích' là Tài khoản ghi nợ
        => Ưu tiên lấy tài khoản nợ-có, tài khoản quản trị, thẻ quản trị trên  quy tắc lương
            dòng phát sinh ghi nợ sẽ có thông tin tài khoản quản trị, thẻ quản trị
        """
        self.rules_generate_account.write({
            'anylytic_option': 'debit_account',
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        # account move lines
        move_lines = payslip.move_id.line_ids
        for line in move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account):
            account_id = line.salary_rule_id.account_debit.id if line.debit > 0 else line.salary_rule_id.account_credit.id

            self.assertRecordValues(
                line,
                [
                    {
                        'account_id': account_id,
                        'analytic_account_id': False if line.credit > 0 else line.salary_rule_id.analytic_account_id.id,
                        'analytic_tag_ids': [] if line.credit > 0 else line.salary_rule_id.analytic_tag_ids.ids,
                        }
                    ]
                )

    def test_priority_account_3(self):
        """
        Quy tắc lương, hợp đồng, phòng ban thiết lập đầy đủ tài khoản kế toán, tài khoản quản trị, thẻ quản trị
        Quy tắc lương thiết lập 'Tùy chọn phân tích' để trống
        => Ưu tiên lấy tài khoản nợ-có, tài khoản quản trị, thẻ quản trị trên  quy tắc lương
           tài khoản quản trị, thẻ quản trị không thể hiện trên phát sinh bút toán tương ứng
        """
        self.rules_generate_account.write({
            'anylytic_option': 'none',
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        # account move lines
        move_lines = payslip.move_id.line_ids
        for line in move_lines.filtered(lambda r:r.salary_rule_id in self.rules_generate_account):
            account_id = line.salary_rule_id.account_credit.id if line.credit > 0 else line.salary_rule_id.account_debit.id
            self.assertRecordValues(
                line,
                [
                    {
                        'account_id': account_id,
                        'analytic_account_id': False,
                        'analytic_tag_ids': [],
                        }
                    ]
                )

    def test_priority_account_4(self):
        """
        Quy tắc lương không thiết lập tài khoản kế toán, tài khoản quản trị, thẻ quản trị
        Hợp đồng và phòng ban thiết lập đầy đủ tài khoản kế toán, tài khoản quản trị, thẻ quản trị
        Quy tắc lương thiết lập 'Tùy chọn phân tích' là Tài khoản ghi nợ
        Sổ nhật ký lương có thiết lập tài khoản Nợ Có
        => Ưu tiên lấy tài khoản nợ-có, tài khoản quản trị, thẻ quản trị theo hợp đồng
            dòng phát sinh bên nợ sẽ có thông tin tài khoản quản trị, thẻ quản trị
            Không có dòng phát sinh bên có, tương ứng với quy tắc lương này
            Có dòng phát sinh điều chỉnh - đối ứng với dòng phát sinh bên nợ của quy tắc lương này
                * Tài khoản kế toán của dòng phát sinh điều chỉnh là tài khoản ghi có trên sổ nhật ký Lương
        """
        self.rules_generate_account.write({
            'generate_account_move_line': True,
            'anylytic_option': 'debit_account',
            'account_debit': False,
            'account_credit': False,
            'analytic_tag_ids': False,
            'analytic_account_id': False,
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        # account move lines
        move_lines = payslip.move_id.line_ids

        credit_lines = move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account and r.credit > 0)
        self.assertFalse(credit_lines, 'Test journal item not oke')

        for line in move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account):
            if line.debit > 0:
                self.assertRecordValues(
                    line,
                    [
                        {
                            'account_id': self.contract_open_emp_A.account_expense_id.id,
                            'analytic_account_id': self.contract_open_emp_A.analytic_account_id.id,
                            'analytic_tag_ids': self.contract_open_emp_A.analytic_tag_ids.ids,
                            }
                        ]
                    )

            adjustment_line = move_lines.filtered(lambda r: r.name == 'Adjustment Entry')
            self.assertRecordValues(
                adjustment_line,
                [
                    {
                        'account_id': line.journal_id.default_credit_account_id.id,
                        'analytic_account_id': False,
                        'analytic_tag_ids': [],
                        }
                    ]
                )

    def test_priority_account_5(self):
        """
        Quy tắc lương không thiết lập, hợp đồng và phòng ban thiết lập đầy đủ tài khoản chi phí, tài khoản quản trị, thẻ quản trị
        Quy tắc lương thiết lập 'Tùy chọn phân tích' là Tài khoản ghi có
        Sổ nhật ký lương có thiết lập tài khoản Nợ Có
        => Ưu tiên lấy tài khoản nợ-có, tài khoản quản trị, thẻ quản trị theo hợp đồng
            Có dòng phát sinh bên nợ
            Không có dòng phát sinh bên có, tương ứng với quy tắc lương này
            Có dòng phát sinh điều chỉnh - đối ứng với dòng phát sinh bên nợ của quy tắc lương này
                * Tài khoản kế toán của dòng phát sinh điều chỉnh là tài khoản ghi có trên sổ nhật ký Lương
        """
        self.rules_generate_account.write({
            'generate_account_move_line': True,
            'anylytic_option': 'credit_account',
            'account_debit': False,
            'account_credit': False
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        # account move lines
        move_lines = payslip.move_id.line_ids

        credit_lines = move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account and r.credit > 0)
        self.assertFalse(credit_lines, 'Test journal item not oke')

        for line in move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account):
            if line.debit > 0:
                self.assertRecordValues(
                    line,
                    [
                        {
                            'account_id': self.contract_open_emp_A.account_expense_id.id,
                            'analytic_account_id': False,
                            'analytic_tag_ids': [],
                            }
                        ]
                    )

            adjustment_line = move_lines.filtered(lambda r: r.name == 'Adjustment Entry')
            self.assertRecordValues(
                adjustment_line,
                [
                    {
                        'account_id': line.journal_id.default_credit_account_id.id,
                        'analytic_account_id': False,
                        'analytic_tag_ids': [],
                        }
                    ]
                )

    def test_priority_account_6(self):
        """
        Quy tắc lương không thiết lập, hợp đồng và phòng ban thiết lập đầy đủ tài khoản chi phí, tài khoản quản trị, thẻ quản trị
        Quy tắc lương thiết lập 'Tùy chọn phân tích' để trống
        Sổ nhật ký lương có thiết lập tài khoản Nợ Có
        => Ưu tiên lấy tài khoản nợ-có theo hợp đồng
            Có dòng phát sinh bên nợ
            Không có dòng phát sinh bên có, tương ứng với quy tắc lương này
            Có dòng phát sinh điều chỉnh - đối ứng với dòng phát sinh bên nợ của quy tắc lương này
                * Tài khoản kế toán của dòng phát sinh điều chỉnh là tài khoản ghi có trên sổ nhật ký Lương
        """
        self.rules_generate_account.write({
            'generate_account_move_line': True,
            'anylytic_option': 'none',
            'account_debit': False,
            'account_credit': False
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        # account move lines
        move_lines = payslip.move_id.line_ids

        credit_lines = move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account and r.credit > 0)
        self.assertFalse(credit_lines, 'Test journal item not oke')

        for line in move_lines.filtered(lambda r:r.salary_rule_id in self.rules_generate_account):
            if line.debit > 0:
                self.assertRecordValues(
                    line,
                    [
                        {
                            'account_id': self.contract_open_emp_A.account_expense_id.id,
                            'analytic_account_id': False,
                            'analytic_tag_ids': [],
                            }
                        ]
                    )

            adjustment_line = move_lines.filtered(lambda r: r.name == 'Adjustment Entry')
            self.assertRecordValues(
                adjustment_line,
                [
                    {
                        'account_id': line.journal_id.default_credit_account_id.id,
                        'analytic_account_id': False,
                        'analytic_tag_ids': [],
                        }
                    ]
                )

    def test_priority_account_7(self):
        """
        Quy tắc lương và hợp đồng không thiết lập, phòng ban thiết lập đầy đủ tài khoản chi phí, tài khoản quản trị, thẻ quản trị
        Quy tắc lương thiết lập 'Tùy chọn phân tích' là Tài khoản ghi có
        Sổ nhật ký lương có thiết lập tài khoản Nợ Có
        => Ưu tiên lấy tài khoản nợ-có theo Phòng ban
            Có dòng phát sinh bên nợ
            Không có dòng phát sinh bên có, tương ứng với quy tắc lương này
            Có dòng phát sinh điều chỉnh - đối ứng với dòng phát sinh bên nợ của quy tắc lương này
                * Tài khoản kế toán của dòng phát sinh điều chỉnh là tài khoản ghi có trên sổ nhật ký Lương
        """
        self.rules_generate_account.write({
            'generate_account_move_line': True,
            'anylytic_option': 'credit_account',
            'account_debit': False,
            'account_credit': False
            })

        self.contract_open_emp_A.write({
            'analytic_account_id': False,
            'analytic_tag_ids': False,
            'account_expense_id': False
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        department = self.contract_open_emp_A.department_id
        # account move lines
        move_lines = payslip.move_id.line_ids

        credit_lines = move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account and r.credit > 0)
        self.assertFalse(credit_lines, 'Test journal item not oke')

        for line in move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account):
            if line.debit > 0:
                self.assertRecordValues(
                    line,
                    [
                        {
                            'account_id': department.account_expense_id.id,
                            'analytic_account_id': False,
                            'analytic_tag_ids': [],
                            }
                        ]
                    )

            adjustment_line = move_lines.filtered(lambda r:r.name == 'Adjustment Entry')
            self.assertRecordValues(
                adjustment_line,
                [
                    {
                        'account_id': line.journal_id.default_credit_account_id.id,
                        'analytic_account_id': False,
                        'analytic_tag_ids': [],
                        }
                    ]
                )

    def test_priority_account_8(self):
        """
        Quy tắc lương và hợp đồng không thiết lập, phòng ban thiết lập đầy đủ tài khoản chi phí, tài khoản quản trị, thẻ quản trị
        Quy tắc lương thiết lập 'Tùy chọn phân tích' là Tài khoản ghi nợ
        Sổ nhật ký lương có thiết lập tài khoản Nợ Có
        => Ưu tiên lấy tài khoản nợ-có theo Phòng ban
            Có dòng phát sinh bên nợ
            Không có dòng phát sinh bên có, tương ứng với quy tắc lương này
            Có dòng phát sinh điều chỉnh - đối ứng với dòng phát sinh bên nợ của quy tắc lương này
                * Tài khoản kế toán của dòng phát sinh điều chỉnh là tài khoản ghi có trên sổ nhật ký Lương
        """
        self.rules_generate_account.write({
            'generate_account_move_line': True,
            'anylytic_option': 'debit_account',
            'account_debit': False,
            'account_credit': False,
            'analytic_account_id': False,
            'analytic_tag_ids': False,
            })

        self.contract_open_emp_A.write({
            'analytic_account_id': False,
            'analytic_tag_ids': False,
            'account_expense_id': False
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        department = self.contract_open_emp_A.department_id
        # account move lines
        move_lines = payslip.move_id.line_ids

        credit_lines = move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account and r.credit > 0)
        self.assertFalse(credit_lines, 'Test journal item not oke')

        for line in move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account):
            if line.debit > 0:
                self.assertRecordValues(
                    line,
                    [
                        {
                            'account_id': department.account_expense_id.id,
                            'analytic_account_id': department.analytic_account_id.id,
                            'analytic_tag_ids': department.analytic_tag_ids.ids,
                            }
                        ]
                    )

            adjustment_line = move_lines.filtered(lambda r: r.name == 'Adjustment Entry')
            self.assertRecordValues(
                adjustment_line,
                [
                    {
                        'account_id': line.journal_id.default_credit_account_id.id,
                        'analytic_account_id': False,
                        'analytic_tag_ids': [],
                        }
                    ]
                )

    def test_priority_account_9(self):
        """
        Quy tắc lương và hợp đồng không thiết lập, phòng ban thiết lập đầy đủ tài khoản chi phí, tài khoản quản trị, thẻ quản trị
        Quy tắc lương thiết lập 'Tùy chọn phân tích' để trống
        Sổ nhật ký lương có thiết lập tài khoản Nợ Có
        => Ưu tiên lấy tài khoản nợ-có theo Phòng ban
            Có dòng phát sinh bên nợ
            Không có dòng phát sinh bên có, tương ứng với quy tắc lương này
            Có dòng phát sinh điều chỉnh - đối ứng với dòng phát sinh bên nợ của quy tắc lương này
                * Tài khoản kế toán của dòng phát sinh điều chỉnh là tài khoản ghi có trên sổ nhật ký Lương
        """
        self.rules_generate_account.write({
            'generate_account_move_line': True,
            'anylytic_option': 'none',
            'account_debit': False,
            'account_credit': False
            })

        self.contract_open_emp_A.write({
            'analytic_account_id': False,
            'analytic_tag_ids': False,
            'account_expense_id': False
            })

        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        payslip.action_payslip_verify()

        department = self.contract_open_emp_A.department_id
        # account move lines
        move_lines = payslip.move_id.line_ids

        credit_lines = move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account and r.credit > 0)
        self.assertFalse(credit_lines, 'Test journal item not oke')

        for line in move_lines.filtered(lambda r: r.salary_rule_id in self.rules_generate_account):
            if line.debit > 0:
                self.assertRecordValues(
                    line,
                    [
                        {
                            'account_id': department.account_expense_id.id,
                            'analytic_account_id': False,
                            'analytic_tag_ids': [],
                            }
                        ]
                    )

            adjustment_line = move_lines.filtered(lambda r:r.name == 'Adjustment Entry')
            self.assertRecordValues(
                adjustment_line,
                [
                    {
                        'account_id': line.journal_id.default_credit_account_id.id,
                        'analytic_account_id': False,
                        'analytic_tag_ids': [],
                        }
                    ]
                )

    def test_exception_create_accmount_move_lines_1(self):
        """
        Sổ nhật ký lương không thiết lập tài khoản nợ có
        Quy tắc lương có thiết lập tài khoản ghi nợ,
        Quy tắc lương không thiết lập tài khoản khoản ghi Có
        Hợp đồng và phòng ban có thiết lập tài khoản chi phí

        => Exception
        """
        self.contract_open_emp_A.journal_id.write({
            'default_debit_account_id': False,
            'default_credit_account_id': False,
            })
        self.rules_generate_account.write({
            'generate_account_move_line': True,
            'anylytic_option': 'none',
            'account_credit': False
            })
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        with self.assertRaises(UserError):
            payslip.action_payslip_verify()

    def test_exception_create_accmount_move_lines_2(self):
        """
        Sổ nhật ký lương không thiết lập tài khoản nợ có
        Quy tắc lương không thiết lập tài khoản khoản ghi Có
        Quy tắc lương có thiết lập tài khoản ghi nợ

        => Exception
        """
        self.contract_open_emp_A.journal_id.write({
            'default_debit_account_id': False,
            'default_credit_account_id': False,
            })
        self.rules_generate_account.write({
            'generate_account_move_line': True,
            'anylytic_option': 'none',
            'account_credit': False
            })
        payslip = self.create_payslip(
            self.product_emp_A.id,
            fields.Date.from_string('2021-7-1'),
            fields.Date.from_string('2021-7-30'),
            self.contract_open_emp_A.id
            )
        with self.assertRaises(UserError):
            payslip.action_payslip_verify()
