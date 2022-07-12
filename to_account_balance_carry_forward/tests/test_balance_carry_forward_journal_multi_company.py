from odoo.tests import tagged
from odoo.tests.common import TransactionCase

@tagged('post_install', '-at_install')
class TestBalanceCarryForward(TransactionCase):

    def test_01_balance_carry_forward_journal_multi_company(self):
        company = self.env['res.company'].create({'name': 'New Company'})
        self.env.company = company
        self.env.ref('l10n_generic_coa.configurable_chart_template').try_loading()
        self.assertRecordValues(company.balance_carry_forward_journal_id, [
            {'code': 'BCF', 'type': 'general'}
        ])

