from odoo.tests import tagged
from odoo.tests import TransactionCase


@tagged('post_install', '-at_install')
class TestAccountOnDepartment200(TransactionCase):

    def setUp(self):
        super(TestAccountOnDepartment200, self).setUp()

        self.expense_account = self.env['account.account'].create({
            'code': 'EXPENSE_ACCOUNT_TEST',
            'name': 'Expenses - (test)',
            'user_type_id': self.env.ref('account.data_account_type_expenses').id,
            'tag_ids': [(6, 0, self.env.ref('account.account_tag_operating').ids)],
            })

        self.vn_chart_template = self.env.ref('l10n_vn.vn_template')

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

        Department = self.env['hr.department'].with_context(tracking_disable=True)
        department1 = Department.create({
            'name': 'department test1',
            'company_id': company.id,
            'account_expense_id': self.expense_account.id,
            })
        department2 = Department.create({
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

        # TH2:
        company._l10n_vn_update_departments_expense_account()
        account_642 = self.env['account.account'].search([
            ('code', '=', '642'),
            ('company_id', '=', company.id)
            ], limit=1)
        self.assertRecordValues(
            department1 | department2,
            [
                {
                    'account_expense_id': self.expense_account.id,
                    },
                {
                    'account_expense_id': account_642.id,
                    },
                ]
            )
