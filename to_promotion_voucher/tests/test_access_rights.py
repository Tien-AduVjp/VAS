from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import Form

from .test_common import TestCommon


@tagged('access_rights')
class TestAccessRight(TestCommon):
    
    def test_access_right_promotion_voucher_user(self):
        # Promotion voucher user access rights to the product
        with self.assertRaises(AccessError):
            self.voucher_product.with_user(self.promotion_voucher_user).read()
        with self.assertRaises(AccessError):
            self.Product.with_user(self.promotion_voucher_user).create({
                'tracking': 'serial',
                'type': 'product',
                'voucher_type_id': self.voucher_type.id,
                'name': 'Voucher 50%'
            })
        with self.assertRaises(AccessError):
            self.voucher_product.with_user(self.promotion_voucher_user).write({'name': 'Test Case'})
        with self.assertRaises(AccessError):
            self.voucher_product.with_user(self.promotion_voucher_user).unlink()

        # Promotion voucher user access rights to the voucher type
        voucher_type = self.VoucherType.with_user(self.promotion_voucher_user).create({
            'name': 'Voucher Type',
            'value': 10,
            'valid_duration': 30
        })
        voucher_type.with_user(self.promotion_voucher_user).read()
        voucher_type.with_user(self.promotion_voucher_user).write({'name': 'Discount'})
        voucher_type.with_user(self.promotion_voucher_user).unlink()
        
        # Promotion voucher user access rights to the issue voucher
        issue_voucher_form = Form(self.VoucherIssueOrder.with_user(self.promotion_voucher_user))
        issue_voucher_form.product_id = self.voucher_product
        issue_voucher = issue_voucher_form.save()
        issue_voucher.with_user(self.promotion_voucher_user).read()
        issue_voucher.with_user(self.promotion_voucher_user).write({'voucher_qty': 10})
        issue_voucher.with_user(self.promotion_voucher_user).unlink()
        
        # Promotion voucher user access rights to the voucher move order
        voucher_move_form = Form(self.VoucherMoveOrder.with_user(self.promotion_voucher_user))
        voucher_move_form.warehouse_id = self.env.ref('stock.warehouse0')
        voucher_move = voucher_move_form.save()
        voucher_move.with_user(self.promotion_voucher_user).read()
        voucher_move.with_user(self.promotion_voucher_user).write({'origin': 'Demo'})
        voucher_move.with_user(self.promotion_voucher_user).unlink()
        
        # Promotion voucher user access rights to the voucher
        with self.assertRaises(AccessError):
            voucher = self.Voucher.with_user(self.promotion_voucher_user).create({'name': 'Voucher 10%'})
        self.voucher.with_user(self.promotion_voucher_user).read()
        with self.assertRaises(AccessError):
            self.voucher.with_user(self.promotion_voucher_user).write({'name': 'Voucher 50%'})
        with self.assertRaises(AccessError):
            self.voucher.with_user(self.promotion_voucher_user).unlink()
        
        # Promotion voucher user access rights to the give vouchers
        with self.assertRaises(AccessError):
            give_voucher = self.GiveVoucher.with_user(self.promotion_voucher_user).create({'origin': 'Company'})
        self.give_voucher.with_user(self.promotion_voucher_user).read()
        with self.assertRaises(AccessError):
            self.give_voucher.with_user(self.promotion_voucher_user).write({'origin': 'Admin'})
        with self.assertRaises(AccessError):
            self.give_voucher.with_user(self.promotion_voucher_user).unlink()
    
    def test_access_right_promotion_voucher_manager(self):
        # Promotion voucher manager access rights to the product
        voucher_product = self.Product.with_user(self.promotion_voucher_manager).create({
            'tracking': 'serial',
            'type': 'product',
            'voucher_type_id': self.voucher_type.id,
            'name': 'Voucher 50%'
        })
        voucher_product.with_user(self.promotion_voucher_manager).read()
        voucher_product.with_user(self.promotion_voucher_manager).write({'name': 'Test Case'})
        voucher_product.with_user(self.promotion_voucher_manager).unlink()

        # Promotion voucher manager access rights to the voucher type
        voucher_type = self.VoucherType.with_user(self.promotion_voucher_manager).create({
            'name': 'Voucher Type',
            'value': 10,
            'valid_duration': 30
        })
        voucher_type.with_user(self.promotion_voucher_manager).read()
        voucher_type.with_user(self.promotion_voucher_manager).write({'name': 'Discount'})
        voucher_type.with_user(self.promotion_voucher_manager).unlink()
        
        # Promotion voucher manager access rights to the issue voucher
        issue_voucher_form = Form(self.VoucherIssueOrder.with_user(self.promotion_voucher_manager))
        issue_voucher_form.product_id = self.voucher_product
        issue_voucher = issue_voucher_form.save()
        issue_voucher.with_user(self.promotion_voucher_manager).read()
        issue_voucher.with_user(self.promotion_voucher_manager).write({'voucher_qty': 10})
        issue_voucher.with_user(self.promotion_voucher_manager).unlink()
        
        # Promotion voucher manager access rights to the voucher move order
        voucher_move_form = Form(self.VoucherMoveOrder.with_user(self.promotion_voucher_manager))
        voucher_move_form.warehouse_id = self.env.ref('stock.warehouse0')
        voucher_move = voucher_move_form.save()
        voucher_move.with_user(self.promotion_voucher_manager).read()
        voucher_move.with_user(self.promotion_voucher_manager).write({'origin': 'Demo'})
        voucher_move.with_user(self.promotion_voucher_manager).unlink()
        
        # Promotion voucher manager access rights to the voucher
        voucher = self.Voucher.with_user(self.promotion_voucher_manager).create({'name': 'Voucher 10%'})
        voucher.with_user(self.promotion_voucher_manager).read()
        voucher.with_user(self.promotion_voucher_manager).write({'name': 'Voucher 50%'})
        voucher.with_user(self.promotion_voucher_manager).unlink()
        
        # Promotion voucher user access rights to the give vouchers
        give_voucher = self.GiveVoucher.with_user(self.promotion_voucher_manager).create({'origin': 'Company'})
        give_voucher.with_user(self.promotion_voucher_manager).read()
        give_voucher.with_user(self.promotion_voucher_manager).write({'origin': 'Admin'})
        give_voucher.with_user(self.promotion_voucher_manager).unlink()
