from odoo.exceptions import UserError
from odoo.tests import tagged

from .test_voucher_issue_order import TestVoucherIssueOrder


@tagged('post_install', '-at_install')
class TestVoucherGiveOrder(TestVoucherIssueOrder):
    
    def test_01_create_give_voucher(self):
        self.assertIn(self.give_voucher.id, self.GiveVoucher.search([]).ids, "Create failed")

    def test_02_1_confirm_voucher_give_order(self):
        # Confirm voucher give order when have vouchers not in status inactivated
        self.voucher.write({'state': 'activated'})
        self.give_voucher.write({'voucher_ids': [(6, 0, [self.voucher.id])]})
        with self.assertRaises(UserError):
            self.give_voucher.action_confirm()
    
    def test_02_2_confirm_voucher_give_order(self):
        # Confirm voucher give order when have vouchers in status inactivated
        self.give_voucher.write({'voucher_ids': [(6, 0, [self.voucher.id])]})
        self.give_voucher.action_confirm()
        self.assertEqual(self.give_voucher.state, 'confirmed', "Confirm failed")
    
    def test_03_confirm_voucher_give_order(self):
        # Confirm voucher give order when not have vouchers
        with self.assertRaises(UserError):
            self.give_voucher.action_confirm()
    
    def test_04_delete_voucher_give_order(self):
        # Delete voucher give order in status draft
        self.give_voucher.unlink()
    
    def test_05_delete_voucher_give_order(self):
        # Delete voucher give order not in status draft
        self.give_voucher.write({'voucher_ids': [(6, 0, [self.voucher.id])]})
        self.give_voucher.action_confirm()
        with self.assertRaises(UserError):
            self.give_voucher.unlink()
    
    def test_06_duplicate_give_order(self):
        give_voucher_copy = self.give_voucher
        self.assertIn(give_voucher_copy.id, self.GiveVoucher.search([]).ids, "Duplicate failed")
        
    def test_07_08_give_voucher_give_order(self):
        self.issue_order.action_issue()
        vouchers = self.Voucher.search([('issue_order_id', '=', self.issue_order.id)])
    
        # Give with vouchers in status inactive 
        self.give_voucher.write({'voucher_ids': [(6, 0, vouchers.ids)]})
        self.give_voucher.action_confirm()
        self.give_voucher.action_give()
        self.assertEqual(self.give_voucher.state, 'done', "Give failed")
        for voucher in vouchers:
            self.assertEqual(voucher.state, 'activated')
        
        # Give with vouchers not in status inactive 
        give_voucher_order_new = self.give_voucher.copy()
        give_voucher_order_new.write({'voucher_ids': [(6, 0, vouchers.ids)]})
        with self.assertRaises(UserError):
            give_voucher_order_new.action_confirm()
            give_voucher_order_new.action_give()
