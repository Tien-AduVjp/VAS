from odoo import _
from odoo.exceptions import UserError

from odoo.tests import Form, tagged

from .test_svl_common import TestSVLCommon


@tagged('post_install', '-at_install', 'external')
class TestSVLSpecificIidentification(TestSVLCommon):
    def setUp(self):
        super(TestSVLSpecificIidentification, self).setUp()

        self.product_serial.product_tmpl_id.categ_id.property_valuation = 'manual_periodic'
        self.product_lot.product_tmpl_id.categ_id.property_valuation = 'manual_periodic'

    def test_product_configuration(self):
        with self.assertRaises(UserError):
            self.env['product.product'].create({
                'name': 'product1',
                'type': 'product',
                'categ_id': self.ref('product.product_category_all'),
            })
    def test_normal_1(self):
        nbre_of_lines = 5
        lot_qty = 20
        sn_qty = 5
        lot_unit_cost = 1000000
        sn_unit_cost = 1500000

        in_moves_lot = self._create_in_move(self.product_lot, lot_unit_cost, lot_qty)
        in_move_serial = self._create_in_move(self.product_serial, sn_unit_cost, sn_qty)

        picking = self._create_picking(in_moves_lot | in_move_serial)
        self._generate_sn(picking.move_lines)
        self._generate_lot(picking.move_lines, nbre_of_lines)
        picking.button_validate()

        # Check
        self.assertEqual(picking.state, 'done', "Wrong state after validating, expected state 'done' instead of '%s'" % picking.state)

        self.assertEqual(self.product_lot.quantity_svl, lot_qty)
        self.assertEqual(sum(self.product_lot.stock_valuation_layer_ids.mapped('remaining_qty')), lot_qty)
        self.assertEqual(sum(self.product_lot.stock_valuation_layer_ids.mapped('remaining_value')), lot_qty * lot_unit_cost)

        self.assertEqual(self.product_serial.quantity_svl, sn_qty)
        self.assertEqual(sum(self.product_serial.stock_valuation_layer_ids.mapped('remaining_qty')), sn_qty)
        self.assertEqual(sum(self.product_serial.stock_valuation_layer_ids.mapped('remaining_value')), sn_qty * sn_unit_cost)

    def test_negative_1(self):
        move1 = self._make_in_move(self.product_lot, 100, 1000000, 5)
        self.assertEqual(self.product_lot.quantity_svl, 100)
        self.assertEqual(self.product_lot.value_svl, 1000000 * 100)

        move2 = self._make_in_move(self.product_lot, 50, 2000000, 2)
        self.assertEqual(self.product_lot.quantity_svl, 100 + 50)
        self.assertEqual(self.product_lot.value_svl, 1000000 * 100 + 2000000 * 50)

        move3 = self._make_out_move(self.product_lot, 160)
        self.assertEqual(move3.stock_valuation_layer_ids[-1].remaining_qty, -10)
        self.assertEqual(self.product_lot.quantity_svl, 100 + 50 - 160)
        self.assertEqual(self.product_lot.value_svl, 1000000 * 100 + 2000000 * 50 - 100 * 1000000 - 60 * 2000000)

        svl_in = (move1 | move2).stock_valuation_layer_ids.filtered(lambda svl: svl.lot_id == move3.stock_valuation_layer_ids.lot_id)
        self.assertEqual(svl_in.remaining_qty, 0)
        self.assertEqual(svl_in.remaining_value, 0)

        move4 = self._make_in_move(self.product_lot, 20, 2000000, 1, force_lot_id=svl_in.lot_id.id)

        self.assertEqual(self.product_lot.quantity_svl, 100 + 50 - 160 + 20)
        self.assertEqual(self.product_lot.value_svl, 1000000 * 100 + 2000000 * 50 - 100 * 1000000 - 60 * 2000000 + 20 * 2000000)
        self.assertEqual(move3.stock_valuation_layer_ids[-1].remaining_qty, 0)
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_qty, 10)
        self.assertEqual(move4.stock_valuation_layer_ids.remaining_value, 10 * 2000000)

    def test_change_in_past_decrease_in_1(self):
        move1 = self._make_in_move(self.product_lot, 20, 1000000, 1)
        move2 = self._make_out_move(self.product_lot, 10)
        move1.move_line_ids.qty_done = 10

        self.assertEqual(self.product_lot.value_svl, 0)
        self.assertEqual(self.product_lot.quantity_svl, 0)

    def test_change_in_past_decrease_in_2(self):
        move1 = self._make_in_move(self.product_lot, 20, 10, 1)
        move2 = self._make_out_move(self.product_lot, 10)
        move3 = self._make_out_move(self.product_lot, 10)
        move1.move_line_ids.qty_done = 10
        move4 = self._make_in_move(self.product_lot, 20, 15, 1)

        self.assertEqual(self.product_lot.value_svl, 150)
        self.assertEqual(self.product_lot.quantity_svl, 10)

    def test_change_in_past_increase_in_1(self):
        move1 = self._make_in_move(self.product_lot, 10, 10, 1)
        move2 = self._make_in_move(self.product_lot, 10, 15, 1)
        move3 = self._make_out_move(self.product_lot, 20)
        move1.move_line_ids.qty_done = 20
 
        self.assertEqual(self.product_lot.value_svl, 100)
        self.assertEqual(self.product_lot.quantity_svl, 10)

    def test_change_in_past_increase_in_2(self):
        move1 = self._make_in_move(self.product_lot, 10, 10, 1)
        move2 = self._make_in_move(self.product_lot, 10, 12, 1)
        move3 = self._make_out_move(self.product_lot, 15)
        move4 = self._make_out_move(self.product_lot, 20)
        move5 = self._make_in_move(self.product_lot, 100, 15, 1)
        move1.move_line_ids.qty_done = 20
  
        self.assertEqual(self.product_lot.value_svl, 1375)
        self.assertEqual(self.product_lot.quantity_svl, 95)

    def test_change_in_past_increase_out_1(self):
        move1 = self._make_in_move(self.product_lot, 20, 10, 1)
        move2 = self._make_out_move(self.product_lot, 10)
        move3 = self._make_in_move(self.product_lot, 20, 15, 1)
        move2.move_line_ids.qty_done = 25

        self.assertEqual(self.product_lot.value_svl, 250)
        self.assertEqual(self.product_lot.quantity_svl, 15)
        self.assertEqual(sum(self.product_lot.stock_valuation_layer_ids.mapped('remaining_qty')), 15)

    def test_change_in_past_decrease_out_1(self):
        move1 = self._make_in_move(self.product_lot, 20, 10, 1)
        move2 = self._make_out_move(self.product_lot, 15)
        move3 = self._make_in_move(self.product_lot, 20, 15, 1)
        move2.move_line_ids.qty_done = 5

        self.assertEqual(self.product_lot.value_svl, 450)
        self.assertEqual(self.product_lot.quantity_svl, 35)
        self.assertEqual(sum(self.product_lot.stock_valuation_layer_ids.mapped('remaining_qty')), 35)

    def test_change_in_past_add_ml_out_1(self):
        move1 = self._make_in_move(self.product_lot, 20, 10, 1)
        move2 = self._make_out_move(self.product_lot, 10)
        move3 = self._make_in_move(self.product_lot, 20, 15, 1)
        self.env['stock.move.line'].create({
            'move_id': move2.id,
            'product_id': move2.product_id.id,
            'lot_id': move2.move_line_ids.lot_id.id,
            'qty_done': 5,
            'product_uom_id': move2.product_uom.id,
            'location_id': move2.location_id.id,
            'location_dest_id': move2.location_dest_id.id,
        })

        self.assertEqual(self.product_lot.value_svl, 350)
        self.assertEqual(self.product_lot.quantity_svl, 25)
        self.assertEqual(sum(self.product_lot.stock_valuation_layer_ids.mapped('remaining_qty')), 25)

    def test_return_delivery_1(self):
        move1 = self._make_in_move(self.product_lot, 10, 10, 1)
        move2 = self._make_out_move(self.product_lot, 10)
        move3 = self._make_in_move(self.product_lot, 10, 20, 1)
        move4 = self._make_out_return(move2, 10)

        self.assertEqual(self.product_lot.value_svl, 300)
        self.assertEqual(self.product_lot.quantity_svl, 20)

    def test_return_receipt_1(self):
        move1 = self._make_in_move(self.product_lot, 10, 10, 1)
        move2 = self._make_in_move(self.product_lot, 10, 20, 1)
        move3 = self._make_in_return(move1, 2)

        self.assertEqual(self.product_lot.value_svl, 280)
        self.assertEqual(self.product_lot.quantity_svl, 18)

    def test_rereturn_receipt_1(self):
        move1 = self._make_in_move(self.product_lot, 1, 10, 1)
        move2 = self._make_in_move(self.product_lot, 1, 20, 1)
        move3 = self._make_out_move(self.product_lot, 1)
        move4 = self._make_in_return(move2, 1)
        move5 = self._make_out_return(move4, 1)
 
        self.assertEqual(self.product_lot.value_svl, 20)
        self.assertEqual(self.product_lot.quantity_svl, 1)

    def test_rereturn_delivery_1(self):
        move1 = self._make_in_move(self.product_lot, 1, 10, 1)
        move2 = self._make_in_move(self.product_lot, 1, 20, 1)
        move3 = self._make_out_move(self.product_lot, 1)
        move4 = self._make_out_return(move3, 1)
        move5 = self._make_in_return(move4, 1)

        self.assertEqual(self.product_lot.value_svl, 20)
        self.assertEqual(self.product_lot.quantity_svl, 1)

    def test_current_accounting_valuation_of_quants_1(self):
        # Test the current accounting valuation of the quants
        # For specific identification valuation, compute the current accounting
        # valuation of the quants by summing the valuation layers's remaining value.
        self._make_in_move(self.product_lot, 10, 10, 1)
        quant = self.product_lot.stock_quant_ids.filtered(
            lambda q: q.location_id.usage == 'internal'
        )
        self.assertEqual(quant.value, 100)
        self._make_out_move(self.product_lot, 1)
        self.assertEqual(quant.value, 90)
        self._make_out_move(self.product_lot, 2)
        self.assertEqual(quant.value, 70)

    def test_dropship_1(self):
        orig_standard_price = self.product_lot.standard_price
        move1 = self._make_in_move(self.product_lot, 1, 10, 1)
        move2 = self._make_in_move(self.product_lot, 1, 20, 1)
        move3 = self._make_dropship_move(self.product_lot, 1, 10, move1.move_line_ids.lot_id.id)

        self.assertEqual(self.product_lot.value_svl, 30)
        self.assertEqual(self.product_lot.quantity_svl, 2)
        self.assertEqual(move3.stock_valuation_layer_ids.lot_id, move1.move_line_ids.lot_id)
        self.assertEqual(orig_standard_price, self.product_lot.standard_price)
