from datetime import date, timedelta

from odoo.exceptions import UserError
from odoo.tests import tagged

from .test_voucher_issue_order import TestVoucherIssueOrder


@tagged('post_install', '-at_install')
class TestVoucher(TestVoucherIssueOrder):

    def test_promotion_voucher(self):
        self.issue_order.action_issue()
        voucher = self.Voucher.search([('issue_order_id', '=', self.issue_order.id)], limit=1)
        # Check the change of voucher after issue
        self.assertEqual(voucher.product_id.id, self.issue_order.product_id.id)
        self.assertEqual(voucher.voucher_type_id.id, self.issue_order.product_id.voucher_type_id.id)
        self.assertEqual(voucher.current_stock_location_id.id, self.issue_order.picking_type_id.default_location_dest_id.id)
        self.assertEqual(voucher.value, voucher.product_id.value)
        self.assertEqual(voucher.value, voucher.product_id.product_tmpl_id.value)
        self.assertEqual(voucher.state, 'new')
        self.assertEqual(voucher.valid_duration, self.issue_order.valid_duration)
        self.assertEqual(voucher.issue_date, self.issue_order.issued_date)

        # Check the change of voucher after give
        self.give_voucher.write({'voucher_ids': [(6, 0, [voucher.id])]})
        self.give_voucher.action_confirm()
        self.give_voucher.action_give()
        self.assertEqual(voucher.state, 'activated')
        self.assertEqual(voucher.activated_date, date.today())
        self.assertEqual(voucher.expiry_date, voucher.activated_date + timedelta(days=voucher.valid_duration))

    def test_extend_expiry_date_voucher(self):
        self.issue_order.action_issue()
        voucher = self.Voucher.search([('issue_order_id', '=', self.issue_order.id)], limit=1)
        voucher.action_set_expiry()
        # Extend expiry date of voucher in status expired
        extend_date = self.ExtendVoucher.create({'valid_duration': 10, 'voucher_ids': [(6, 0, [voucher.id])]})
        extend_date.action_extend()
        self.assertEqual(voucher.state, 'activated')
        self.assertEqual(voucher.expiry_date, date.today() + timedelta(days=extend_date.valid_duration))

    def test_set_expired_voucher(self):
        self.issue_order.action_issue()
        voucher = self.Voucher.search([('issue_order_id', '=', self.issue_order.id)], limit=1)
        # Set expired voucher not in status expired
        voucher.action_set_expiry()
        self.assertEqual(voucher.state, 'expired')
        # Set expired voucher in status expired
        with self.assertRaises(UserError):
            voucher.action_set_expiry()

    def test_cron_check_expired (self):
        # The vouchers expiration date is bigger than today
        self.voucher.write({'expiry_date': date.today() + timedelta(days=1)})
        self.cron_hero.method_direct_trigger()
        self.assertNotEqual(self.voucher.state, 'expired')

        # The vouchers expiration date has passed
        self.voucher.write({'expiry_date': date.today() - timedelta(days=1)})
        self.cron_hero.method_direct_trigger()
        self.assertEqual(self.voucher.state, 'expired')
