from datetime import datetime

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestAccessRights(TestBase):

    def test_access_warranty_user_read(self):
        """ [Security Test] """
        self.po1.with_user(self.user_read).read(['partner_id', 'order_line'])

        with self.assertRaises(AccessError):
            self.env['purchase.order'].with_user(self.user_read).create({
                'partner_id': self.partner.id,
                'order_line': [
                    (0, 0, {
                        'name': self.product.name,
                        'product_id': self.product.id,
                        'product_uom': self.uom_unit.id,
                        'product_qty': 2.0,
                        'price_unit': 100.0,
                        'date_planned': datetime.today(),
                    })
                ],
            })
        with self.assertRaises(AccessError):
            self.po1.with_user(self.user_read).write({'partner_id': self.partner.id})

        with self.assertRaises(AccessError):
            self.po4.with_user(self.user_read).unlink()

        self.po1.order_line[0].with_user(self.user_read).read(['product_id'])

        with self.assertRaises(AccessError):
            self.env['purchase.order.line'].with_user(self.user_read).create({
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.uom_unit.id,
                'product_qty': 2.0,
                'price_unit': 100.0,
                'date_planned': datetime.today(),
                'order_id':self.po1.id
            })
        with self.assertRaises(AccessError):
            self.po1.order_line[0].with_user(self.user_read).write({'product_qty': 3.0, })

        with self.assertRaises(AccessError):
            self.po4.order_line[0].with_user(self.user_read).unlink()


    def test_access_warranty_user(self):
        """ [Security Test] TC01 """
        with self.assertRaises(AccessError):
            self.po1.with_user(self.user_user).read(['partner_id', 'order_line'])

        """ [Security Test] TC02 """
        with self.assertRaises(AccessError):
            self.env['purchase.order'].with_user(self.user_user).create({
                'partner_id': self.partner.id,
                'order_line': [
                    (0, 0, {
                        'name': self.product.name,
                        'product_id': self.product.id,
                        'product_uom': self.uom_unit.id,
                        'product_qty': 2.0,
                        'price_unit': 100.0,
                        'date_planned': datetime.today(),
                    })
                ],
            })

        with self.assertRaises(AccessError):
            self.po1.with_user(self.user_user).write({'partner_id': self.partner.id})

        with self.assertRaises(AccessError):
            self.po4.with_user(self.user_user).unlink()

        """ [Security Test] TC03 """
        with self.assertRaises(AccessError):
            self.po1.order_line[0].with_user(self.user_user).read(['product_id'])

        """ [Security Test] TC04 """
        with self.assertRaises(AccessError):
            self.env['purchase.order.line'].with_user(self.user_user).create({
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.uom_unit.id,
                'product_qty': 2.0,
                'price_unit': 100.0,
                'date_planned': datetime.today(),
                'order_id':self.po1.id
            })
        with self.assertRaises(AccessError):
            self.po1.order_line[0].with_user(self.user_user).write({'product_qty': 3.0, })

        with self.assertRaises(AccessError):
            self.po4.order_line[0].with_user(self.user_user).unlink()


    def test_access_warranty_manager(self):
        """ [Security Test] TC05 """
        self.po1.with_user(self.user_manager).read(['partner_id', 'order_line'])

        """ [Security Test] TC06 """
        with self.assertRaises(AccessError):
            self.env['purchase.order'].with_user(self.user_manager).create({
                'partner_id': self.partner.id,
                'order_line': [
                    (0, 0, {
                        'name': self.product.name,
                        'product_id': self.product.id,
                        'product_uom': self.uom_unit.id,
                        'product_qty': 2.0,
                        'price_unit': 100.0,
                        'date_planned': datetime.today(),
                    })
                ],
            })

        with self.assertRaises(AccessError):
            self.po1.with_user(self.user_manager).write({'partner_id': self.partner.id})

        with self.assertRaises(AccessError):
            self.po4.with_user(self.user_manager).unlink()

        """ [Security Test] TC07 """
        self.po1.order_line[0].with_user(self.user_manager).read(['product_id'])

        """ [Security Test] TC08 """
        with self.assertRaises(AccessError):
            self.env['purchase.order.line'].with_user(self.user_manager).create({
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.uom_unit.id,
                'product_qty': 2.0,
                'price_unit': 100.0,
                'date_planned': datetime.today(),
                'order_id':self.po1.id
            })
        with self.assertRaises(AccessError):
            self.po1.order_line[0].with_user(self.user_manager).write({'product_qty': 3.0, })

        with self.assertRaises(AccessError):
            self.po4.order_line[0].with_user(self.user_manager).unlink()

    def test_access_purchase_user(self):
        """ [Security Test] TC09 """
        self.milestone_30_days.with_user(self.user_purchase_user).read()

        with self.assertRaises(AccessError):
            self.env['product.milestone'].with_user(self.user_purchase_user).create({
                'name': '90 days',
                'amount': 90,
                'uom_id': self.env.ref('uom.product_uom_day').id
            })

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_purchase_user).write({'amount': 30})

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_purchase_user).unlink()

        self.product.warranty_policy_ids.with_user(self.user_purchase_user).read()

        warranty_policy = self.env['warranty.policy'].with_user(self.user_purchase_user).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'product_tmpl_id': self.product.product_tmpl_id.id
        })

        warranty_policy.with_user(self.user_purchase_user).write({'apply_to': 'sale'})

        with self.assertRaises(AccessError):
            warranty_policy.with_user(self.user_purchase_user).unlink()

        self.warranty_claim.warranty_claim_policy_ids.with_user(self.user_purchase_user).read()

        warranty_claim_policy = self.env['warranty.claim.policy'].with_user(self.user_purchase_user).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'operation_start': 1.0,
            'current_measurement': 1.0,
            'warranty_claim_id': self.warranty_claim.id
        })

        warranty_claim_policy.with_user(self.user_purchase_user).write({'apply_to': 'sale'})

        with self.assertRaises(AccessError):
            warranty_claim_policy.with_user(self.user_purchase_user).unlink()

        self.warranty_claim.with_user(self.user_purchase_user).read()

        warranty_claim = self.env['warranty.claim'].with_user(self.user_purchase_user).create({
            'name': 'Test Warranty Claim Test',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'warranty_start_date': fields.Date.from_string('2021-08-20'),
            'date_claim': fields.Date.from_string('2021-08-20'),
            'type': 'vendor',
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'purchase',
                'operation_start': 2.0,
                'current_measurement': 5.0
            })]
        })

        warranty_claim.with_user(self.user_purchase_user).write({'name': 'Test Warranty Claim Test Update'})

        with self.assertRaises(AccessError):
            warranty_claim.with_user(self.user_purchase_user).unlink()
