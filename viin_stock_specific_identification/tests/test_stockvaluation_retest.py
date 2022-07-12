from datetime import timedelta

from odoo.fields import Datetime
from odoo.exceptions import UserError
from odoo.addons.stock_account.tests.test_stockvaluation import TestStockValuation


class TestStockValuationRetest(TestStockValuation):

    @classmethod
    def setUpClass(cls):
        super(TestStockValuationRetest, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.product3 = cls.env['product.product'].create({
            'name': 'Product C',
            'type': 'product',
            'default_code': 'prdc',
            'tracking': 'serial',
            'categ_id': cls.env.ref('product.product_category_all').id,
        })

    def test_stock_valuation_identification_method(self):
        """ Stock Valuation Identification Method by respecting Lots/Serials"""

        products = self.env['product.product'].search([('categ_id', '=', self.product3.categ_id.id),
                                                       ('tracking', '=', 'none')])
        if products:
            # Test: when changing cost method to specific identification, all product have been enabled tracking
            with self.assertRaises(UserError):
                self.product3.categ_id.property_cost_method = 'specific_identification'

        # enable tracking on all product that belong this category
        # to avoid error when using specific identification method
        products.write({'tracking': 'serial'})
        self.product3.categ_id.property_cost_method = 'specific_identification'

        # self.product3.categ_id.property_valuation = 'real_time'
        now = Datetime.now()
        date1 = now - timedelta(days=8)
        date2 = now - timedelta(days=7)
        date3 = now - timedelta(days=6)
        date4 = now - timedelta(days=5)

        picking_type_in = self.env.ref('stock.picking_type_in')
        receipt = self.env['stock.picking'].create({
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'partner_id': self.partner.id,
            'picking_type_id': picking_type_in.id,
        })
        # in 2 @ 100, serial 0001, 0002
        move1 = self.env['stock.move'].create({
            'name': 'in 2 @ 100',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'product_id': self.product3.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 2.0,
            'price_unit': 100,
            'picking_id': receipt.id,
            'picking_type_id': picking_type_in.id,
        })
        move1._action_confirm()
        move1._action_assign()
        move1.move_line_ids[0].write({'qty_done': 1.0, 'lot_name': '0001'})
        move1.move_line_ids[1].write({'qty_done': 1.0, 'lot_name': '0002'})
        move1._action_done()
        move1.stock_valuation_layer_ids.write({'create_date': date1})

        self.assertEqual(sum(move1.stock_valuation_layer_ids.mapped('value')), 200.0)
        self.assertEqual(sum(move1.stock_valuation_layer_ids.mapped('remaining_qty')), 2.0)

        # in 2 @ 200, serial 0004, 0005
        move2 = self.env['stock.move'].create({
            'name': 'in 2 @ 100',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'product_id': self.product3.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 2.0,
            'price_unit': 200,
            'picking_id': receipt.id,
            'picking_type_id': picking_type_in.id,
        })
        move2._action_confirm()
        move2._action_assign()
        move2.move_line_ids[0].write({'qty_done': 1.0, 'lot_name': '0004'})
        move2.move_line_ids[1].write({'qty_done': 1.0, 'lot_name': '0005'})
        move2._action_done()
        move2.stock_valuation_layer_ids.write({'create_date': date2})

        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('value')), 400.0)
        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('remaining_qty')), 2.0)

        # in 2 @ 300, serial 0006, 0007
        move3 = self.env['stock.move'].create({
            'name': 'in 2 @ 100',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'product_id': self.product3.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 2.0,
            'price_unit': 300,
            'picking_id': receipt.id,
            'picking_type_id': picking_type_in.id,
        })
        move3._action_confirm()
        move3._action_assign()
        move3.move_line_ids[0].write({'qty_done': 1.0, 'lot_name': '0006'})
        move3.move_line_ids[1].write({'qty_done': 1.0, 'lot_name': '0007'})
        move3._action_done()
        move3.stock_valuation_layer_ids.write({'create_date': date3})

        self.assertEqual(sum(move3.stock_valuation_layer_ids.mapped('value')), 600.0)
        self.assertEqual(sum(move3.stock_valuation_layer_ids.mapped('remaining_qty')), 2.0)

        # send 3 with serials of 0001, 0004, 0007
        out_pick = self.env['stock.picking'].create({
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'partner_id': self.env['res.partner'].search([], limit=1).id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
        })
        Lot = self.env['stock.production.lot']
        move4 = self.env['stock.move'].create({
            'name': '3 out',
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'product_id': self.product3.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 3.0,
            'picking_id': out_pick.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'move_line_ids': [
                (0, 0, {
                'product_id': self.product3.id,
                'location_id': self.stock_location.id,
                'location_dest_id': self.customer_location.id,
                'product_uom_id': self.uom_unit.id,
                'qty_done': 1.0,
                'lot_id': Lot.search([('name','=','0001')], limit=1).id
                }),
                (0, 0, {
                'product_id': self.product3.id,
                'location_id': self.stock_location.id,
                'location_dest_id': self.customer_location.id,
                'product_uom_id': self.uom_unit.id,
                'qty_done': 1.0,
                'lot_id': Lot.search([('name','=','0004')], limit=1).id
                }),
                (0, 0, {
                'product_id': self.product3.id,
                'location_id': self.stock_location.id,
                'location_dest_id': self.customer_location.id,
                'product_uom_id': self.uom_unit.id,
                'qty_done': 1.0,
                'lot_id': Lot.search([('name','=','0007')], limit=1).id
                }),]
        })
        move4._action_confirm()
        move4._action_done()
        move4.stock_valuation_layer_ids.write({'create_date': date4})

        # valuation for move4
        # the sum value of the 0001, 0004, 0007 should be -100-200-300 = -600
        self.assertEqual(sum(move4.stock_valuation_layer_ids.mapped('value')), -600.0)
