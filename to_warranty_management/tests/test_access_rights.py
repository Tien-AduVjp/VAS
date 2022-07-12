from odoo import fields
from odoo.tests import tagged
from odoo.exceptions import AccessError
from .test_base import TestBase


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(TestBase):

    def test_access_warranty_user_read(self):
        """ [Security Test] """
        self.milestone_30_days.with_user(self.user_read).read()

        with self.assertRaises(AccessError):
            self.env['product.milestone'].with_user(self.user_read).create({
                'name': '90 days',
                'amount': 90,
                'uom_id': self.env.ref('uom.product_uom_day').id
            })

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_read).write({'amount': 30})

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_read).unlink()

        self.product.warranty_policy_ids.with_user(self.user_read).read()

        warranty_policy = self.env['warranty.policy'].with_user(self.user_read).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'product_tmpl_id': self.product.product_tmpl_id.id
        })

        warranty_policy.with_user(self.user_read).write({'apply_to': 'sale'})

        with self.assertRaises(AccessError):
            warranty_policy.with_user(self.user_read).unlink()

        self.warranty_claim.warranty_claim_policy_ids.with_user(self.user_read).read()

        warranty_claim_policy = self.env['warranty.claim.policy'].with_user(self.user_read).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'operation_start': 1.0,
            'current_measurement': 1.0,
            'warranty_claim_id': self.warranty_claim.id
        })

        warranty_claim_policy.with_user(self.user_read).write({'apply_to': 'sale'})

        with self.assertRaises(AccessError):
            warranty_claim_policy.with_user(self.user_read).unlink()

        self.warranty_claim.with_user(self.user_read).read()

        warranty_claim = self.env['warranty.claim'].with_user(self.user_read).create({
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

        warranty_claim.with_user(self.user_read).write({'type': 'vendor'})

        with self.assertRaises(AccessError):
            warranty_claim.with_user(self.user_read).unlink()

    def test_access_warranty_user(self):
        """ [Security Test] TC01 """
        self.milestone_30_days.with_user(self.user_user).read()

        """ [Security Test] TC02 """
        with self.assertRaises(AccessError):
            self.env['product.milestone'].with_user(self.user_user).create({
                'name': '90 days',
                'amount': 90,
                'uom_id': self.env.ref('uom.product_uom_day').id
            })

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_user).write({'amount': 30})

        with self.assertRaises(AccessError):
            self.milestone_30_days.with_user(self.user_user).unlink()

        """ [Security Test] TC03 """
        self.product.warranty_policy_ids.with_user(self.user_user).read()

        warranty_policy = self.env['warranty.policy'].with_user(self.user_user).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'product_tmpl_id': self.product.product_tmpl_id.id
        })

        warranty_policy.with_user(self.user_user).write({'apply_to': 'sale'})

        """ [Security Test] TC04 """
        with self.assertRaises(AccessError):
            warranty_policy.with_user(self.user_user).unlink()

        """ [Security Test] TC05 """
        self.warranty_claim.warranty_claim_policy_ids.with_user(self.user_user).read()

        warranty_claim_policy = self.env['warranty.claim.policy'].with_user(self.user_user).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'operation_start': 1.0,
            'current_measurement': 1.0,
            'warranty_claim_id': self.warranty_claim.id
        })

        warranty_claim_policy.with_user(self.user_user).write({'apply_to': 'sale'})

        """ [Security Test] TC06 """
        with self.assertRaises(AccessError):
            warranty_claim_policy.with_user(self.user_user).unlink()

        """ [Security Test] TC07 """
        #with self.assertRaises(AccessError):
        self.warranty_claim.with_user(self.user_user).read()

        warranty_claim = self.env['warranty.claim'].with_user(self.user_user).create({
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

        warranty_claim.with_user(self.user_user).write({'type': 'vendor'})

        """ [Security Test] TC08 """
        with self.assertRaises(AccessError):
            warranty_claim.with_user(self.user_user).unlink()

    def test_access_warranty_manager(self):
        """ [Security Test] TC09 """
        self.milestone_30_days.with_user(self.user_manager).read()

        product_milestone = self.env['product.milestone'].with_user(self.user_manager).create({
            'name': '90 days',
            'amount': 90,
            'uom_id': self.env.ref('uom.product_uom_day').id
        })

        product_milestone.with_user(self.user_manager).write({'amount': 90})

        product_milestone.with_user(self.user_manager).unlink()

        """ [Security Test] TC10 """
        self.product.warranty_policy_ids.with_user(self.user_manager).read()

        warranty_policy = self.env['warranty.policy'].with_user(self.user_manager).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'product_tmpl_id': self.product.product_tmpl_id.id
        })

        warranty_policy.with_user(self.user_manager).write({'apply_to': 'sale'})

        warranty_policy.with_user(self.user_manager).unlink()

        """ [Security Test] TC11 """
        self.warranty_claim.warranty_claim_policy_ids.with_user(self.user_manager).read()

        warranty_claim_policy = self.env['warranty.claim.policy'].with_user(self.user_manager).create({
            'product_milestone_id': self.milestone_100_lit.id,
            'apply_to': 'sale',
            'operation_start': 1.0,
            'current_measurement': 1.0,
            'warranty_claim_id': self.warranty_claim.id
        })

        warranty_claim_policy.with_user(self.user_manager).write({'apply_to': 'sale'})

        warranty_claim_policy.with_user(self.user_manager).unlink()

        """ [Security Test] TC12 """
        self.warranty_claim.with_user(self.user_manager).read()

        warranty_claim = self.env['warranty.claim'].with_user(self.user_manager).create({
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

        warranty_claim.with_user(self.user_manager).write({'type': 'vendor'})

        warranty_claim.with_user(self.user_manager).unlink()
