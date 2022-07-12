from odoo.tests.common import tagged
from .common import TestCommonC133


@tagged('post_install', '-at_install')
class TestVNSalaryRule133(TestCommonC133):

    def test_01_salary_rule_with_GROSS_code(self):
        """Case 1: Test quy tắc lương mã là Gross
        Input: Truy cập quy tắc lương mã là Gross
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi có: 334 Phải trả công nhân viên
            Tùy chọn kế toán quản trị: Tài khoản ghi nợ
        """
        GROSS_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'GROSS'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            GROSS_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_credit': self.account_334_id,
                    'anylytic_option': 'debit_account',
                    },
                ]
            )

        self._test_12_action_reset(GROSS_rule)

    def test_02_salary_rule_with_ESINS_code(self):
        """Case 2: Test quy tắc lương mã là ESINS
        Input: Truy cập quy tắc lương mã là ESINS
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi nợ: 3383 Bảo hiểm xã hội
            Tài khoản ghi có:  334 Phải trả công nhân viên
        """
        ESINS_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'ESINS'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            ESINS_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_debit': self.account_3383_id,
                    'account_credit': self.account_334_id,
                    },
                ]
            )

        self._test_12_action_reset(ESINS_rule)

    def test_03_salary_rule_with_CSINS_code(self):
        """Case 3: Test quy tắc lương mã là CSINS
        Input: Truy cập quy tắc lương mã là CSINS
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi có: 3383 Bảo hiểm xã hội
            Tùy chọn kế toán quản trị: Tài khoản ghi nợ
        """
        CSINS_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'CSINS'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            CSINS_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_credit': self.account_3383_id,
                    'anylytic_option': 'debit_account',
                    },
                ]
            )

        self._test_12_action_reset(CSINS_rule)

    def test_04_salary_rule_with_EHINS_code(self):
        """Case 4: Test quy tắc lương mã là EHINS
        Input: Truy cập quy tắc lương mã là EHINS
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi nợ: 3384 Bảo hiểm y tế
            Tài khoản ghi có: 334 Phải trả công nhân viên
        """
        EHINS_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'EHINS'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            EHINS_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_debit': self.account_3384_id,
                    'account_credit': self.account_334_id,
                    },
                ]
            )

        self._test_12_action_reset(EHINS_rule)

    def test_05_salary_rule_with_CHINS_code(self):
        """Case 5: Test quy tắc lương mã là CHINS
        Input: Truy cập quy tắc lương mã là CHINS
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi có: 3384 Bảo hiểm y tế
            Tùy chọn kế toán quản trị: Tài khoản ghi nợ
        """
        CHINS_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'CHINS'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            CHINS_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_credit': self.account_3384_id,
                    'anylytic_option': 'debit_account',
                    },
                ]
            )

        self._test_12_action_reset(CHINS_rule)

    def test_06_salary_rule_with_EUEINS_code(self):
        """Case 6 Test quy tắc lương mã là EUEINS
        Input: Truy cập quy tắc lương mã là EUEINS
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi nợ: 3386 Bảo hiểm thất nghiệp
            Tài khoản ghi có: 334 Phải trả công nhân viên
        """
        EUEINS_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'EUEINS'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            EUEINS_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_debit': self.account_3385_id,
                    'account_credit': self.account_334_id,
                    },
                ]
            )

        self._test_12_action_reset(EUEINS_rule)

    def test_07_salary_rule_with_GROSS_code(self):
        """Case 7: Test quy tắc lương mã là CUEINS
        Input: Truy cập quy tắc lương mã là CUEINS
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi có: 3385 Bảo hiểm thất nghiệp
            Tùy chọn kế toán quản trị: Tài khoản ghi nợ
        """
        CUEINS_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'CUEINS'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            CUEINS_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_credit': self.account_3385_id,
                    'anylytic_option': 'debit_account',
                    },
                ]
            )

        self._test_12_action_reset(CUEINS_rule)

    def test_08_salary_rule_with_ELUF_code(self):
        """Case 8: Test quy tắc lương mã là ELUF
        Input: Truy cập quy tắc lương mã là ELUF
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi nợ: 3382 Kinh phí công đoàn
            Tài khoản ghi có: 334 Phải trả công nhân viên
        """
        ELUF_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'ELUF'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            ELUF_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_debit': self.account_3382_id,
                    'account_credit': self.account_334_id,
                    },
                ]
            )

        self._test_12_action_reset(ELUF_rule)

    def test_09_salary_rule_with_CLUF_code(self):
        """Case 9: Test quy tắc lương mã là CLUF
        Input: Truy cập quy tắc lương mã là CLUF
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi có: 3382 Kinh phí công đoàn
            Tùy chọn kế toán quản trị: Tài khoản ghi nợ
        """
        CLUF_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'CLUF'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            CLUF_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_credit': self.account_3382_id,
                    'anylytic_option': 'debit_account',
                    },
                ]
            )

        self._test_12_action_reset(CLUF_rule)

    def test_10_salary_rule_with_PTAX_code(self):
        """Case 10: Test quy tắc lương mã là PTAX
        Input: Truy cập quy tắc lương mã là PTAX
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi nợ: 3335 Thuế TNCN
            Tài khoản ghi có: 334 Phải trả công nhân viên
        """
        PTAX_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'PTAX'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            PTAX_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_debit': self.account_3335_id,
                    'account_credit': self.account_334_id,
                    },
                ]
            )

        self._test_12_action_reset(PTAX_rule)

    def test_11_salary_rule_with_HARMFUL_code(self):
        """Case 11: Test quy tắc lương mã là HARMFUL
        Input: Truy cập quy tắc lương mã là HARMFUL
        Output:
            Tạo phát sinh kế toán: True
            Tài khoản ghi có: 334 Phải trả công nhân viên
            Tùy chọn kế toán quản trị: Tài khoản ghi nợ
        """
        HARMFUL_rule = self.env['hr.salary.rule'].search([
            ('code', '=', 'HARMFUL'),
            ('company_id', '=', self.company_c133.id),
            ], limit=1)
        self.assertRecordValues(
            HARMFUL_rule,
            [
                {
                    'generate_account_move_line': True,
                    'account_credit': self.account_334_id,
                    'anylytic_option': 'debit_account',
                    },
                ]
            )

        self._test_12_action_reset(HARMFUL_rule)

    def _test_12_action_reset(self, rule):
        """Case 12: Test nút reset
        Input: Bấm nút "Reset"
        Output: Đặt lại các trường sau về giá trị như khi cài cặt module:
            Tạo phát sinh kế toán
            Tài khoản ghi nợ,
            Tài khoản ghi có
            Tùy chọn kế toán quản trị
        """

        rule.action_reset()

        default_vals = self._get_default_vals_of_rule_to_reset(rule)

        self.assertRecordValues(
            rule,
            [
                {
                    'generate_account_move_line': default_vals.get('generate_account_move_line', False),
                    'account_debit': default_vals.get('account_debit', False),
                    'account_credit': default_vals.get('account_credit', False),
                    'anylytic_option': default_vals.get('anylytic_option', False),
                    },
                ]
            )

    def _get_default_vals_of_rule_to_reset(self, rule):
        struct = rule.struct_id
        default_salary_rules_vals_list = struct.company_id._parepare_salary_rules_vals_list(struct)
        match = {}
        for vals_dict in default_salary_rules_vals_list:
            if vals_dict.get('code') == rule.code\
                and vals_dict.get('category_id') == rule.category_id.id\
                and vals_dict.get('company_id') == rule.company_id.id:
                match = vals_dict
                break

        default_vals = rule._get_fields_to_reset()
        default_vals.update(match)
        return default_vals
