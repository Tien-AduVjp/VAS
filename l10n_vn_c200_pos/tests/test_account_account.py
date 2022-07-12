from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestAccountAccount(TransactionCase):

    def test_change_account_131_to_132(self):
        # After install l10n_vn_c200_pos, all pos.payment.method have receivable_account_id is 132 will change to 131
        # Check, If exit pos.payment.method have receivable_account_id is 132, this method will throw error
        # This test is only true at the time of new installation
        vn_template = self.env.ref('l10n_vn.vn_template')
        companies = self.env['res.company'].search([('chart_template_id', '=', vn_template.id)])
        for company in companies:
            pos_payment_method = self.env['pos.payment.method'].search([('company_id', '=', company.id), ('receivable_account_id.code', '=', '132')])
            self.assertEqual(len(pos_payment_method), 0, "l10n_vn_c200_pos: Wrong account in PoS Payment Methods. Note: this test is only true at the time of new installation")
