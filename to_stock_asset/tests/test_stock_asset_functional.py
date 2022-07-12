from odoo.exceptions import MissingError, UserError
from odoo.tests.common import tagged

from .stock_asset_common import TestStockAssetCommon


@tagged('post_install', '-at_install')
class TestStockAssetFunctional(TestStockAssetCommon):

    def test_01_out_picking_with_storable_product_no_tracking(self):
        self.product1.tracking = 'none'

        self._make_in_move(self.product1, 1)

        self.assertEqual(self.product1.type, 'product')
        self.assertEqual(self.product1.tracking, 'none')
        picking = self._make_out_picking_as_asset(self.product1, 1)
        self.assertRaises(UserError, picking.button_validate)

    def test_02_out_picking_with_consumable_product(self):
        self._make_in_move(self.product_comsu, 1)
        self.assertEqual(self.product_comsu.type, 'consu')
        picking = self._make_out_picking_as_asset(self.product_comsu, 1)
        self.assertRaises(UserError, picking.button_validate)

    def test_03_out_picking_with_storable_product_tracking(self):
        # The product must be configured in automated valuation method
        self.product1.categ_id.property_valuation = 'manual_periodic'

        self.assertEqual(self.product1.type, 'product')
        self.assertEqual(self.product1.tracking, 'serial')
        self.assertEqual(self.product1.valuation, 'manual_periodic')
        picking = self._make_out_picking_as_asset(self.product1, 1)
        self.assertRaises(UserError, picking.button_validate)

    def test_04_return_picking_with_asset_that_is_in_draft(self):
        picking1 = self._make_in_picking_with_serial_product(self.product1, 2, 10000000)

        picking2 = self._make_out_picking_as_asset(self.product1, 1)
        self._validate_picking(picking2)

        asset = self._search_asset_is_in_draft(picking2.move_line_ids.lot_id)

        self.assertEqual(asset.value, 10000000)
        # Remove asset that has been linked to stock move
        self.assertRaises(UserError, asset.unlink)
        # return a part of what we've done
        return_picking = self._make_return_picking(picking2)
        return_picking.action_done()
        self.assertEqual(return_picking.state, 'done')
        with self.assertRaises(MissingError):
            asset.value

    def test_05_return_picking_with_asset_that_is_not_in_draft(self):
        picking1 = self._make_in_picking_with_serial_product(self.product1, 2, 10000000)

        picking2 = self._make_out_picking_as_asset(self.product1, 1)
        self._validate_picking(picking2)

        asset = self._search_asset_is_in_draft(picking2.move_line_ids.lot_id)

        self.assertEqual(asset.value, 10000000)
        asset.validate()
        # Remove asset that has been linked to stock move
        self.assertRaises(UserError, asset.unlink)
        # return a part of what we've done
        with self.assertRaises(UserError):
            self._make_return_picking(picking2)

    def test_06_two_asset_with_same_serial(self):
        picking1 = self._make_in_picking_with_serial_product(self.product1, 2, 10000000)

        picking2 = self._make_out_picking_as_asset(self.product1, 2)
        self._validate_picking(picking2)

        assets = self._search_asset_is_in_draft(picking2.move_line_ids.lot_id)

        self.assertEqual(assets[0].value, 10000000)
        self.assertEqual(assets[1].value, 10000000)

        # Case: asset 1 is in open state, asset 2 is in draft state
        # two asset with same serial
        # Action: validate the asset 1
        lot1 = assets[1].production_lot_id
        assets[1].production_lot_id = assets[0].production_lot_id
        assets[0].validate()
        with self.assertRaises(UserError):
            assets[1].validate()

        # Case: two asset are in open state
        # Action: change serial of asset1 with same serial
        assets[1].production_lot_id = lot1
        assets[1].validate()
        wizard = self.env['account.asset.asset.add.wizard'].with_context({
                'active_id': assets[1].id,
                'active_ids':[assets[1].id]
                }).create({
                    'production_lot_id': assets[0].production_lot_id.id
                    })
        with self.assertRaises(UserError):
            wizard.action_add_value()

    def test_07_out_picking_with_storable_product_tracking(self):
        # The product must be set asset category
        self.product1.asset_category_id = False
        self.product1.categ_id.property_valuation = 'real_time'

        self.assertEqual(self.product1.type, 'product')
        self.assertEqual(self.product1.tracking, 'serial')
        self.assertEqual(self.product1.valuation, 'real_time')
        self.assertFalse(self.product1.asset_category_id)

        picking = self._make_out_picking_as_asset(self.product1, 1)
        self.assertRaises(UserError, picking.button_validate)
