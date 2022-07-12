from odoo.tests.common import TransactionCase, Form

class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()

        self.picking_type_receipts = self.env.ref('stock.picking_type_in')
        self.picking_type_internal_transfers = self.env.ref('stock.picking_type_internal')       
        user_type_expense = self.env.ref('account.data_account_type_expenses')
        account_expense_product = self.env['account.account'].create({
            'code': 'EXPENSE_PROD111',
            'name': 'Expense - Test Account',
            'user_type_id': user_type_expense.id,
        })
        account_type_inc = self.env.ref('account.data_account_type_revenue')
        account_income = self.env['account.account'].create({'name': 'Income', 'code': 'INC00' , 'user_type_id': account_type_inc.id, 'reconcile': True})
        
        # Create product category
        self.product_category = self.env.ref('product.product_category_all')
        self.product_category.property_cost_method = 'fifo'
        self.product_category.property_valuation = 'real_time'
        self.product_category.property_account_expense_categ_id = account_expense_product.id,
        self.product_category.property_account_income_categ_id = account_income.id
        
        # Create a vendor
        self.vendor = self.env.ref('base.res_partner_1')

        #create product
        self.product_storeable = self.env.ref('product.product_product_25')
        self.product_storeable.categ_id = self.product_category.id

        self.product_consumable = self.env.ref('product.product_product_8')
        self.product_consumable.type = 'consu'
        self.product_consumable.categ_id = self.product_category.id    

        # Create data user
        ResUsers = self.env['res.users'].with_context({'no_reset_password': True, 'tracking_disable': True})
        
        #User inventory
        self.user_inventory = ResUsers.create({
            'name': 'User Inventory',
            'login': 'user_inventory',
            'email': 'user.inventory@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('stock.group_stock_user').id])]            
        })
        
        #User inventory with accountant(Billing)
        self.user_inventory_billing = ResUsers.create({
            'name': 'User Inventory Billing',
            'login': 'user_inventory_billing',
            'email': 'user.inventory.billing@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('stock.group_stock_user').id, self.env.ref('account.group_account_invoice').id])],        
        })
        
        #User inventory with accountant(Admin)
        self.user_inventory_accountant_admin = ResUsers.create({
            'name': 'User Inventory Account Admin',
            'login': 'user_inventory_accountant_admin',
            'email': 'user.inventory.accountant.admin@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('stock.group_stock_user').id, self.env.ref('account.group_account_user').id])],        
        })
        
        #User accountant(Billing)
        self.user_accountant_billing = ResUsers.create({
            'name': 'User Accountant billing',
            'login': 'user_accountant_billing',
            'email': 'user.accountant.billing@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('account.group_account_invoice').id])],        
        })

        #User accountant(Admin)
        self.user_accountant = ResUsers.create({
            'name': 'User Accountant',
            'login': 'user_accountant',
            'email': 'user.accountant@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('account.group_account_user').id])],        
        })

    def create_inventory_transfer(self, product, picking_type):
        stock_picking_form = Form(self.env['stock.picking'])         
        stock_picking_form.picking_type_id = picking_type       
        with stock_picking_form.move_ids_without_package.new() as move:
            move.product_id = product
            move.product_uom_qty = 1

        stock_picking = stock_picking_form.save()
        stock_picking.action_confirm()
        
        stock_transfer_form = self.env['stock.immediate.transfer'].create({
            'pick_ids': stock_picking
        })
        stock_transfer_form.process()
        return stock_picking
