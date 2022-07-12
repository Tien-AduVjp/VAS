from datetime import date

from odoo.tests.common import Form, tagged

from .stock_asset_common import TestStockAssetCommon


@tagged('post_install', '-at_install')
class TestStockAssetFlow(TestStockAssetCommon):

    def test_01_out_picking_with_stockrable_serial_product(self):
        asset = self.env['account.asset.asset']
        with self.mocked_today('2020-08-08'):
            # receive 2 units @ 100.000.000 per unit
            picking1 = self._make_in_picking_with_serial_product(self.product1,
                                                                 2,
                                                                 100000000,
                                                                 serials=['ASSET_001', 'ASSET_002']
                                                                 )
            # out 1 units @ 100.000.000 per unit with serial as ASSET_001
            picking2 = self._make_out_picking_as_asset(self.product1, 1)
            self._force_serial_on_move_line(picking2.move_line_ids, 'ASSET_001')
            self._validate_picking(picking2)

            # Check stock journal entries
            self.assertEqual(100000000, picking2.account_move_ids.amount_total)

            asset = self._search_asset_is_in_draft(picking2.move_line_ids.lot_id)
            # Check
            self.assertEqual(asset.value, 100000000)
            self.assertEqual(asset.state, 'draft')
            self.assertEqual(asset.production_lot_id.name, 'ASSET_001')
            self.assertEqual(asset.stock_move_line_ids.location_id.usage, 'internal')
            self.assertEqual(asset.stock_move_line_ids.location_dest_id.usage, 'asset_allocation')

            # Create landed cost for in picking @ 10.000.000
            self._create_landed_cost(picking1, 10000000)
            self.assertEqual(asset.value, 105000000)

        with self.mocked_today('2020-10-28'):
            asset.validate()
            depreciation_lines = asset.depreciation_line_ids.filtered(lambda l: l.depreciation_date <= date(2020, 10, 28))
            for move in depreciation_lines.move_id:
                self.assertEqual(move.state, 'posted')
            # Stock in at 28/10/2020
            in_wizard = self._create_stock_in_wizard(asset, date(2020, 10, 28))
            in_wizard.create_asset_stock_in()
            asset.move_ids.filtered(lambda move: move.state == 'draft')._post()
            # Check
            in_move = asset.stock_move_line_ids[-1].move_id
            self.assertEqual(in_move.state, 'done')
            self.assertEqual(in_move.location_dest_id.usage, 'internal')
            self.assertEqual(in_move.location_id.usage, 'asset_allocation')
            self.assertEqual(81854838.71000001, in_move.price_unit)

        # out 1 units @ 81.854.838,71000001 at 12/01/2021 with serial as ASSET_001
        with self.mocked_today('2021-01-12'):
            picking3 = self._make_out_picking_as_asset(self.product1, 1)
            self._force_serial_on_move_line(picking3.move_line_ids, 'ASSET_001')
            self._validate_picking(picking3)

            # Check stock journal entries
            self.assertEqual(81854838.71000001, picking3.account_move_ids.amount_total)

            asset = self._search_asset_is_in_draft(picking3.move_line_ids.lot_id)
            # Check
            self.assertEqual(asset.value, 81854838.71000001)
            self.assertEqual(asset.production_lot_id.name, 'ASSET_001')

            # out 1 units @ 105.000.000 at 12/01/2021 with serial as ASSET_002
            picking4 = self._make_out_picking_as_asset(self.product1, 1)
            self._force_serial_on_move_line(picking4.move_line_ids, 'ASSET_002')
            self._validate_picking(picking4)

            # Check stock journal entries
            self.assertEqual(105000000, picking4.account_move_ids.amount_total)

            asset = self._search_asset_is_in_draft(picking4.move_line_ids.lot_id)
            # Check
            self.assertEqual(asset.value, 105000000)
            self.assertEqual(asset.production_lot_id.name, 'ASSET_002')

    def test_02_out_picking_with_stockrable_serial_product_multi(self):
        asset = self.env['account.asset.asset']
        with self.mocked_today('2020-08-08'):
            # receive 2 units @ 100.000.000 per unit
            picking1 = self._make_in_picking_with_serial_product(self.product1,
                                                                 2,
                                                                 100000000,
                                                                 serials=['ASSET_001', 'ASSET_002']
                                                                 )
            # out 2 units @ 100.000.000 per unit with serial as ASSET_001 and ASSET_002
            picking2 = self._make_out_picking_as_asset(self.product1, 2)
            self._force_serial_on_move_line(picking2.move_line_ids[0], 'ASSET_001')
            self._force_serial_on_move_line(picking2.move_line_ids[1], 'ASSET_002')
            self._validate_picking(picking2)

            # Check stock journal entries
            self.assertEqual(len(picking2.account_move_ids), 1)
            self.assertEqual(200000000, picking2.account_move_ids.amount_total)

    def test_03_out_picking_with_stockrable_serial_product_multi(self):
        with self.mocked_today('2020-08-08'):
            # receive 2 units @ 100.000.000 per unit
            # receive 2 units @ 200.000.000 per unit
            self._make_in_picking_with_serial_product(self.product1,
                                                                 2,
                                                                 100000000,
                                                                 serials=['ASSET_001', 'ASSET_002']
                                                                 )
            self._make_in_picking_with_serial_product(self.product1,
                                                                 2,
                                                                 200000000,
                                                                 serials=['ASSET_003', 'ASSET_004']
                                                                 )
            # out 4 units
            picking3 = self._make_out_picking_as_asset(self.product1, 4)
            self._force_serial_on_move_line(picking3.move_line_ids[0], 'ASSET_001')
            self._force_serial_on_move_line(picking3.move_line_ids[1], 'ASSET_002')
            self._force_serial_on_move_line(picking3.move_line_ids[2], 'ASSET_003')
            self._force_serial_on_move_line(picking3.move_line_ids[3], 'ASSET_004')
            self._validate_picking(picking3)

            # Check stock journal entries
            self.assertEqual(len(picking3.account_move_ids), 1)
            self.assertEqual(600000000, picking3.account_move_ids.amount_total)

    def _create_stock_in_wizard(self, asset, date):
        Wizard = self.env['asset.stock.in.wizard'].with_context(active_id=asset.id, active_ids=asset.ids)
        wizard_form = Form(Wizard)
        wizard_form.date = date
        return wizard_form.save()

    def _create_landed_cost(self, pickings, price_unit, split_method='equal'):
        Cost = self.env['stock.landed.cost']

        default_vals = Cost.default_get(list(Cost.fields_get()))
        default_vals.update({
            'picking_ids': pickings.ids,
            'account_journal_id': self.expenses_journal.id,
            'cost_lines': [(0, 0, {'product_id': self.ref('product.product_product_1')})],
            'valuation_adjustment_lines': [],
        })
        landed_cost = self.env['stock.landed.cost'].new(default_vals)
        landed_cost.cost_lines.onchange_product_id()
        landed_cost.cost_lines.name = '%s split' % split_method
        landed_cost.cost_lines.split_method = split_method
        landed_cost.cost_lines.price_unit = price_unit
        vals = landed_cost._convert_to_write(landed_cost._cache)
        landed_cost = Cost.create(vals)

        # Compute the landed cost using Compute button
        landed_cost.compute_landed_cost()
        # Confirm the landed cost
        landed_cost.button_validate()
        return landed_cost
