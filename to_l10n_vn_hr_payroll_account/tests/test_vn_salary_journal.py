from odoo.tests.common import tagged

from .common import TestCommon


@tagged('post_install', '-at_install')
class TestVNSalaryJournal(TestCommon):

    def test_01_default_account_on_salary_journal(self):
        """Case 1: Test Sổ nhật ký lương nhân viên
        Input: Công ty thiết lập COA Việt Nam, Truy cập sổ nhật ký "Lương nhân viên" (mã SAL)
        Output:
            Tài khoản Ghi nợ Mặc định / Tài khoản Ghi có Mặc định là "3341 Phải trả công nhân viên"
        """
        salary_journal = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('code', '=', 'SAL')
            ], limit=1)
        self.assertRecordValues(
            salary_journal,
            [
                {
                    'default_credit_account_id': self.account_3341_id,
                    'default_debit_account_id': self.account_3341_id,
                    },
                ]
            )
