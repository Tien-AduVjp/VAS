from odoo import fields
from odoo.tests import tagged
from odoo.exceptions import AccessError

from .test_base import TestBase


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestBase):

    def test_access_warranty_user(self):
        """ [Security Test] TC01 """
        self.lot1.with_user(self.user_user).read(['name'])

        """ [Security Test] TC02 """
        with self.assertRaises(AccessError):
            self.env['stock.production.lot'].with_user(self.user_user).create({
                'name': 'Test Lot 1',
                'product_id': self.product_lot1.id,
                'company_id': self.env.company.id,
                'warranty_start_date': fields.Date.from_string('2021-08-20'),
                'warranty_period': 12,
                'warranty_claim_policy_ids': [(0, 0, {
                    'product_milestone_id': self.milestone_15_days.id,
                    'apply_to': 'purchase',
                    'operation_start': 1.0,
                    'current_measurement': 1.0
                })]
            })

        with self.assertRaises(AccessError):
            self.lot1.with_user(self.user_user).write({'warranty_period': 15})

        with self.assertRaises(AccessError):
            self.lot1.with_user(self.user_user).unlink()

    def test_access_warranty_manager(self):
        """ [Security Test] TC03 """
        self.lot1.with_user(self.user_manager).read(['name'])

        """ [Security Test] TC04 """
        with self.assertRaises(AccessError):
            self.env['stock.production.lot'].with_user(self.user_manager).create({
                'name': 'Test Lot 1',
                'product_id': self.product_lot1.id,
                'company_id': self.env.company.id,
                'warranty_start_date': fields.Date.from_string('2021-08-20'),
                'warranty_period': 12,
                'warranty_claim_policy_ids': [(0, 0, {
                    'product_milestone_id': self.milestone_15_days.id,
                    'apply_to': 'purchase',
                    'operation_start': 1.0,
                    'current_measurement': 1.0
                })]
            })

        with self.assertRaises(AccessError):
            self.lot1.with_user(self.user_manager).write({'warranty_period': 15})

        with self.assertRaises(AccessError):
            self.lot1.with_user(self.user_manager).unlink()

    def test_access_stock_user(self):
        """ [Security Test] TC05 """
        self.milestone_30_days.with_user(self.user_stock_user).read()

        with self.assertRaises(AccessError):
            self.env['product.milestone'].with_user(self.user_stock_user).create({
                'name': '90 days',
                'amount': 90,
                'uom_id': self.env.ref('uom.product_uom_day').id
            })

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_stock_user).write({'amount': 30})

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_stock_user).unlink()

        self.product.warranty_policy_ids.with_user(self.user_stock_user).read()

        warranty_policy = self.env['warranty.policy'].with_user(self.user_stock_user).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'product_tmpl_id': self.product.product_tmpl_id.id
        })

        warranty_policy.with_user(self.user_stock_user).write({'apply_to': 'sale'})

        with self.assertRaises(AccessError):
            warranty_policy.with_user(self.user_stock_user).unlink()

        self.warranty_claim.warranty_claim_policy_ids.with_user(self.user_stock_user).read()

        warranty_claim_policy = self.env['warranty.claim.policy'].with_user(self.user_stock_user).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'operation_start': 1.0,
            'current_measurement': 1.0,
            'warranty_claim_id': self.warranty_claim.id
        })

        warranty_claim_policy.with_user(self.user_stock_user).write({'apply_to': 'sale'})

        with self.assertRaises(AccessError):
            warranty_claim_policy.with_user(self.user_stock_user).unlink()

        self.warranty_claim.with_user(self.user_stock_user).read()

        warranty_claim = self.env['warranty.claim'].with_user(self.user_stock_user).create({
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

        warranty_claim.with_user(self.user_stock_user).write({'name': 'Test Warranty Claim Test Update'})

        with self.assertRaises(AccessError):
            warranty_claim.with_user(self.user_stock_user).unlink()
