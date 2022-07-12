from odoo.tests import tagged

from odoo.addons.to_hr_payroll.tests.common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestAccountOnDepartment(TestPayrollCommon):

    @classmethod
    def setUpClass(cls):
        super(TestAccountOnDepartment, cls).setUpClass()

        cls.expense_account = cls.env['account.account'].create({
            'code': 'EXPENSE_ACCOUNT_TEST',
            'name': 'Expenses - (test)',
            'user_type_id': cls.env.ref('account.data_account_type_expenses').id,
            'tag_ids': [(6, 0, cls.env.ref('account.account_tag_operating').ids)],
            })

        cls.vn_chart_template = cls.env.ref('l10n_vn.vn_template')

    def test_01_account_on_department(self):
        """Case 1: Test tài khoản chi phí trên phòng/ban
        Input: Truy cập phòng ban:
            TH1: Phòng/ban đã thiết lập tài khoản chi phí trước khi cài module
            TH2: Phòng/ban chưa thiết lập tài khoản chi phí trước khi cài module
        Output:
            TH1: không thay đổi
            TH2: Tài khoản chi phí phòng ban là 6421 Chi phí nhân viên quản lý
        """
        company = self.env['res.company'].create({
            'name': 'Company Test',
            'currency_id': self.vn_chart_template.currency_id.id,
        })

        self.env.user.company_ids |= company

        department1 = self.env['hr.department'].with_context(tracking_disable=True).create({
            'name': 'department test1',
            'company_id': company.id,
            'account_expense_id': self.expense_account.id,
            })
        department2 = self.env['hr.department'].with_context(tracking_disable=True).create({
            'name': 'department test2',
            'company_id': company.id,
            })

        self.vn_chart_template.try_loading(company=company)

        self.assertRecordValues(
            department1 | department2,
            [
                {
                    'account_expense_id': self.expense_account.id,
                    },
                {
                    'account_expense_id': False,
                    },
                ]
            )
