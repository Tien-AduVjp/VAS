from odoo import fields
from odoo.tests.common import Form, tagged

from .test_base import TestBase

@tagged('post_install', '-at_install')
class TestProductionLotWarrantyClaimPolicy(TestBase):
    
    def test_compute_warranty_expiration_date_01(self):
        """
        [Form Test] - TC04
        """
        with Form(self.lot1) as f:
            f.warranty_start_date = fields.Date.from_string('2021-08-23')
            self.assertEqual(f.warranty_expiration_date, fields.Date.from_string('2022-08-23'))
            
    def test_compute_warranty_expiration_date_02(self):
        """
        [Form Test] - TC05
        """
        with Form(self.lot1) as f:
            f.warranty_start_date = fields.Date.from_string('2021-08-23')
            self.assertEqual(f.warranty_expiration_date, fields.Date.from_string('2022-08-23'))
            f.warranty_period = 15
            self.assertEqual(f.warranty_expiration_date, fields.Date.from_string('2022-11-23'))
            
    def test_compute_warranty_expiration_date_03(self):
        """
        [Form Test] - TC06
        """
        with Form(self.lot1) as f:
            f.warranty_start_date = fields.Date.from_string('2021-08-23')
            self.assertEqual(f.warranty_expiration_date, fields.Date.from_string('2022-08-23'))
            f.warranty_start_date = False
            self.assertEqual(f.warranty_expiration_date, False)
    
    def test_compute_warranty_expiration_date_04(self):
        """
        [Form Test] - TC07
        """
        with Form(self.lot1) as f:
            f.warranty_start_date = fields.Date.from_string('2021-08-23')
            self.assertEqual(f.warranty_expiration_date, fields.Date.from_string('2022-08-23'))
            f.warranty_period = False
            self.assertEqual(f.warranty_expiration_date, False)
            
    def test_compute_supplier_warranty_expiration_date_01(self):
        """
        [Form Test] - TC08
        """
        with Form(self.lot1) as f:
            f.supplier_warranty_start_date = fields.Date.from_string('2021-08-23')
            self.assertEqual(f.supplier_warranty_expiration_date, fields.Date.from_string('2022-08-23'))
            
    def test_compute_supplier_warranty_expiration_date_02(self):
        """
        [Form Test] - TC09
        """
        with Form(self.lot1) as f:
            f.supplier_warranty_start_date = fields.Date.from_string('2021-08-23')
            self.assertEqual(f.supplier_warranty_expiration_date, fields.Date.from_string('2022-08-23'))
            f.warranty_period = 15
            self.assertEqual(f.supplier_warranty_expiration_date, fields.Date.from_string('2022-11-23'))
            
    def test_compute_supplier_warranty_expiration_date_03(self):
        """
        [Form Test] - TC10
        """
        with Form(self.lot1) as f:
            f.supplier_warranty_start_date = fields.Date.from_string('2021-08-23')
            self.assertEqual(f.supplier_warranty_expiration_date, fields.Date.from_string('2022-08-23'))
            f.supplier_warranty_start_date = False
            self.assertEqual(f.supplier_warranty_expiration_date, False)
    
    def test_compute_supplier_warranty_expiration_date_04(self):
        """
        [Form Test] - TC11
        """
        with Form(self.lot1) as f:
            f.supplier_warranty_start_date = fields.Date.from_string('2021-08-23')
            self.assertEqual(f.supplier_warranty_expiration_date, fields.Date.from_string('2022-08-23'))
            f.warranty_period = False
            self.assertEqual(f.supplier_warranty_expiration_date, False)
            
    def _compare_warranty_policies_for_lot_and_product(self, lot, product):
        claim_policy_for_lot = lot.warranty_claim_policy_ids
        policy_for_product = product.warranty_policy_ids
        if len(claim_policy_for_lot) == len(policy_for_product):
            set_claim_policy_for_lot = set()
            set_policy_for_product = set()
            for claim_policy in claim_policy_for_lot:
                set_claim_policy_for_lot.add((claim_policy.product_milestone_id.id, claim_policy.apply_to))
            for policy in policy_for_product:
                set_policy_for_product.add((policy.product_milestone_id.id, policy.apply_to))
            return set_claim_policy_for_lot == set_policy_for_product
        else:
            return False
        
    def test_stock_move_line_01(self):
        """
        [Functional Test] - TC01
        """
        lot1 = self.env['stock.production.lot'].create({
            'name': 'lot1',
            'product_id': self.product_lot1.id,
            'company_id': self.env.company.id,
        })
        picking = self.env['stock.picking'].create({
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'partner_id': self.partner.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
        })
        
        move = self.env['stock.move'].create({
            'name': 'Test Stock Move',
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'picking_id': picking.id,
            'product_id': self.product_lot1.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': 1.0,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
        })
        picking.action_confirm()
        picking.action_assign()
        # receive lot1
        move.move_line_ids.lot_id = lot1
        move.move_line_ids.qty_done = 1
        picking.action_done()
        
        self.assertTrue(self._compare_warranty_policies_for_lot_and_product(lot1, self.product_lot1))
        self.assertTrue(lot1.warranty_period == self.product_lot1.warranty_period)
