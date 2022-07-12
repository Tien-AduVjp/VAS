from odoo.tests import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestStockLocationAccount(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestStockLocationAccount, cls).setUpClass()

        cls.company_1 = cls.env['res.company'].create({'name': 'Company 1'})
        cls.company_2 = cls.env['res.company'].create({'name': 'Company 2'})

        cls.stock_valuation_account_1 = cls.env['account.account'].create({
            'name': 'Stock Valuation 1',
            'code': 'Stock Valuation 1',
            'user_type_id': cls.env.ref('account.data_account_type_current_assets').id,
            'reconcile': True,
            'company_id': cls.company_1.id
        })

        cls.stock_valuation_account_2 = cls.env['account.account'].create({
            'name': 'Stock Valuation 2',
            'code': 'Stock Valuation 2',
            'user_type_id': cls.env.ref('account.data_account_type_current_assets').id,
            'reconcile': True,
            'company_id': cls.company_1.id
        })

        cls.stock_valuation_account_3 = cls.env['account.account'].create({
            'name': 'Stock Valuation 3',
            'code': 'Stock Valuation 3',
            'user_type_id': cls.env.ref('account.data_account_type_current_assets').id,
            'reconcile': True,
            'company_id': cls.company_2.id
        })

        cls.stock_valuation_account_4 = cls.env['account.account'].create({
            'name': 'Stock Valuation 4',
            'code': 'Stock Valuation 4',
            'user_type_id': cls.env.ref('account.data_account_type_current_assets').id,
            'reconcile': True,
            'company_id': cls.company_2.id
        })

        cls.stock_location = cls.env['stock.location'].create({
            'name': 'Location all companies',
            'usage': 'inventory',
            'company_id': False
        })

    def test_location_account_multi_company(self):
        stock_location_depend_company_1 = self.stock_location.with_context(allowed_company_ids=[self.company_1.id])
        stock_location_depend_company_1.write({
            'property_valuation_in_account_id': self.stock_valuation_account_1.id,
            'property_valuation_out_account_id': self.stock_valuation_account_2.id
        })
        stock_location_depend_company_2 = self.stock_location.with_context(allowed_company_ids=[self.company_2.id])
        stock_location_depend_company_2.write({
            'property_valuation_in_account_id': self.stock_valuation_account_3.id,
            'property_valuation_out_account_id': self.stock_valuation_account_4.id
        })
        # check accounts of stock location on each company are different
        self.assertEqual(stock_location_depend_company_1.property_valuation_in_account_id, self.stock_valuation_account_1)
        self.assertEqual(stock_location_depend_company_1.property_valuation_out_account_id, self.stock_valuation_account_2)

        self.assertEqual(stock_location_depend_company_2.property_valuation_in_account_id, self.stock_valuation_account_3)
        self.assertEqual(stock_location_depend_company_2.property_valuation_out_account_id, self.stock_valuation_account_4)

        self.assertNotEqual(stock_location_depend_company_1.property_valuation_in_account_id, stock_location_depend_company_2.property_valuation_in_account_id)
