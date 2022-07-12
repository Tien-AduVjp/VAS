from odoo.addons.stock_landed_costs.tests.common import TestStockLandedCostsCommon


class TestStockLandedCostsCommonExtension(TestStockLandedCostsCommon):
    
    def setUp(self):
        super(TestStockLandedCostsCommonExtension, self).setUp()

        self.partner = self.env['res.partner'].create({'name': 'Viindoo AS'})
        
        # We already have one account from Odoo's materdata
        # We create a new one and then assign to the product category
        self.default_account_1 = self.env['account.account'].create({
            'name': 'Transportation goods',
            'code': 'X2202',
            'user_type_id': self.env['account.account.type'].create({
                    'name': 'Transportation',
                    'type': 'other',
                    'internal_group': 'equity'}).id,
            'reconcile': True})
        self.category_product = self.env['product.category'].create({
            'name': 'Testing Product',
            'property_cost_method': 'fifo', 
            'property_valuation': 'real_time', 
            'property_stock_account_input_categ_id': self.default_account.id,
            'property_stock_account_output_categ_id': self.default_account_1.id,
            'property_account_expense_categ_id': self.default_account_1.id
        })

        # Create products
        self.product_1 = self.env['product.product'].create({'name': 'Product to use 1', 'type': 'product', 'categ_id': self.category_product.id})
        self.product_2 = self.env['product.product'].create({'name': 'Product to use 2', 'type': 'product', 'categ_id': self.category_product.id})
        self.product_service = self.env['product.product'].create({
            'name': 'Transportation fee', 
            'type': 'service',
            'categ_id': self.category_product.id,
        })
        self.product_with_serial = self.env['product.product'].create({
            'name': 'Product with serial 1',
            'type': 'product',
            'categ_id': self.category_product.id,
            'tracking': 'serial',
        })
