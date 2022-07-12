from odoo import fields
from odoo.tests import Form, tagged

from .common import TestCommon

@tagged('post_install', '-at_install')
class TestRepair(TestCommon):

    def test_onchange_warranty_claim_id_01(self):
        """
        [Form Test] - TC01
        - Case: Change warranty claim of repair order, in which new warranty claim has product, lot, partner and warranty expiration information
        - Expected Result:
            + product, lot, partner, warranty expiration of repair will be updated based on warranty claim
            + product uom of repair will be set based uom of product
        """

        with Form(self.env['repair.order']) as f:
            f.warranty_claim_id = self.warranty_claim1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product1)
            self.assertTrue(f.partner_id == self.partner_a)
            self.assertTrue(f.product_uom == self.product1.uom_id)
            self.assertEqual(f.guarantee_limit, fields.Date.from_string('2022-09-06'))
            f.warranty_claim_id = self.warranty_claim2
            self.assertTrue(f.lot_id == self.lot2)
            self.assertTrue(f.product_id == self.product2)
            self.assertTrue(f.partner_id == self.partner_b)
            self.assertTrue(f.product_uom == self.product2.uom_id)
            self.assertEqual(f.guarantee_limit, fields.Date.from_string('2023-09-06'))

    def test_onchange_warranty_claim_id_02(self):
        """
        [Form Test] - TC02
        - Case: Unselect warranty claim of repair order, in which new warranty claim has product, lot, partner and warranty expiration information
        - Expected Result:
            + product, product uom, lot, partner, warranty expiration of repair will be kept
        """

        with Form(self.env['repair.order']) as f:
            f.warranty_claim_id = self.warranty_claim1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product1)
            self.assertTrue(f.partner_id == self.partner_a)
            self.assertTrue(f.product_uom == self.product1.uom_id)
            self.assertEqual(f.guarantee_limit, fields.Date.from_string('2022-09-06'))
            f.warranty_claim_id = self.env['warranty.claim']
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product1)
            self.assertTrue(f.partner_id == self.partner_a)
            self.assertTrue(f.product_uom == self.product1.uom_id)
            self.assertEqual(f.guarantee_limit, fields.Date.from_string('2022-09-06'))

    def test_onchange_warranty_claim_id_03(self):
        """
        [Form Test] - TC03
        - Case: Change warranty claim of repair order, in which new warranty claim doesn't has lot and warranty expiration information
        - Expected Result:
            + product, partner of repair will be updated based on warranty claim
            + product uom of repair will be set based uom of product
            + lot and warranty expiration of repair will be reset
        """

        with Form(self.env['repair.order']) as f:
            f.warranty_claim_id = self.warranty_claim1
            self.assertTrue(f.lot_id == self.lot1)
            self.assertTrue(f.product_id == self.product1)
            self.assertTrue(f.partner_id == self.partner_a)
            self.assertTrue(f.product_uom == self.product1.uom_id)
            self.assertEqual(f.guarantee_limit, fields.Date.from_string('2022-09-06'))
            f.warranty_claim_id = self.warranty_claim3
            self.assertTrue(not f.lot_id)
            self.assertTrue(f.product_id == self.product2)
            self.assertTrue(f.product_uom == self.product2.uom_id)
            self.assertFalse(f.partner_id)
            self.assertTrue(not f.guarantee_limit)
            # Because lot_id is required if selected product is tracking by lot/serial, so we need to select lot for this repair
            f.lot_id = self.lot2

    def test_onchange_warranty_claim_id_04(self):
        """
        [Form Test] - TC04
        - Case: Unselect warranty claim of repair order when editing a repair:
            + in which new warranty claim has product, lot, partner and warranty expiration information
        - Expected Result:
            + product, product uom, lot, partner, warranty expiration of repair will be kept as original value before editing
        """

        with Form(self.repair) as f:
            f.lot_id = self.lot1
            f.product_id = self.product1
            f.partner_id = self.partner_a
            f.guarantee_limit = fields.Date.from_string('2023-09-07')
            f.warranty_claim_id = self.env['warranty.claim']
            self.assertTrue(f.lot_id == self.lot2)
            self.assertTrue(f.product_id == self.product2)
            self.assertTrue(f.product_uom == self.product2.uom_id)
            self.assertTrue(f.partner_id == self.partner_b)
            self.assertTrue(not f.guarantee_limit)
