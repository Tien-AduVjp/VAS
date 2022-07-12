from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestProductWarrantyPolicy(TestBase):

    def test_check_constrains_milestone_01(self):
        """
        [Functional Test] - TC01
        """
        with self.assertRaises(ValidationError):
            self.env['product.template'].create({
                'name': 'Test Product Invalid 1',
                'warranty_period': 12,
                'warranty_policy_ids': [(0, 0, {
                    'product_milestone_id': self.milestone_30_days.id,
                    'apply_to': 'sale',
                }), (0, 0, {
                    'product_milestone_id': self.milestone_15_days.id,
                    'apply_to': 'sale',
                })]
            })

    def test_check_constrains_milestone_02(self):
        """
        [Functional Test] - TC02
        """
        checked_product = self.product
        current_warranty_policy_vals = []
        with self.assertRaises(ValidationError):
            current_warranty_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_15_days.id,
                                                                                'apply_to': 'sale'}))
            checked_product.write({'warranty_policy_ids': current_warranty_policy_vals})

    def test_check_constrains_milestone_03(self):
        """
        [Functional Test] - TC03
        """
        self.env['product.template'].create({
            'name': 'Test Product Valid 1',
            'warranty_period': 12,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'sale',
            }), (0, 0, {
                'product_milestone_id': self.milestone_1000_km.id,
                'apply_to': 'sale',
            })]
        })

    def test_check_constrains_milestone_04(self):
        """
        [Functional Test] - TC04
        """
        checked_product = self.product
        current_warranty_policy_vals = []
        current_warranty_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_100_lit.id,
                                                                            'apply_to': 'sale'}))
        checked_product.write({'warranty_policy_ids': current_warranty_policy_vals})

    def test_check_constrains_milestone_05(self):
        """
        [Functional Test] - TC05
        """
        with self.assertRaises(ValidationError):
            self.env['product.template'].create({
                'name': 'Test Product Invalid 2',
                'warranty_period': 12,
                'warranty_policy_ids': [(0, 0, {
                    'product_milestone_id': self.milestone_30_days.id,
                    'apply_to': 'purchase',
                }), (0, 0, {
                    'product_milestone_id': self.milestone_15_days.id,
                    'apply_to': 'purchase',
                })]
            })

    def test_check_constrains_milestone_06(self):
        """
        [Functional Test] - TC06
        """
        checked_product = self.product
        current_warranty_policy_vals = []
        with self.assertRaises(ValidationError):
            current_warranty_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_30_days.id,
                                                                                'apply_to': 'purchase'}))
            checked_product.write({'warranty_policy_ids': current_warranty_policy_vals})

    def test_check_constrains_milestone_07(self):
        """
        [Functional Test] - TC07
        """
        self.env['product.template'].create({
            'name': 'Test Product Valid 2',
            'warranty_period': 12,
            'warranty_policy_ids': [(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'purchase',
            }), (0, 0, {
                'product_milestone_id': self.milestone_1000_km.id,
                'apply_to': 'purchase',
            })]
        })

    def test_check_constrains_milestone_08(self):
        """
        [Functional Test] - TC08
        """
        checked_product = self.product
        current_warranty_policy_vals = []
        current_warranty_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_100_lit.id,
                                                                            'apply_to': 'purchase'}))
        checked_product.write({'warranty_policy_ids': current_warranty_policy_vals})
