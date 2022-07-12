import logging
from odoo.tests.common import tagged, Form, SavepointCase

_logger = logging.getLogger(__name__)

@tagged('-at_install', 'post_install')
class TestEmployeeAdvanceVn(SavepointCase):

    @classmethod
    def setUpClass(cls): 
        super(TestEmployeeAdvanceVn, cls).setUpClass()
        cls.chart_template_vn = cls.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if not cls.chart_template_vn:
            _logger.warn("Test skipped because there is no chart of account defined ...")
            cls.skipTest(cls, "No Chart of account found")

        cls.company_a = cls.env['res.company'].create({
            'name': 'Company A',
        })

        cls.chart_template_vn.try_loading(company=cls.company_a)
        cls.env.user.write({
            'company_ids': [(4, cls.company_a.id)],
            'company_id': cls.company_a.id,
        })
        cls.account_141 = cls.env['account.account'].search([
            ('company_id', '=', cls.env.company.id),
            ('code', 'ilike', '141' + '%')], limit=1)

    def test_01_check_account_journal(self):
        # Check default debit, credit account in employee advance journal
        emd_journals = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('is_advance_journal', '=', True),
            ('default_debit_account_id', '!=', False),
            ('default_credit_account_id', '!=', False)])
        default_account = (emd_journals.default_debit_account_id | emd_journals.default_credit_account_id)
        self.assertEqual(len(default_account), 1)
        self.assertEqual(default_account.id, self.account_141.id)

        # Check change is advance journal in journal
        journal = self.env['account.journal'].search([
            ('company_id', '=', self.env.company.id),
            ('type', '=', 'cash'),
            ('is_advance_journal', '=', False)], limit=1)
        journal_form = Form(journal)
        journal_form.is_advance_journal = True
        self.assertEqual(journal_form.default_debit_account_id.id, self.account_141.id)
        self.assertEqual(journal_form.default_credit_account_id.id, self.account_141.id)
