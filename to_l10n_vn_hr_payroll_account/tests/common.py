from odoo.tests import SavepointCase


class TestCommonC200(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommonC200, cls).setUpClass()


        chart_template_200 = cls.env.ref('l10n_vn.vn_template')
        cls.company_c200 = cls.env['res.company'].create({
            'name': 'Company C200',
            'currency_id': chart_template_200.currency_id.id
            })
        chart_template_200.try_loading(company=cls.company_c200)

        Account = cls.env['account.account']
        cls.account_3335_id = Account.search([
            ('code', '=', '3335'),
            ('company_id', '=', cls.company_c200.id)
            ], limit=1).id

        cls.account_334_id = Account.search([
            ('code', '=', '334'),
            ('company_id', '=', cls.company_c200.id)
            ], limit=1).id

        cls.account_3382_id = Account.search([
            ('code', '=', '3382'),
            ('company_id', '=', cls.company_c200.id)
            ], limit=1).id

        cls.account_3383_id = Account.search([
            ('code', '=', '3383'),
            ('company_id', '=', cls.company_c200.id)
            ], limit=1).id

        cls.account_3384_id = Account.search([
            ('code', '=', '3384'),
            ('company_id', '=', cls.company_c200.id)
            ], limit=1).id

        cls.account_3386_id = Account.search([
            ('code', '=', '3386'),
            ('company_id', '=', cls.company_c200.id)
            ], limit=1).id


class TestCommonC133(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommonC133, cls).setUpClass()

        chart_template_133 = cls.env.ref('l10n_vn_c133.vn_template_c133')
        cls.company_c133 = cls.env['res.company'].create({
            'name': 'Company C133',
            'currency_id': chart_template_133.currency_id.id
            })
        chart_template_133.try_loading(company=cls.company_c133)

        Account = cls.env['account.account']
        cls.account_3335_id = Account.search([
            ('code', '=', '3335'),
            ('company_id', '=', cls.company_c133.id)
            ], limit=1).id

        cls.account_334_id = Account.search([
            ('code', '=', '334'),
            ('company_id', '=', cls.company_c133.id)
            ], limit=1).id

        cls.account_3382_id = Account.search([
            ('code', '=', '3382'),
            ('company_id', '=', cls.company_c133.id)
            ], limit=1).id

        cls.account_3383_id = Account.search([
            ('code', '=', '3383'),
            ('company_id', '=', cls.company_c133.id)
            ], limit=1).id

        cls.account_3384_id = Account.search([
            ('code', '=', '3384'),
            ('company_id', '=', cls.company_c133.id)
            ], limit=1).id

        cls.account_3385_id = Account.search([
            ('code', '=', '3385'),
            ('company_id', '=', cls.company_c133.id)
            ], limit=1).id
