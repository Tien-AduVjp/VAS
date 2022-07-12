from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .test_voucher_issue_order import TestVoucherIssueOrder


@tagged('post_install', '-at_install')
class TestVoucherMoveOrder(TestVoucherIssueOrder):

    def test_01_create_duplicate_move_order(self):
        # check create
        self.assertIn(self.voucher_move_order.id, self.VoucherMoveOrder.search([]).ids, "Create failed")
        # check duplicate
        move_order = self.voucher_move_order.copy()
        self.assertFalse(move_order.voucher_ids)

    def test_02_confirm_voucher_move_order(self):
        # Confirm voucher move order when not have vouchers
        with self.assertRaises(UserError):
            self.voucher_move_order.action_confirm()

    def test_03_confirm_voucher_move_order(self):
        # Confirm voucher move order when have vouchers not in status inactivated
        with self.assertRaises(UserError):
            self.voucher.write({'state': 'activated'})
            self.voucher_move_order.write({'voucher_ids': [(6, 0, [self.voucher.id])]})
            self.voucher_move_order.action_confirm()

        # Confirm voucher move order when have vouchers in status inactivated
        self.voucher_move_order.write({'voucher_ids': [(6, 0, [self.voucher.id])]})
        self.voucher_move_order.action_confirm()
        self.assertEqual(self.voucher_move_order.state, 'confirmed', "Confirm failed")

    def test_04_delete_voucher_move_order(self):
        # Delete voucher move order in status draft
        self.voucher_move_order.unlink()
        self.assertNotIn(self.voucher_move_order.id, self.VoucherMoveOrder.search([]).ids, "Delete failed")

    def test_05_delete_voucher_move_order(self):
        # Delete voucher move order not in status draft
        with self.assertRaises(UserError):
            self.voucher_move_order.write({'voucher_ids': [(6, 0, [self.voucher.id])]})
            self.voucher_move_order.action_confirm()
            self.voucher_move_order.unlink()

    def test_06_move_voucher_move_order(self):
        self.issue_order.action_issue()
        vouchers = self.Voucher.search([('issue_order_id', '=', self.issue_order.id)])

        # Move without voucher
        with self.assertRaises(UserError):
            self.voucher_move_order.action_move()

        # Move with inactive and in-stock vouchers
        self.voucher_move_order.write({'voucher_ids': [(6, 0, vouchers.ids)]})
        self.voucher_move_order.action_confirm()
        self.voucher_move_order.action_move()
        self.assertEqual(self.voucher_move_order.state, 'done', "Move failed")

        # Move with vouchers that are inactive and out of stock
        voucher_move_order_new = self.voucher_move_order_form.save()
        voucher_move_order_new.write({'voucher_ids': [(6, 0, vouchers.ids)]})
        with self.assertRaises(ValidationError):
            voucher_move_order_new.action_confirm()
            voucher_move_order_new.action_move()
