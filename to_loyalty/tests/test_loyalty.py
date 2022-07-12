from psycopg2 import IntegrityError

from odoo import tools, exceptions
from odoo.tests.common import tagged
from .common import LoyaltyCommon


@tagged('post_install', '-at_install')
class TestLoyalty(LoyaltyCommon):
    @classmethod
    def setUpClass(cls):
        super(TestLoyalty, cls).setUpClass()
        cls.setup_sale_team()
        cls.setup_given_points()
        cls.setup_spent_points()

    def test_01_rounding_program(self):
        self.env['loyalty.program'].create(self._vals_loyalty_program_change_rounding(0.000001))
        with tools.mute_logger('odoo.sql_db'):
            self.assertRaises(IntegrityError,
                              self.env['loyalty.program'].create,
                              self._vals_loyalty_program_change_rounding(0))

    def test_01_01_rounding_program(self):
        with tools.mute_logger('odoo.sql_db'):
            self.assertRaises(IntegrityError,
                              self.env['loyalty.program'].create,
                              self._vals_loyalty_program_change_rounding(-0.0001))

    def test_02_create_customer_level(self):
        with tools.mute_logger('odoo.sql_db'):
            with self.assertRaises(IntegrityError):
                self._create_loyalty_customer_level('level_1', 150000)

    def test_02_01_create_customer_level(self):
        with tools.mute_logger('odoo.sql_db'):
            with self.assertRaises(IntegrityError):
                self._create_loyalty_customer_level('level_1_1', 15)

    def test_03_loyalty_points_of_customer(self):
        self.assertEqual(self.partner_1.loyalty_points, 10, "to_loyalty: Wrong points of parnter_1")
        self.assertEqual(self.partner_2.loyalty_points, 85, "to_loyalty: Wrong points of parnter_2")
        self.assertEqual(self.partner_3.loyalty_points, 30, "to_loyalty: Wrong points of parnter_3")

    def test_04_loyalty_level_of_customer(self):
        self.assertEqual(self.partner_1.level_id.id, False, "to_loyalty: Wrong level of parnter_1")
        self.assertEqual(self.partner_2.level_id.id, self.customer_level_2.id, "to_loyalty: Wrong level of parnter_2")
        self.assertEqual(self.partner_3.level_id.id, self.customer_level_1.id, "to_loyalty: Wrong level of parnter_3")

    def test_05_loyalty_level_count_partner(self):
        self.assertEqual(self.customer_level_1.partner_ids_count, 1, "to_loyalty: Wrong count partnet on customer level")
        self.assertEqual(self.customer_level_2.partner_ids_count, 1, "to_loyalty: Wrong count partnet on customer level")

    def test_1010_check_manual_adjustment_vs_product(self):
        with tools.mute_logger('odoo.sql_db'):
            with self.assertRaises(exceptions.ValidationError):
                self._create_loyalty_point_given(
                    product=self.product_1,
                    product_qty=1,
                    points=10,
                    partner=self.partner_1,
                    program=self.loyalty_program_1,
                    manual_adjustment=True,
                )

    def test_1020_check_check_gift_product(self):
        with self.assertRaises(exceptions.ValidationError):
            self.loyalty_program_1.reward_ids[0].gift_product_id = False

    def test_1030_check_discount_product(self):
        with self.assertRaises(exceptions.ValidationError):
            self.loyalty_program_1.reward_ids[1].discount_product_id = False

    def test_1040_loyalty_point_of_team(self):
        self.assertEqual(self.team_1.loyalty_points_given, 10, "to_loyalty: Wrong loyalty points given")
        self.assertEqual(self.team_1.loyalty_points_spent, -25, "to_loyalty: Wrong loyalty points spent")
        self.assertEqual(self.team_2.loyalty_points_given, 110, "to_loyalty: Wrong loyalty points given")
        self.assertEqual(self.team_2.loyalty_points_spent, 0, "to_loyalty: Wrong loyalty points spent")

    def _vals_loyalty_program_change_rounding(self, rounding):
        return {
            'name': 'loyalty_program_rounding',
            'pp_currency': 1,
            'pp_product': 1,
            'pp_order': 1,
            'currency_id': self.currency_usd.id,
            'rounding': rounding
        }
