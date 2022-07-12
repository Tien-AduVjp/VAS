from odoo.addons.account.tests.test_account_move_in_invoice import AccountTestInvoicingCommon
from odoo.tests.common import tagged


@tagged('post_install', '-at_install')
class TestFunctionPostInitHook(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref='l10n_vn.vn_template')
        cls.todo_list = [  # Property Promotion Voucher Accounts
            'property_promotion_voucher_profit_account_id',
            'property_promotion_voucher_loss_account_id',
        ]

    def test_function_post_init_hook(self):
        self.env.company._update_promotion_voucher_properties_vietnam()
        for todo in self.todo_list:
            account = getattr(self.env.company, todo)
            value = account and 'account.account,' + str(account.id) or False
            property = self.env['ir.property'].search([
                ('name', '=', todo),
                ('company_id', '=', self.env.company.id),
                ('res_id', '=', False)
            ])
            self.assertEqual(property.value_reference, value, "to_promotion_voucher_l10n_vn: Value not as expected")
