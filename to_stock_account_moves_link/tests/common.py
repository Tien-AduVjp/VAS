from odoo.tests.common import TransactionCase, Form

class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()

        self.picking_type_in = self.env.ref('stock.picking_type_in')
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.picking_type_internal = self.env.ref('stock.picking_type_internal')

        self.stock_location = self.env.ref('stock.stock_location_stock')
        self.customer_location = self.env.ref('stock.stock_location_customers')
        self.supplier_location = self.env.ref('stock.stock_location_suppliers')

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
        self.product_category.write({
            'property_cost_method': 'fifo',
            'property_valuation': 'real_time',
            'property_account_expense_categ_id': account_expense_product.id,
            'property_account_income_categ_id': account_income.id,
            })

        # Create a vendor
        self.vendor = self.env.ref('base.res_partner_1')

        #create product
        self.product_storeable = self.env.ref('product.product_product_25')
        self.product_storeable.categ_id = self.product_category.id

        self.product_consumable = self.env.ref('product.product_product_8')
        self.product_consumable.write({'type': 'consu', 'categ_id': self.product_category.id})

        self.uom_unit = self.env.ref('uom.product_uom_unit')

        # Create data user
        ResUsers = self.env['res.users'].with_context(**{'no_reset_password': True, 'tracking_disable': True})

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

    def _make_in_picking(self, product, quantity=1, unit_cost=None):
        """ Helper to create and validate a receipt picking.
        """
        unit_cost = unit_cost or product.standard_price
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_in.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'move_lines': [(0, 0, {
                'name': 'in %s units @ %s per unit' % (str(quantity), str(unit_cost)),
                'product_id': product.id,
                'location_id': self.supplier_location.id,
                'location_dest_id': self.stock_location.id,
                'product_uom': self.uom_unit.id,
                'product_uom_qty': quantity,
                'price_unit': unit_cost,
                'picking_type_id': self.picking_type_in.id,
                })]
        })

        picking.move_lines._action_confirm()
        picking.move_lines._action_assign()
        picking.move_line_ids.qty_done = quantity
        picking.move_lines._action_done()

        return picking

    def _make_out_picking(self, product, quantity=1):
        """ Helper to create and validate a delivery picking.
        """
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_out.id,
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'move_lines': [(0, 0, {
                'name': 'out %s units' % str(quantity),
                'product_id': product.id,
                'location_id': self.stock_location.id,
                'location_dest_id': self.customer_location.id,
                'product_uom': self.uom_unit.id,
                'product_uom_qty': quantity,
                'picking_type_id': self.picking_type_out.id,
                })]
            })

        picking.move_lines._action_confirm()
        picking.move_lines._action_assign()
        picking.move_line_ids.qty_done = quantity
        picking.move_lines._action_done()

        return picking

    def _make_internal_picking(self, product, quantity=1):
        """ Helper to create and validate a internal picking.
        """
        picking = self.env['stock.picking'].create({
            'picking_type_id': self.picking_type_internal.id,
            'location_id': self.stock_location.id,
            'location_dest_id': self.stock_location.id,
            'move_lines': [(0, 0, {
                'name': 'out %s units' % str(quantity),
                'product_id': product.id,
                'location_id': self.stock_location.id,
                'location_dest_id': self.stock_location.id,
                'product_uom': self.uom_unit.id,
                'product_uom_qty': quantity,
                'picking_type_id': self.picking_type_internal.id,
                })]
            })

        picking.move_lines._action_confirm()
        picking.move_lines._action_assign()
        picking.move_line_ids.qty_done = quantity
        picking.move_lines._action_done()

        return picking
