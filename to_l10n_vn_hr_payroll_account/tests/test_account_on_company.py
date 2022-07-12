from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestAccountOnCompany133(TransactionCase):

    def test_account_on_company_1(self):
        """
        Khi thiết lập CoA VN (TT133) cho công ty

        => Tài khoản phải trả nhân viên là 334
        """
        chart_template_133 = self.env.ref('l10n_vn_c133.vn_template_c133')
        company = self.env['res.company'].create({
            'name': 'New company',
            'currency_id': chart_template_133.currency_id.id
        })
        chart_template_133.try_loading(company=company)
        self.assertEqual(company.general_employee_payable_account_id.code, '334')

    def test_account_on_company_2(self):
        """
        Khi thiết lập CoA VN cho công ty (TT200)

        => Tài khoản phải trả nhân viên là 334
        """
        chart_template_200 = self.env.ref('l10n_vn.vn_template')
        company = self.env['res.company'].create({
            'name': 'New company',
            'currency_id': chart_template_200.currency_id.id
        })
        chart_template_200.try_loading(company=company)
        self.assertEqual(company.general_employee_payable_account_id.code, '334')
