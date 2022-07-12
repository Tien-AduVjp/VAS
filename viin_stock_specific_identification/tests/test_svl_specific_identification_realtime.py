from .test_svl_common import TestSVLCommon


class TestSVLRealtime(TestSVLCommon):

    @classmethod
    def setUpClass(cls):
        super(TestSVLRealtime, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'xxx'})
        cls.owner1 = cls.env['res.partner'].create({'name': 'owner1'})
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.inventory_user = cls.env['res.users'].create({
            'name': 'Pauline Poivraisselle',
            'login': 'pauline',
            'email': 'p.p@example.viindoo.com',
            'notification_type': 'inbox',
            'groups_id': [(6, 0, [cls.env.ref('stock.group_stock_user').id])]
        })

    def _get_stock_input_move_lines(self):
        return self.env['account.move.line'].search([
            ('account_id', '=', self.stock_input_account.id),
        ], order='date, id')

    def _get_stock_output_move_lines(self):
        return self.env['account.move.line'].search([
            ('account_id', '=', self.stock_output_account.id),
        ], order='date, id')

    def _get_stock_valuation_move_lines(self):
        return self.env['account.move.line'].search([
            ('account_id', '=', self.stock_valuation_account.id),
        ], order='date, id')

    def test_realtime(self):
        """ Stock moves update stock value with product x cost price,
        price change updates the stock value based on current stock level.
        """
        move1 = self._make_in_move(self.product_lot, 10, 100, 2)
        # account values for move1
        input_amls = self._get_stock_input_move_lines()
        self.assertEqual(len(input_amls), 1)
        self.assertEqual(input_amls.credit, 1000)
        self.assertEqual(input_amls.debit, 0)
        self.assertEqual(input_amls.quantity, 10)
        self.assertEqual(input_amls.stock_move_id, move1)
        self.assertEqual(input_amls.product_id, self.product_lot)
        self.assertEqual(input_amls.product_uom_id, self.uom_unit)

        valuation_amls = self._get_stock_valuation_move_lines()
        self.assertEqual(len(valuation_amls), 1)
        self.assertEqual(valuation_amls.debit, 1000)
        self.assertEqual(valuation_amls.credit, 0)
        self.assertEqual(valuation_amls.quantity, 10)
        self.assertEqual(valuation_amls.stock_move_id, move1)
        self.assertEqual(valuation_amls.product_id, self.product_lot)
        self.assertEqual(valuation_amls.product_uom_id, self.uom_unit)

        output_aml = self._get_stock_output_move_lines()
        self.assertEqual(len(output_aml), 0)

        # stock_account values for move1
        svls = move1.stock_valuation_layer_ids
        self.assertEqual(len(svls), 2)
        self.assertEqual(sum(svls.mapped('remaining_qty')), 10)
        self.assertEqual(sum(svls.mapped('remaining_value')), 1000)
        self.assertEqual(sum(svls.mapped('quantity')), 10)
        self.assertEqual(sum(svls.mapped('value')), 1000)
        self.assertEqual(svls.lot_id, move1.move_line_ids.lot_id)
        for svl in svls:
            self.assertEqual(svl.remaining_qty, 5)
            self.assertEqual(svl.remaining_value, 500)
            self.assertEqual(svl.unit_cost, 100)
            self.assertEqual(svl.quantity, 5)
            self.assertEqual(svl.value, 500)

    def test_specific_identification_perpetual_1(self):
        # receive 10 units @ 10 per unit
        move1 = self._make_in_move(self.product_lot, 10, 10, 1)
        # receive 10 units @ 8 per unit
        move2 = self._make_in_move(self.product_lot, 10, 8, 1)
        # sale 3 units
        move3 = self._create_out_move(self.product_lot, 3)
        picking = self._create_picking(move3)
        picking.action_assign()
        move3.move_line_ids.write({'qty_done': 3.0, 'lot_id': move2.move_line_ids.lot_id.id})
        picking.button_validate()
        # stock_account values for move3
        self.assertEqual(move3.stock_valuation_layer_ids.remaining_qty, 0.0)  # unused in out move
        self.assertEqual(move3.stock_valuation_layer_ids.value, -24.0)  # took 3 items from move 2 @ 8 per unit
        self.assertEqual(move3.stock_valuation_layer_ids.lot_id, move2.move_line_ids.lot_id)
        # account values for move3
        input_aml = self._get_stock_input_move_lines()
        self.assertEqual(len(input_aml), 2)

        valuation_aml = self._get_stock_valuation_move_lines()
        move3_valuation_aml = valuation_aml[-1]
        self.assertEqual(len(valuation_aml), 3)
        self.assertEqual(move3_valuation_aml.debit, 0)
        self.assertEqual(move3_valuation_aml.credit, 24)
        self.assertEqual(move3_valuation_aml.product_id.id, self.product_lot.id)
        self.assertEqual(move3_valuation_aml.quantity, -3)
        self.assertEqual(move3_valuation_aml.product_uom_id.id, self.uom_unit.id)

        output_aml = self._get_stock_output_move_lines()
        move3_output_aml = output_aml[-1]
        self.assertEqual(len(output_aml), 1)
        self.assertEqual(move3_output_aml.debit, 24)
        self.assertEqual(move3_output_aml.credit, 0)

        # ---------------------------------------------------------------------
        # Increase received quantity of move1 from 10 to 12, it should create
        # a new stock layer at the top of the queue.
        # ---------------------------------------------------------------------
        move2.quantity_done = 12

        # stock_account values for move2
        self.assertEqual(move2.stock_valuation_layer_ids.sorted()[-1].unit_cost, 8)
        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('remaining_qty')), 9.0)
        self.assertEqual(sum(move2.stock_valuation_layer_ids.mapped('value')), 96)  # move 2 is now 10@8 + 2@8

        # account values for move1
        input_aml = self._get_stock_input_move_lines()
        self.assertEqual(len(input_aml), 3)
        move2_correction_input_aml = input_aml[-1]
        self.assertEqual(move2_correction_input_aml.debit, 0)
        self.assertEqual(move2_correction_input_aml.credit, 16)

        valuation_aml = self._get_stock_valuation_move_lines()
        move2_correction_valuation_aml = valuation_aml[-1]
        self.assertEqual(len(valuation_aml), 4)
        self.assertEqual(move2_correction_valuation_aml.debit, 16)
        self.assertEqual(move2_correction_valuation_aml.credit, 0)
        self.assertEqual(move2_correction_valuation_aml.product_id.id, self.product_lot.id)
        self.assertEqual(move2_correction_valuation_aml.quantity, 2)
        self.assertEqual(move2_correction_valuation_aml.product_uom_id.id, self.uom_unit.id)

        output_aml = self._get_stock_output_move_lines()
        self.assertEqual(len(output_aml), 1)
        # Sale 20 units, we fall in negative stock for 10 units. Theses are
        # valued at the move2 cost and the total is negative.
        move4 = self._make_out_move(self.product_lot, 20)
        # stock_account values for move5
        # (took 10 from the first receipt, 7 from the second receipt, 2 from the increase of the second receipt)
        self.assertEqual(sum(move4.stock_valuation_layer_ids.mapped('remaining_qty')), -1)
        self.assertEqual(sum(move4.stock_valuation_layer_ids.mapped('quantity')), -20)
        self.assertEqual(sum(move4.stock_valuation_layer_ids.mapped('value')), -180.0)
