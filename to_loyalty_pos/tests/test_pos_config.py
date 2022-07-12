from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from odoo.addons.to_loyalty.tests.common import LoyaltyCommon


@tagged('post_install', '-at_install')
class TestLoyaltyPos(LoyaltyCommon):
    def test_01_setting_pos_config(self):
        """Shop and loyalty program need the same currency"""
        pos_config = self.env.ref('point_of_sale.pos_config_main')
        program_vnd = self.env['loyalty.program'].create({
            'name': 'program_vnd',
            'pp_currency': 0.000001,
            'pp_product': 5,
            'pp_order': 3,
            'currency_id': self.currency_vnd.id,
        })
        pos_config.write({'loyalty_id': self.loyalty_program_1.id})
        self.assertRaises(ValidationError, pos_config.write, {'loyalty_id': program_vnd.id})

    def test_02_change_currency_loyalty_program(self):
        """Shop and loyalty program need the same currency"""
        pos_config = self.env.ref('point_of_sale.pos_config_main')
        pos_config.write({'loyalty_id': self.loyalty_program_1.id})
        self.assertRaises(ValidationError, self.loyalty_program_1.write, {'currency_id': self.currency_vnd.id})
