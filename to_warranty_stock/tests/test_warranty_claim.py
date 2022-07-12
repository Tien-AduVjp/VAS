from odoo import fields
from odoo.tests.common import Form, tagged
from odoo.exceptions import ValidationError

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestWarrantyClaim(TestBase):
    
    def _compare_warranty_claim_policies_for_lot(self, form_warranty_claim_policies, apply_to, lot):
        policies = lot.warranty_claim_policy_ids.filtered(lambda wp: wp.apply_to == apply_to)
        if len(form_warranty_claim_policies) == len(policies):
            set_form_policies = set()
            set_policies = set()
            for idx in range(len(form_warranty_claim_policies)):
                line = form_warranty_claim_policies.edit(idx)
                set_form_policies.add((line.product_milestone_id.id, line.apply_to, line.operation_start))
            for policy in policies:
                set_policies.add((policy.product_milestone_id.id, policy.apply_to, policy.operation_start))
            return set_form_policies == set_policies
        else:
            return False

    def test_compute_warranty_claim_policy_ids_01(self):
        """
        [Form Test] - TC12
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            f.lot_id = self.lot1
            f.partner_id = self.partner
            self.assertTrue(f.product_id == self.product_lot1)
            self.assertTrue(f.warranty_start_date == self.lot1.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot1.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot1.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_lot(f.warranty_claim_policy_ids, 'sale', f.lot_id))
    
    def test_compute_warranty_claim_policy_ids_02(self):
        """
        [Form Test] - TC13
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.lot_id = self.lot1
            f.partner_id = self.partner
            self.assertTrue(f.product_id == self.product_lot1)
            self.assertTrue(f.warranty_start_date == self.lot1.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot1.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot1.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_lot(f.warranty_claim_policy_ids, 'purchase', f.lot_id))
            
    def test_compute_warranty_claim_policy_ids_03(self):
        """
        [Form Test] - TC14
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.lot_id = self.lot1
            f.partner_id = self.partner
            self.assertTrue(f.product_id == self.product_lot1)
            self.assertTrue(f.warranty_start_date == self.lot1.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot1.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot1.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_lot(f.warranty_claim_policy_ids, 'purchase', f.lot_id))
            f.type = 'customer'
            self.assertTrue(self._compare_warranty_claim_policies_for_lot(f.warranty_claim_policy_ids, 'sale', f.lot_id))
            
    def test_compute_warranty_claim_policy_ids_04(self):
        """
        [Form Test] - TC15
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'vendor'
            f.lot_id = self.lot_without_sale
            f.partner_id = self.partner
            self.assertTrue(f.product_id == self.product_lot1)
            self.assertTrue(f.warranty_start_date == self.lot_without_sale.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot_without_sale.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot_without_sale.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_lot(f.warranty_claim_policy_ids, 'purchase', f.lot_id))
            f.type = 'customer'
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)  
            
    def test_compute_warranty_claim_policy_ids_05(self):
        """
        [Form Test] - TC16
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            f.lot_id = self.lot1
            f.partner_id = self.partner
            self.assertTrue(f.product_id == self.product_lot1)
            self.assertTrue(f.warranty_start_date == self.lot1.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot1.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot1.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_lot(f.warranty_claim_policy_ids, 'sale', f.lot_id))
            f.type = 'vendor'
            self.assertTrue(self._compare_warranty_claim_policies_for_lot(f.warranty_claim_policy_ids, 'purchase', f.lot_id)) 
            
    def test_compute_warranty_claim_policy_ids_06(self):
        """
        [Form Test] - TC17
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            f.lot_id = self.lot_without_purchase
            f.partner_id = self.partner
            self.assertTrue(f.product_id == self.product_lot1)
            self.assertTrue(f.warranty_start_date == self.lot_without_purchase.warranty_start_date)
            self.assertTrue(f.warranty_period == self.lot_without_purchase.warranty_period)
            self.assertTrue(f.warranty_expiration_date == self.lot_without_purchase.warranty_expiration_date)
            self.assertTrue(self._compare_warranty_claim_policies_for_lot(f.warranty_claim_policy_ids, 'sale', f.lot_id))
            f.type = 'vendor'
            self.assertTrue(len(f.warranty_claim_policy_ids) == 0)
            
    def test_compute_warranty_start_date_01(self):
        """
        [Form Test] - TC21
        """
        f = Form(self.env['warranty.claim'])
        f.type = 'customer'
        f.lot_id = self.lot1
        f.partner_id = self.partner
        self.assertTrue(f.warranty_start_date == self.lot1.warranty_start_date)
        warranty_claim = f.save()
        self.lot1.warranty_start_date = fields.Date.from_string('2021-08-25')
        self.assertTrue(warranty_claim.warranty_start_date == fields.Date.from_string('2021-08-25'))
        self.assertTrue(self.lot1.warranty_expiration_date == fields.Date.from_string('2022-08-25'))
        self.assertTrue(warranty_claim.warranty_expiration_date == fields.Date.from_string('2022-08-25'))
    
    def test_compute_warranty_period_01(self):
        """
        [Form Test] - TC22
        """
        f = Form(self.env['warranty.claim'])
        f.type = 'customer'
        f.lot_id = self.lot1
        f.partner_id = self.partner
        self.assertTrue(f.warranty_period == self.lot1.warranty_period)
        warranty_claim = f.save()
        self.lot1.warranty_period = 15
        self.assertTrue(warranty_claim.warranty_period == 15)
        self.assertTrue(self.lot1.warranty_expiration_date == fields.Date.from_string('2022-11-20'))
        self.assertTrue(warranty_claim.warranty_expiration_date == fields.Date.from_string('2022-11-20'))
        
    def test_compute_warranty_expiration_date_01(self):
        """
        [Form Test] - TC23
        """
        with Form(self.env['warranty.claim']) as f:
            f.type = 'customer'
            f.lot_id = self.lot1
            f.partner_id = self.partner
            self.assertTrue(f.warranty_expiration_date == self.lot1.warranty_expiration_date)
            f.warranty_start_date = fields.Date.from_string('2021-08-30')
            self.assertTrue(f.warranty_expiration_date == self.lot1.warranty_expiration_date)
        
    def test_update_warranty_info_of_lot_01(self):
        """
        [Form Test] - TC24
        """
        f = Form(self.env['warranty.claim'])
        f.type = 'customer'
        f.lot_id = self.lot1
        f.partner_id = self.partner
        self.assertTrue(f.warranty_period == self.lot1.warranty_period)
        warranty_claim = f.save()
        warranty_claim.action_investigation()
        with self.assertRaises(ValidationError):
            self.lot1.warranty_period = 15
        
    def test_update_warranty_info_of_lot_02(self):
        """
        [Form Test] - TC25
        """
        f = Form(self.env['warranty.claim'])
        f.type = 'customer'
        f.lot_id = self.lot1
        f.partner_id = self.partner
        self.assertTrue(f.warranty_period == self.lot1.warranty_period)
        warranty_claim = f.save()
        warranty_claim.action_investigation()
        with self.assertRaises(ValidationError):
            self.lot1.warranty_start_date = fields.Date.from_string('2021-08-30')
            
    def test_check_constrains_product_and_lot_01(self):
        """
        [Functional Test] - TC02
        """
        with self.assertRaises(ValidationError):
            self.env['warranty.claim'].create({
                'name': 'Test Warranty Claim Invalid 1',
                'lot_id': self.lot1.id,
                'product_id': self.product_serial1.id,
                'partner_id': self.partner.id,
                'type': 'customer',
                'warranty_start_date': fields.Date.from_string('2021-08-20'),
                'warranty_claim_policy_ids': [(0, 0, {
                    'product_milestone_id': self.milestone_30_days.id,
                    'apply_to': 'sale',
                    'operation_start': 1.0,
                    'current_measurement': 1.0
                })]
            })

    def test_action_confirm_01(self):
        """
        [Functional Test] - TC03
        """
        f = Form(self.env['warranty.claim'])
        f.type = 'customer'
        f.lot_id = self.lot_without_expiration_date
        f.partner_id = self.partner
        warranty_claim = f.save()
        warranty_claim.action_investigation()
        with self.assertRaises(ValidationError):
            warranty_claim.action_confirm()
            
    def test_action_confirm_02(self):
        """
        [Functional Test] - TC04
        """
        f = Form(self.env['warranty.claim'])
        f.type = 'customer'
        f.lot_id = self.lot1
        f.partner_id = self.partner
        warranty_claim = f.save()
        warranty_claim.action_investigation()
        warranty_claim.action_confirm()
        self.assertTrue(warranty_claim.state == 'confirmed')
