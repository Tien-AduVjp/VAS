from odoo import fields
from odoo.tests import tagged
from odoo.exceptions import AccessError

from .test_base import TestBase


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestBase):

    def test_access_warranty_user_read(self):
        """ [Security Test] """
        self.so1.with_user(self.user_read).read(['partner_id', 'order_line'])

        with self.assertRaises(AccessError):
            self.env['sale.order'].with_user(self.user_read).create({
                'partner_id': self.customer.id,
                'partner_invoice_id': self.customer.id,
                'partner_shipping_id': self.customer.id,
                'pricelist_id': self.pricelist_usd.id,
                'order_line': [
                    (0, 0, {
                        'name': self.product.name,
                        'product_id': self.product.id,
                        'product_uom': self.uom_unit.id,
                        'product_uom_qty': 2.0,
                        'price_unit': 100.0,
                    })
                ],
            })

        with self.assertRaises(AccessError):
            self.so1.with_user(self.user_read).write({'partner_id': self.partner.id})

        with self.assertRaises(AccessError):
            self.so4.with_user(self.user_read).unlink()

        self.so1.order_line[0].with_user(self.user_read).read(['product_id'])

        with self.assertRaises(AccessError):
            self.env['sale.order.line'].with_user(self.user_read).create({
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 2.0,
                'price_unit': 100.0,
                'order_id':self.so1.id
            })
        with self.assertRaises(AccessError):
            self.so1.order_line[0].with_user(self.user_read).write({'product_uom_qty': 3.0, })

        with self.assertRaises(AccessError):
            self.so4.order_line[0].with_user(self.user_read).unlink()

    def test_access_warranty_user(self):
        """ [Security Test] TC01 """
        self.so1.with_user(self.user_user).read(['partner_id', 'order_line'])

        """ [Security Test] TC02 """
        with self.assertRaises(AccessError):
            self.env['sale.order'].with_user(self.user_user).create({
                'partner_id': self.customer.id,
                'partner_invoice_id': self.customer.id,
                'partner_shipping_id': self.customer.id,
                'pricelist_id': self.pricelist_usd.id,
                'order_line': [
                    (0, 0, {
                        'name': self.product.name,
                        'product_id': self.product.id,
                        'product_uom': self.uom_unit.id,
                        'product_uom_qty': 2.0,
                        'price_unit': 100.0,
                    })
                ],
            })

        with self.assertRaises(AccessError):
            self.so1.with_user(self.user_user).write({'partner_id': self.partner.id})

        with self.assertRaises(AccessError):
            self.so4.with_user(self.user_user).unlink()

        """ [Security Test] TC03 """
        self.so1.order_line[0].with_user(self.user_user).read(['product_id'])

        """ [Security Test] TC04 """
        with self.assertRaises(AccessError):
            self.env['sale.order.line'].with_user(self.user_user).create({
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 2.0,
                'price_unit': 100.0,
                'order_id':self.so1.id
            })
        with self.assertRaises(AccessError):
            self.so1.order_line[0].with_user(self.user_user).write({'product_uom_qty': 3.0, })

        with self.assertRaises(AccessError):
            self.so4.order_line[0].with_user(self.user_user).unlink()

    def test_access_warranty_manager(self):
        """ [Security Test] TC05 """
        self.so1.with_user(self.user_manager).read(['partner_id', 'order_line'])

        """ [Security Test] TC06 """
        with self.assertRaises(AccessError):
            self.env['sale.order'].with_user(self.user_manager).create({
                'partner_id': self.customer.id,
                'partner_invoice_id': self.customer.id,
                'partner_shipping_id': self.customer.id,
                'pricelist_id': self.pricelist_usd.id,
                'order_line': [
                    (0, 0, {
                        'name': self.product.name,
                        'product_id': self.product.id,
                        'product_uom': self.uom_unit.id,
                        'product_uom_qty': 2.0,
                        'price_unit': 100.0,
                    })
                ],
            })

        with self.assertRaises(AccessError):
            self.so1.with_user(self.user_manager).write({'partner_id': self.partner.id})

        with self.assertRaises(AccessError):
            self.so4.with_user(self.user_manager).unlink()

        """ [Security Test] TC07 """
        self.so1.order_line[0].with_user(self.user_manager).read(['product_id'])

        """ [Security Test] TC08 """
        with self.assertRaises(AccessError):
            self.env['sale.order.line'].with_user(self.user_manager).create({
                'name': self.product.name,
                'product_id': self.product.id,
                'product_uom': self.uom_unit.id,
                'product_uom_qty': 2.0,
                'price_unit': 100.0,
                'order_id':self.so1.id
            })
        with self.assertRaises(AccessError):
            self.so1.order_line[0].with_user(self.user_manager).write({'product_uom_qty': 3.0, })

        with self.assertRaises(AccessError):
            self.so4.order_line[0].with_user(self.user_manager).unlink()

    def test_access_purchase_user(self):
        """ [Security Test] TC09 """
        self.milestone_30_days.with_user(self.user_salesman_user).read()

        with self.assertRaises(AccessError):
            self.env['product.milestone'].with_user(self.user_salesman_user).create({
                'name': '90 days',
                'amount': 90,
                'uom_id': self.env.ref('uom.product_uom_day').id
            })

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_salesman_user).write({'amount': 30})

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_salesman_user).unlink()

        self.product.warranty_policy_ids.with_user(self.user_salesman_user).read()

        warranty_policy = self.env['warranty.policy'].with_user(self.user_salesman_user).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'product_tmpl_id': self.product.product_tmpl_id.id
        })

        warranty_policy.with_user(self.user_salesman_user).write({'apply_to': 'sale'})

        with self.assertRaises(AccessError):
            warranty_policy.with_user(self.user_salesman_user).unlink()

        self.warranty_claim.warranty_claim_policy_ids.with_user(self.user_salesman_user).read()

        warranty_claim_policy = self.env['warranty.claim.policy'].with_user(self.user_salesman_user).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'operation_start': 1.0,
            'current_measurement': 1.0,
            'warranty_claim_id': self.warranty_claim.id
        })

        warranty_claim_policy.with_user(self.user_salesman_user).write({'apply_to': 'sale'})

        with self.assertRaises(AccessError):
            warranty_claim_policy.with_user(self.user_salesman_user).unlink()

        #with self.assertRaises(AccessError):
        self.warranty_claim.with_user(self.user_salesman_user).read()

        warranty_claim = self.env['warranty.claim'].with_user(self.user_salesman_user).create({
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

        warranty_claim.with_user(self.user_salesman_user).write({'name': 'Test Warranty Claim Test Update'})

        with self.assertRaises(AccessError):
            warranty_claim.with_user(self.user_salesman_user).unlink()
