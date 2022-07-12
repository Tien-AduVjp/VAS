from odoo.tests.common import TransactionCase, tagged
from odoo.addons.stock_account.tests.test_stockvaluation import _create_accounting_data


@tagged('post_install', '-at_install')
class TestFleetStockAccount(TransactionCase):

    def setUp(self):
        super(TestFleetStockAccount, self).setUp()
        product = self.env.ref('product.product_product_25')
        stock_input_account, stock_output_account, stock_valuation_account, expense_account, stock_journal = _create_accounting_data(
            self.env)
        product.categ_id.write({
            'property_valuation': 'real_time',
            'property_cost_method': 'fifo',
            'property_stock_account_input_categ_id': stock_input_account.id,
            'property_stock_account_output_categ_id': stock_output_account.id,
            'property_stock_valuation_account_id': stock_valuation_account.id,
            'property_stock_journal': stock_journal.id,
        })
        self.vehicle = self.env.ref('fleet.vehicle_1')

        self.stock_picking = self.env['stock.picking'].create({
            'name': 'test_stock',
            'picking_type_id': self.env.ref('to_fleet_stock.picking_type_fleet_consumption').id,
            'fleet_service_type_id': self.env.ref('fleet.type_service_service_1').id,
            'move_ids_without_package': [(0, 0, {
                'name': 'test_stock',
                'product_id': product.id,
                'quantity_done': 3,
                'product_uom_qty': 3,
                'vehicle_id': self.vehicle.id,
                'product_uom': product.uom_id.id,
            })],
            'location_id': self.env.ref('stock.stock_location_customers').id,
            'location_dest_id': self.env.ref('stock.stock_location_stock').id
        })

    def test_fleet_stock_account(self):
        self.stock_picking.action_confirm()
        self.stock_picking.action_assign()
        self.stock_picking._action_done()
        self.assertIn(self.vehicle.id, self.stock_picking.account_move_ids.line_ids.filtered(
            lambda l: l.debit > 0).vehicle_ids.ids)
