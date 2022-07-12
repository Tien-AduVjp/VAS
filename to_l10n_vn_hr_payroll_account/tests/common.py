from odoo.addons.account.tests.test_account_move_in_invoice import AccountTestInvoicingCommon


class TestCommon(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref='l10n_vn.vn_template')

        cls.account_3335_id = cls.env['account.account'].search([
            ('code', '=', '3335'),
            ('company_id', '=', cls.env.company.id)
            ], limit=1).id

        cls.account_3341_id = cls.env['account.account'].search([
            ('code', '=', '3341'),
            ('company_id', '=', cls.env.company.id)
            ], limit=1).id

        cls.account_3382_id = cls.env['account.account'].search([
            ('code', '=', '3382'),
            ('company_id', '=', cls.env.company.id)
            ], limit=1).id

        cls.account_3383_id = cls.env['account.account'].search([
            ('code', '=', '3383'),
            ('company_id', '=', cls.env.company.id)
            ], limit=1).id

        cls.account_3384_id = cls.env['account.account'].search([
            ('code', '=', '3384'),
            ('company_id', '=', cls.env.company.id)
            ], limit=1).id

        cls.account_3386_id = cls.env['account.account'].search([
            ('code', '=', '3386'),
            ('company_id', '=', cls.env.company.id)
            ], limit=1).id
