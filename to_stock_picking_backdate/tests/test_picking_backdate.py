from datetime import datetime

from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo.exceptions import AccessError
from odoo.addons.stock_account.tests import test_stockvaluation

from .common import TestCommon


@tagged('post_install', '-at_install', 'external', '-standard')
class TestPickingBackDate(TestCommon):

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_picking_with_manager_user_group(self):
        picking1, move1 = self.create_picking_move(self.productA,
                                                   self.supplier_location,
                                                   self.stock_location,
                                                   self.picking_type_in,
                                                   datetime(2021, 3, 25))
        picking1.with_user(self.manager_user).action_confirm()
        data = picking1.with_user(self.manager_user).with_context(open_stock_picking_backdate_wizard=True).button_validate()
        res_model = data.get('res_model', '')
        self.assertEqual('stock.picking.backdate', res_model, 'popup display not oke')

        picking2, move2 = self.create_picking_move(self.productA,
                                                   self.supplier_location,
                                                   self.stock_location,
                                                   self.picking_type_in,
                                                   datetime(2021, 3, 25))
        picking2.with_user(self.manager_user).action_confirm()
        backdate = datetime(2021, 3, 31, 9)
        picking_backdate = self.PickingBackdate.create({'picking_id': picking2.id, 'date': backdate})
        picking_backdate.with_user(self.manager_user).process()
        self.assertEqual(backdate, picking2.date_done, "Check date on 'stock picking' not oke")
        self.assertEqual(backdate, move2.date, "Check date on 'stock move' not oke")
        self.assertEqual(backdate, move2.stock_valuation_layer_ids[0].create_date, "Check date on 'stock valuation layer' not oke")

        picking3, move3 = self.create_picking_move(self.productA,
                                                   self.stock_location,
                                                   self.customer_location,
                                                   self.picking_type_out,
                                                   datetime(2021, 3, 25))
        picking3.with_user(self.manager_user).action_confirm()
        backdate = datetime(2021, 3, 31, 9)
        picking_backdate = self.PickingBackdate.create({'picking_id': picking3.id, 'date': backdate})
        picking_backdate.with_user(self.manager_user).process()
        self.assertEqual(backdate, picking3.date_done, "Check date on 'stock picking' not oke")
        self.assertEqual(backdate, move3.date, "Check date on 'stock move' not oke")
        self.assertEqual(backdate, move3.stock_valuation_layer_ids[0].create_date, "Check date on 'stock valuation layer' not oke")

        # check account
        picking4, move4 = self.create_picking_move(self.productB,
                                                   self.supplier_location,
                                                   self.stock_location,
                                                   self.picking_type_in,
                                                   datetime(2021, 3, 25))
        picking4.with_user(self.manager_user).action_confirm()
        backdate = datetime(2021, 3, 31, 9)
        picking_backdate = self.PickingBackdate.create({'picking_id': picking4.id, 'date': backdate})
        picking_backdate.with_user(self.manager_user).process()
        self.assertEqual(backdate.date(), picking4.move_ids_without_package[0].account_move_ids[0].date, "Check date on 'account move' not oke")

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_picking_with_backdate_stock_user_group(self):
        picking1, move1 = self.create_picking_move(self.productA,
                                                   self.supplier_location,
                                                   self.stock_location,
                                                   self.picking_type_in,
                                                   datetime(2021, 3, 25))
        picking1.with_user(self.backdate_stock_user).action_confirm()
        data = picking1.with_user(self.backdate_stock_user).with_context(open_stock_picking_backdate_wizard=True).button_validate()
        res_model = data.get('res_model', '')
        self.assertEqual('stock.picking.backdate', res_model, 'popup display not oke')

        picking2, move2 = self.create_picking_move(self.productA,
                                                   self.supplier_location,
                                                   self.stock_location,
                                                   self.picking_type_in,
                                                   datetime(2021, 3, 25))
        picking2.with_user(self.backdate_stock_user).action_confirm()
        backdate = datetime(2021, 3, 31, 9)
        picking_backdate = self.PickingBackdate.create({'picking_id': picking2.id, 'date': backdate})
        picking_backdate.with_user(self.backdate_stock_user).process()
        self.assertEqual(backdate, picking2.date_done, "Check date on 'stock picking' not oke")
        self.assertEqual(backdate, move2.date, "Check date on 'stock move' not oke")
        self.assertEqual(backdate, move2.stock_valuation_layer_ids[0].create_date, "Check date on 'stock valuation layer' not oke")

        picking3, move3 = self.create_picking_move(self.productA,
                                                   self.stock_location,
                                                   self.customer_location,
                                                   self.picking_type_out,
                                                   datetime(2021, 3, 25))
        picking3.with_user(self.backdate_stock_user).action_confirm()
        backdate = datetime(2021, 3, 31, 9)
        picking_backdate = self.PickingBackdate.create({'picking_id': picking3.id, 'date': backdate})
        picking_backdate.with_user(self.backdate_stock_user).process()
        self.assertEqual(backdate, picking3.date_done, "Check date on 'stock picking' not oke")
        self.assertEqual(backdate, move3.date, "Check date on 'stock move' not oke")
        self.assertEqual(backdate, move3.stock_valuation_layer_ids[0].create_date, "Check date on 'stock valuation layer' not oke")

        # check account
        picking4, move4 = self.create_picking_move(self.productB,
                                                   self.supplier_location,
                                                   self.stock_location,
                                                   self.picking_type_in,
                                                   datetime(2021, 3, 25))
        picking4.with_user(self.backdate_stock_user).action_confirm()
        backdate = datetime(2021, 3, 31, 9)
        picking_backdate = self.PickingBackdate.create({'picking_id': picking4.id, 'date': backdate})
        picking_backdate.with_user(self.backdate_stock_user).process()
        self.assertEqual(backdate.date(), picking4.move_ids_without_package[0].account_move_ids[0].date, "Check date on 'account move' not oke")

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_picking_with_stock_user_group(self):
        picking1, move1 = self.create_picking_move(self.productA,
                                                   self.supplier_location,
                                                   self.stock_location,
                                                   self.picking_type_in,
                                                   datetime(2021, 3, 25))
 
        picking1.with_user(self.stock_user).action_confirm()
        data = picking1.with_user(self.stock_user).button_validate()
        self.assertEqual(data, None, "don't popup display not oke")

    @mute_logger('odoo.addons.base.models.ir_model')
    def test_picking_with_backdate_user_group(self):
        picking1, move1 = self.create_picking_move(self.productA,
                                                   self.supplier_location,
                                                   self.stock_location,
                                                   self.picking_type_in,
                                                   datetime(2021, 3, 25))
        with self.assertRaises(AccessError):
            picking1.with_user(self.backdate_user).action_confirm()

        backdate = datetime(2021, 3, 31, 9)
        picking_backdate = self.PickingBackdate.create({'picking_id': picking1.id, 'date': backdate})
        with self.assertRaises(AccessError):
            picking_backdate.with_user(self.backdate_user).process()
