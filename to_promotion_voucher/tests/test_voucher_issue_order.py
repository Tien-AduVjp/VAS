from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import Form

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestVoucherIssueOrder(TestCommon):
    
    def setUp(self):
        super(TestVoucherIssueOrder, self).setUp()
        virtual_location_production = self.StockLocation.create({
            'name': 'Demo Location',
            'location_id': self.env.ref('stock.stock_location_locations_virtual').id,
            'usage': 'production'
        })
        issue_order_form = Form(self.VoucherIssueOrder)
        issue_order_form.product_id = self.voucher_product
        if not issue_order_form.picking_type_id.default_location_src_id:
            issue_order_form.picking_type_id.default_location_src_id = virtual_location_production
        if not issue_order_form.picking_type_id.default_location_dest_id:
            issue_order_form.picking_type_id.default_location_dest_id = self.env.ref('stock.stock_location_stock')
        self.issue_order = issue_order_form.save()

    def test_01_1_delete_draft_voucher_issue_order(self):
        # Set to draft voucher issue order
        self.issue_order.action_draft()
        self.assertEqual(self.issue_order.state, 'draft', "Status does not have to draft")
        # Delete voucher issue order when not in confirm or issue status
        self.issue_order.unlink()
    
    def test_01_2_delete_cancel_voucher_issue_order(self):
        # Cancel voucher issue order
        self.issue_order.action_cancel()
        self.assertEqual(self.issue_order.state, 'cancel', "Status does not have to cancel")
        # Delete voucher issue order when not in confirm or issue status
        self.issue_order.unlink()

    def test_02_delete_comfirm_voucher_issue_order(self):
        # Comfirm voucher issue order
        self.issue_order.action_confirm()
        self.assertEqual(self.issue_order.state, 'confirmed', "Status does not have to confirm")
        # Delete voucher issue order when in confirm status
        with self.assertRaises(UserError):
            self.issue_order.unlink()
    
    def test_03_issue_voucher_not_default_location(self):
        # Action issue voucher issue order when pikcing type not have default destination location or default source location
        self.issue_order.picking_type_id.write({'default_location_dest_id': False})
        with self.assertRaises(UserError):
            self.issue_order.action_issue()
    
    def test_04_issue_voucher_have_default_location(self):
        # Action issue voucher issue order when pikcing type have default destination location and default source location
        self.issue_order.action_issue()
        self.assertEqual(self.issue_order.state, 'done', "Status does not have to done")
        self.assertEqual(self.issue_order.issued_date, fields.Date.today(), "Release date is not today")
        vouchers = self.Voucher.search([('issue_order_id', '=', self.issue_order.id)])
        self.assertEqual(len(vouchers), self.issue_order.voucher_qty, "Issue voucher failed")
