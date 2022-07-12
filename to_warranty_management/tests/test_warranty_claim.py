from odoo import fields
from odoo.tools import float_compare
from odoo.tests.common import Form, tagged
from odoo.exceptions import ValidationError, UserError

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestWarrantyClaim(TestBase):
    
    def test_compute_warranty_end_01(self):
        """
        [Form Test] - TC01 
        """
        with Form(self.env['warranty.claim.policy']) as f:
            f.operation_start = 2.0
            check_result = float_compare(f.operation_end, 2.0, 2)
            self.assertTrue(check_result == 0)
            f.product_milestone_id = self.milestone_30_days
            f.apply_to = 'sale'
            
    def test_compute_warranty_end_02(self):
        """
        [Form Test] - TC02
        """
        with Form(self.env['warranty.claim.policy']) as f:
            f.product_milestone_id = self.milestone_30_days
            f.operation_start = 2.0
            f.apply_to = 'sale'
            check_result = float_compare(f.operation_end, 32.0, 2)
            self.assertTrue(check_result == 0)
            
    def test_compute_warranty_end_03(self):
        """
        [Form Test] - TC03
        """
        with Form(self.env['warranty.claim.policy']) as f:
            f.product_milestone_id = self.milestone_30_days
            f.apply_to = 'sale'
            check_result = float_compare(f.operation_end, 30.0, 2)
            self.assertTrue(check_result == 0)
            f.operation_start = 2.0
            
    def test_compute_warranty_end_04(self):
        """
        [Form Test] - TC04
        """
        with Form(self.env['warranty.claim.policy']) as f:
            f.product_milestone_id = self.milestone_30_days
            f.operation_start = -2.0
            f.apply_to = 'sale'
            check_result = float_compare(f.operation_end, 28.0, 2)
            self.assertTrue(check_result == 0)
            
    def test_compute_state_01(self):
        """
        [Form Test] - TC05
        """
        with Form(self.env['warranty.claim.policy']) as f:
            f.operation_start = 2.0
            f.product_milestone_id = self.milestone_30_days
            f.apply_to = 'sale'
            f.current_measurement = 5.0
            self.assertEqual(f.state, 'ok')
            
    def test_compute_state_02(self):
        """
        [Form Test] - TC06
        """
        with Form(self.env['warranty.claim.policy']) as f:
            f.operation_start = 2.0
            f.product_milestone_id = self.milestone_30_days
            f.apply_to = 'sale'
            f.current_measurement = 35.0
            self.assertEqual(f.state, 'not_ok')
            
    def test_compute_state_03(self):
        """
        [Form Test] - TC07
        """
        with Form(self.env['warranty.claim.policy']) as f:
            f.operation_start = 2.02
            f.product_milestone_id = self.milestone_30_days
            f.apply_to = 'sale'
            f.current_measurement = 32.03
            self.assertEqual(f.state, 'not_ok')
            
    def test_compute_state_04(self):
        """
        [Form Test] - TC08
        """
        with Form(self.env['warranty.claim.policy']) as f:
            f.operation_start = 2.02
            f.product_milestone_id = self.milestone_30_days
            f.apply_to = 'sale'
            f.current_measurement = 32.01
            self.assertEqual(f.state, 'ok')
            
    def test_compute_warranty_period_01(self):
        """
        [Form Test] - TC09
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product_without_warranty_period
            f.partner_id = self.partner
            f.type = 'customer'
            self.assertEqual(f.warranty_period, False)
            
    def test_compute_warranty_period_02(self):
        """
        [Form Test] - TC10
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product
            f.partner_id = self.partner
            f.type = 'customer'
            self.assertEqual(f.warranty_period, 12)
        
    def test_compute_warranty_period_03(self):
        """
        [Form Test] - TC11
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product
            f.partner_id = self.partner
            f.warranty_period = 6
            f.type = 'customer'
            self.assertEqual(f.warranty_period, 6)
            
    def _compare_warranty_claim_policies(self, form_warranty_claim_policies, apply_to, product):
        policies = product.warranty_policy_ids.filtered(lambda wp: wp.apply_to == apply_to)
        if len(form_warranty_claim_policies) == len(policies):
            set_form_policies = set()
            set_policies = set()
            for idx in range(len(form_warranty_claim_policies)):
                line = form_warranty_claim_policies.edit(idx)
                set_form_policies.add((line.product_milestone_id.id, line.apply_to))
            for policy in policies:
                set_policies.add((policy.product_milestone_id.id, policy.apply_to))
            return set_form_policies == set_policies
        else:
            return False
    
    def test_compute_warranty_claim_policy_ids_01(self):
        """
        [Form Test] - TC12
        """
        with Form(self.env['warranty.claim']) as f:
            f.partner_id = self.partner
            f.type = 'customer'
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)
            f.product_id = self.product
            
    def test_compute_warranty_claim_policy_ids_02(self):
        """
        [Form Test] - TC13
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product
            f.partner_id = self.partner
            f.type = 'customer'
            self.assertTrue(self._compare_warranty_claim_policies(f.warranty_claim_policy_ids, 'sale', f.product_id))
            
    def test_compute_warranty_claim_policy_ids_03(self):
        """
        [Form Test] - TC14
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product_without_sale_apply
            f.partner_id = self.partner
            f.type = 'customer'
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)
            
    def test_compute_warranty_claim_policy_ids_04(self):
        """
        [Form Test] - TC15
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product
            f.partner_id = self.partner
            f.type = 'vendor'
            self.assertTrue(self._compare_warranty_claim_policies(f.warranty_claim_policy_ids, 'purchase', f.product_id))
    
    def test_compute_warranty_claim_policy_ids_05(self):
        """
        [Form Test] - TC16
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product_without_sale_apply
            f.partner_id = self.partner
            f.type = 'customer'
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)
            
    def test_compute_warranty_claim_policy_ids_06(self):
        """
        [Form Test] - TC18
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product
            f.partner_id = self.partner
            f.type = 'customer'
            self.assertTrue(self._compare_warranty_claim_policies(f.warranty_claim_policy_ids, 'sale', f.product_id))
            f.type = 'vendor'
            self.assertTrue(self._compare_warranty_claim_policies(f.warranty_claim_policy_ids, 'purchase', f.product_id))
            
    def test_compute_warranty_claim_policy_ids_07(self):
        """
        [Form Test] - TC19
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product
            f.partner_id = self.partner
            f.type = 'vendor'
            self.assertTrue(self._compare_warranty_claim_policies(f.warranty_claim_policy_ids, 'purchase', f.product_id))
            f.type = 'customer'
            self.assertTrue(self._compare_warranty_claim_policies(f.warranty_claim_policy_ids, 'sale', f.product_id))
            
    def test_compute_warranty_expiration_date_01(self):
        """
        [Form Test] - TC17
        """
        with Form(self.env['warranty.claim']) as f:
            f.product_id = self.product
            f.partner_id = self.partner
            f.type = 'customer'
            f.warranty_start_date = fields.Date.from_string('2021-08-20')
            self.assertEqual(f.warranty_expiration_date, fields.Date.from_string('2022-08-20'))
            
    def test_check_constrains_milestone_01(self):
        """
        [Functional Test] - TC09
        """
        with self.assertRaises(ValidationError):
            self.env['warranty.claim'].create({
                'name': 'Test Warranty Claim Invalid 1',
                'product_id': self.product.id,
                'partner_id': self.partner.id,
                'type': 'customer',
                'warranty_start_date': fields.Date.from_string('2021-08-20'),
                'warranty_claim_policy_ids': [(0, 0, {
                    'product_milestone_id': self.milestone_30_days.id,
                    'apply_to': 'sale',
                    'operation_start': 1.0,
                    'current_measurement': 1.0
                }), (0, 0, {
                    'product_milestone_id': self.milestone_15_days.id,
                    'apply_to': 'sale',
                    'operation_start': 1.0,
                    'current_measurement': 1.0
                })]
            })
            
    def test_check_constrains_milestone_02(self):
        """
        [Functional Test] - TC10
        """
        checked_warranty_claim = self.warranty_claim
        current_warranty_claim_policy_vals = []
        for policy in checked_warranty_claim.warranty_claim_policy_ids:
            current_warranty_claim_policy_vals.append((4, policy.id, 0))
        with self.assertRaises(ValidationError):
            current_warranty_claim_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_15_days.id,
                                                              'apply_to': 'sale',
                                                              'operation_start': 1.0,
                                                              'current_measurement': 1.0}))
            checked_warranty_claim.write({'warranty_claim_policy_ids': current_warranty_claim_policy_vals})
    
    def test_check_constrains_milestone_03(self):
        """
        [Functional Test] - TC11
        """
        self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Valid 1',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'type': 'customer',
            'warranty_start_date': fields.Date.from_string('2021-08-20'),
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'sale',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': self.milestone_1000_km.id,
                'apply_to': 'sale',
                'operation_start': 100,
                'current_measurement': 100
            })]
        })
        
    def test_check_constrains_milestone_04(self):
        """
        [Functional Test] - TC12
        """
        checked_warranty_claim = self.warranty_claim
        current_warranty_claim_policy_vals = []
        for policy in checked_warranty_claim.warranty_claim_policy_ids:
            current_warranty_claim_policy_vals.append((4, policy.id, 0))

        current_warranty_claim_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_100_lit.id,
                                                          'apply_to': 'sale',
                                                          'operation_start': 1.0,
                                                          'current_measurement': 1.0}))
        checked_warranty_claim.write({'warranty_claim_policy_ids': current_warranty_claim_policy_vals})
        
    def test_check_constrains_milestone_05(self):
        """
        [Functional Test] - TC13
        """
        with self.assertRaises(ValidationError):
            self.env['warranty.claim'].create({
                'name': 'Test Warranty Claim Invalid 2',
                'product_id': self.product.id,
                'partner_id': self.partner.id,
                'type': 'vendor',
                'warranty_start_date': fields.Date.from_string('2021-08-20'),
                'warranty_claim_policy_ids': [(0, 0, {
                    'product_milestone_id': self.milestone_30_days.id,
                    'apply_to': 'purchase',
                    'operation_start': 1.0,
                    'current_measurement': 1.0
                }), (0, 0, {
                    'product_milestone_id': self.milestone_15_days.id,
                    'apply_to': 'purchase',
                    'operation_start': 1.0,
                    'current_measurement': 1.0
                })]
            })
            
    def test_check_constrains_milestone_06(self):
        """
        [Functional Test] - TC14
        """
        checked_warranty_claim = self.warranty_claim
        current_warranty_claim_policy_vals = []
        for policy in checked_warranty_claim.warranty_claim_policy_ids:
            current_warranty_claim_policy_vals.append((4, policy.id, 0))
        with self.assertRaises(ValidationError):
            current_warranty_claim_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_30_days.id,
                                                              'apply_to': 'purchase',
                                                              'operation_start': 1.0,
                                                              'current_measurement': 1.0}))
            checked_warranty_claim.write({'warranty_claim_policy_ids': current_warranty_claim_policy_vals})
    
    def test_check_constrains_milestone_07(self):
        """
        [Functional Test] - TC15
        """
        self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Valid 2',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'type': 'vendor',
            'warranty_start_date': fields.Date.from_string('2021-08-20'),
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'purchase',
                'operation_start': 1.0,
                'current_measurement': 1.0
            }), (0, 0, {
                'product_milestone_id': self.milestone_1000_km.id,
                'apply_to': 'purchase',
                'operation_start': 100,
                'current_measurement': 100
            })]
        })
        
    def test_check_constrains_milestone_08(self):
        """
        [Functional Test] - TC16
        """
        checked_warranty_claim = self.warranty_claim
        current_warranty_claim_policy_vals = []
        for policy in checked_warranty_claim.warranty_claim_policy_ids:
            current_warranty_claim_policy_vals.append((4, policy.id, 0))

        current_warranty_claim_policy_vals.append((0, 0, {'product_milestone_id': self.milestone_100_lit.id,
                                                          'apply_to': 'purchase',
                                                          'operation_start': 1.0,
                                                          'current_measurement': 1.0}))
        checked_warranty_claim.write({'warranty_claim_policy_ids': current_warranty_claim_policy_vals})
        
    def test_action_confirm_01(self):
        """
        [Functional Test] - TC26
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Without Start Date',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'type': 'vendor',
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'purchase',
                'operation_start': 1.0,
                'current_measurement': 1.0
            })]
        })
        checked_warranty_claim.action_investigation()
        with self.assertRaises(UserError):
            checked_warranty_claim.action_confirm()
    
    def test_action_confirm_02(self):
        """
        [Functional Test] - TC18
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim With Normal Data',
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
        checked_warranty_claim.action_investigation()
        checked_warranty_claim.action_confirm()
        self.assertTrue(checked_warranty_claim.state == 'confirmed')
        
    def test_action_confirm_03(self):
        """
        [Functional Test] - TC19
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Without Not OK Policy',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'warranty_start_date': fields.Date.from_string('2021-08-20'),
            'date_claim': fields.Date.from_string('2021-08-20'),
            'type': 'vendor',
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'purchase',
                'operation_start': 2.0,
                'current_measurement': 35.0
            })]
        })
        checked_warranty_claim.action_investigation()
        result = checked_warranty_claim.action_confirm()
        
        view = self.env.ref('to_warranty_management.action_confirm_wizard_form_view')
        ctx = dict(checked_warranty_claim._context or {})
        ctx.update({'default_warranty_claim_id': checked_warranty_claim.id})
        expected_result = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'action.confirm.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }
        self.assertTrue(result == expected_result)
        self.assertTrue(checked_warranty_claim.state == 'investigation')
        
    def test_action_confirm_04(self):
        """
        [Functional Test] - TC20
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim With Expired Date Less Than Date Claim',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'warranty_start_date': fields.Date.from_string('2021-08-20'),
            'date_claim': fields.Date.from_string('2022-08-21'),
            'type': 'vendor',
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'purchase',
                'operation_start': 2.0,
                'current_measurement': 5.0
            })]
        })
        checked_warranty_claim.action_investigation()
        result = checked_warranty_claim.action_confirm()
        
        view = self.env.ref('to_warranty_management.action_confirm_wizard_form_view')
        ctx = dict(checked_warranty_claim._context or {})
        ctx.update({'default_warranty_claim_id': checked_warranty_claim.id})
        expected_result = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'action.confirm.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': ctx,
        }
        self.assertTrue(result == expected_result)
        self.assertTrue(checked_warranty_claim.state == 'investigation')
        
    def test_action_confirm_05(self):
        """
        [Functional Test] - TC21
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Without Not OK Policy',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'warranty_start_date': fields.Date.from_string('2021-08-20'),
            'date_claim': fields.Date.from_string('2021-08-20'),
            'type': 'vendor',
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'purchase',
                'operation_start': 2.0,
                'current_measurement': 35.0
            })]
        })
        checked_warranty_claim.action_investigation()
        checked_warranty_claim.with_context(call_from_wizard=True).action_confirm()
        self.assertTrue(checked_warranty_claim.state == 'confirmed')
        
    def test_action_confirm_06(self):
        """
        [Functional Test] - TC22
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim With Expired Date Less Than Date Claim',
            'product_id': self.product.id,
            'partner_id': self.partner.id,
            'warranty_start_date': fields.Date.from_string('2021-08-20'),
            'date_claim': fields.Date.from_string('2022-08-21'),
            'type': 'vendor',
            'warranty_claim_policy_ids':[(0, 0, {
                'product_milestone_id': self.milestone_30_days.id,
                'apply_to': 'purchase',
                'operation_start': 2.0,
                'current_measurement': 5.0
            })]
        })
        checked_warranty_claim.action_investigation()
        checked_warranty_claim.with_context(call_from_wizard=True).action_confirm()
        self.assertTrue(checked_warranty_claim.state == 'confirmed')
        
    def _compare_copied_warranty_claim(self, warranty_claim, copied_warranty_claim):
        self.assertTrue(warranty_claim.product_id == copied_warranty_claim.product_id)
        self.assertTrue(warranty_claim.partner_id == copied_warranty_claim.partner_id)
        self.assertTrue(warranty_claim.date_claim == copied_warranty_claim.date_claim)
        self.assertTrue(warranty_claim.type == copied_warranty_claim.type)
        set_claim_policies = set()
        set_copied_claim_policies = set()
        for policy in warranty_claim.warranty_claim_policy_ids:
            set_claim_policies.add((policy.product_milestone_id.id, policy.apply_to, policy.operation_start, policy.current_measurement))
        for policy in copied_warranty_claim.warranty_claim_policy_ids:
            set_copied_claim_policies.add((policy.product_milestone_id.id, policy.apply_to, policy.operation_start, policy.current_measurement))
        return set_claim_policies == set_copied_claim_policies
        
    def test_copy_01(self):
        """
        [Functional Test] - TC23
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Test Copy',
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
        copied_warranty_claim = checked_warranty_claim.copy()
        self.assertTrue(self._compare_copied_warranty_claim(checked_warranty_claim, copied_warranty_claim))
        
    def test_unlink_01(self):
        """
        [Functional Test] - TC24
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Test Unlink',
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
        checked_warranty_claim.unlink()
        
    def test_unlink_02(self):
        """
        [Functional Test] - TC24
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Test Unlink',
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
        checked_warranty_claim.action_investigation()
        checked_warranty_claim.action_cancelled()
        checked_warranty_claim.unlink()
        
    def test_unlink_03(self):
        """
        [Functional Test] - TC25
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Test Unlink',
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
        checked_warranty_claim.action_investigation()
        checked_warranty_claim.action_disclaimed()
        with self.assertRaises(UserError):
            checked_warranty_claim.unlink()
            
    def test_unlink_04(self):
        """
        [Functional Test] - TC25
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Test Unlink',
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
        checked_warranty_claim.action_investigation()
        checked_warranty_claim.action_confirm()
        with self.assertRaises(UserError):
            checked_warranty_claim.unlink()
    
    def test_unlink_05(self):
        """
        [Functional Test] - TC25
        """
        checked_warranty_claim = self.env['warranty.claim'].create({
            'name': 'Test Warranty Claim Test Unlink',
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
        checked_warranty_claim.action_investigation()
        checked_warranty_claim.action_confirm()
        checked_warranty_claim.action_done()
        with self.assertRaises(UserError):
            checked_warranty_claim.unlink()
