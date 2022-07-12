from odoo.tests import Form, tagged

from .test_base import TestBase


@tagged('post_install', '-at_install')
class TestRepair(TestBase):

    def test_onchange_location_id_01(self):
        """
        [Functional Test] - TC01
        
        - Case: Change lot of a repair in draft state in case this lot has customer information
        - Expected Result: Partner of repair will be set based on customer on lot
        """
        with Form(self.repair) as f:
            f.lot_id = self.lot1
            self.assertTrue(f.partner_id == self.partner_a)
            f.lot_id = self.lot2
            self.assertTrue(f.partner_id == self.partner_b)
    
    def test_onchange_location_id_02(self):
        """
        [Functional Test] - TC02
        
        - Case: Change lot of a repair in confirmed state in case this lot has customer information
        - Expected Result: Partner of repair will not change
        """
        with Form(self.repair) as f:
            f.lot_id = self.lot1
            self.assertTrue(f.partner_id == self.partner_a)
        self.repair.action_validate()
        self.assertTrue(self.repair.state == 'confirmed')
        
        with Form(self.repair) as f:
            f.lot_id = self.lot2
            self.assertTrue(f.partner_id == self.partner_a)
