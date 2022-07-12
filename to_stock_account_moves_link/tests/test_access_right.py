from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import Common


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):

    #Case 1
    def test_access_right_user_inventory(self):
        self.picking = self._make_in_picking(self.product_storeable)
        picking= self.picking.with_user(self.user_inventory)
        with self.assertRaises(AccessError):
            picking.account_move_ids.read()

    #Case 2
    def test_access_right_user_inventory_billing(self):
        self.picking = self._make_in_picking(self.product_storeable)
        picking= self.picking.with_user(self.user_inventory_billing)
        with self.assertRaises(AccessError):
            picking.account_move_ids.read()

    #Case 3
    def test_access_right_user_inventory_accountant_admin(self):
        self.picking = self._make_in_picking(self.product_storeable)
        picking= self.picking.with_user(self.user_inventory_accountant_admin)
        self.assertEqual(picking.account_moves_count, 1)

    #Case 4
    def test_access_right_user_accountant_billing(self):
        self.picking = self._make_in_picking(self.product_storeable)
        picking= self.picking.with_user(self.user_accountant_billing)
        with self.assertRaises(AccessError):
            picking.account_move_ids.stock_move_id.read()

    #Case 5
    def test_access_right_user_accountant(self):
        picking = self._make_in_picking(self.product_storeable)
        self.assertGreater(picking.account_moves_count, 0)
