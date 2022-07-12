from odoo.tests.common import SingleTransactionCase

from odoo.addons.stock_account.tests import test_stockvaluation


class TestCommon(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestCommon, cls).setUpClass()

        cls.PickingBackdate = cls.env['stock.picking.backdate']
        # setup Users
        group_backdate = cls.env.ref('to_backdate.group_backdate')
        group_internal = cls.env.ref('base.group_user')
        group_stock_user = cls.env.ref('stock.group_stock_user')
        group_stock_manager = cls.env.ref('stock.group_stock_manager')

        Users = cls.env['res.users'].with_context({
            'no_reset_password': True,
            'tracking_disable': True})
        cls.backdate_user = Users.create({
            'name': 'Backdate User',
            'login': 'backdate_user',
            'email': 'backdate_user@example.viindoo.com',
            'groups_id': [(6, 0, [group_internal.id, group_backdate.id])]
            })
        cls.stock_user = Users.create({
            'name': 'Stock User',
            'login': 'stock_user',
            'email': 'stock_user@example.viindoo.com',
            'groups_id': [(6, 0, [group_stock_user.id])]
            })
        cls.backdate_stock_user = Users.create({
            'name': 'Backdate Stock User',
            'login': 'backdate_stock_user',
            'email': 'backdate_stock_user@example.viindoo.com',
            'groups_id': [(6, 0, [group_stock_user.id, group_backdate.id])]
            })
        cls.manager_user = Users.create({
            'name': 'Inventory Manager User',
            'login': 'manager_backdate',
            'email': 'manager_backdate@example.viindoo.com',
            'groups_id': [(6, 0, [group_stock_manager.id])]
            })

        # setup data for create stock picking/move
        cls.owner = cls.env['res.partner'].create({'name': 'Jean'})
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.picking_type_in = cls.env.ref('stock.picking_type_in')
        cls.picking_type_out = cls.env.ref('stock.picking_type_out')
        cls.productA = cls.env['product.product'].create({'name': 'Product A', 'type': 'product'})
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')

        # set account
        accounts = test_stockvaluation._create_accounting_data(cls.env)
        cls.stock_input_account = accounts[0]
        cls.stock_output_account = accounts[1]
        cls.stock_valuation_account = accounts[2]
        cls.expense_account = accounts[3]
        cls.stock_journal = accounts[4]

        cls.categ = cls.env.ref('product.product_category_all')
        cls.categ.write({
            'property_valuation': 'real_time',
            'property_stock_account_input_categ_id': cls.stock_input_account.id,
            'property_stock_account_output_categ_id': cls.stock_output_account.id,
            'property_stock_valuation_account_id': cls.stock_valuation_account.id,
            'property_stock_journal': cls.stock_journal.id,
        })
        cls.productB = cls.env['product.product'].create({'name': 'Product B',
                                                            'type': 'product',
                                                            'categ_id': cls.categ.id,
                                                            'standard_price': 1000.0})

    def create_picking_move(self, product, location, location_dest, picking_type, date):
        picking = self.env['stock.picking'].create({
            'location_id': location.id,
            'location_dest_id': location_dest.id,
            'partner_id': self.owner.id,
            'picking_type_id': picking_type.id,
            'scheduled_date': date
        })
        # move from shelf1
        move = self.env['stock.move'].create({
            'name': 'test_edit_moveline_1',
            'location_id': location.id,
            'location_dest_id': location_dest.id,
            'picking_id': picking.id,
            'product_id': product.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 100.0,
            'quantity_done': 100.0,
        })
        return picking, move
