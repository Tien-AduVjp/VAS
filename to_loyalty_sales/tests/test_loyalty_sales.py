from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from odoo.addons.to_loyalty.tests.common import LoyaltyCommon
from odoo import fields

@tagged('post_install', '-at_install')
class TestLoyalTySale(LoyaltyCommon):
    @classmethod
    def setUpClass(cls):
        super(TestLoyalTySale, cls).setUpClass()
        cls.pricelist_vnd = cls.env['product.pricelist'].create({
            'name': 'pricelist_vnd',
            'currency_id': cls.currency_vnd.id,
        })
        cls.pricelist_usd = cls.env['product.pricelist'].create({
            'name': 'pricelist_usa',
            'currency_id': cls.currency_usd.id,
        })
        cls.env.ref('base.rateUSDbis').write({
            'name': fields.Date.to_date('%s-01-01'%fields.Date.today().year)
        })
        # loyalty_point_partner_1
        cls._create_loyalty_point_given(
            points=100,
            partner=cls.partner_1,
            program=cls.loyalty_program_1,
            manual_adjustment=True
        )
        # loyalty_point_partner_2
        cls._create_loyalty_point_given(
            points=5000000000000,
            partner=cls.partner_2,
            program=cls.loyalty_program_1,
            manual_adjustment=True
        )

    def test_1001_calculate_won_points(self):
        """No rules"""
        self.loyalty_program_1.rule_ids = False
        sale_order = self._create_sale_order(
            partner=self.partner_3,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        self.assertEqual(sale_order.order_line[0].loyalty_points, 10.0, "to_loyalty: Wrong calculate won points")
        self.assertEqual(sale_order.spendable_points, 0.0, "to_loyalty: Wrong calculate won points")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.spendable_points, 13.0, "to_loyalty: Wrong calculate won points")

    def test_1002_calculate_won_points(self):
        sale_order = self._create_sale_order(
            partner=self.partner_3,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        self.assertEqual(sale_order.order_line[0].loyalty_points, 10.0, "to_loyalty: Wrong calculate won points")
        self.assertEqual(sale_order.spendable_points, 0.0, "to_loyalty: Wrong calculate won points")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.spendable_points, 13.0, "to_loyalty: Wrong calculate won points")

    def test_1003_calculate_won_points(self):
        """Convert currency"""
        sale_order = self._create_sale_order(
            partner=self.partner_3,
            pricelist=self.pricelist_vnd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        self.assertEqual(sale_order.order_line[0].loyalty_points, 10.0, "to_loyalty: Wrong calculate won points")
        self.assertEqual(sale_order.spendable_points, 0.0, "to_loyalty: Wrong calculate won points")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.spendable_points, 13.0, "to_loyalty: Wrong calculate won points")

    def test_1004_calculate_won_points(self):
        """Convert units"""
        # Convert Dozens to Units, Dozens have id  = 2
        sale_order = self._create_sale_order(
            partner=self.partner_3,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0,
            product_uom=2
        )
        self.assertEqual(sale_order.order_line[0].loyalty_points, 120.0, "to_loyalty: Wrong calculate won points")
        self.assertEqual(sale_order.spendable_points, 0.0, "to_loyalty: Wrong calculate won points")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.spendable_points, 123.0, "to_loyalty: Wrong calculate won points")

    def test_1005_calculate_won_points(self):
        """All rules are matching, all that cumulative = True"""
        rule_3 = self.env['loyalty.rule'].create({
            'name': 'loyalty_rule_1',
            'rule_type': 'product',
            'product_id': self.product_1.product_variant_id.id,
            'cumulative': True,
            'pp_product': 8,
            'pp_currency': 0.000001
        })
        self.loyalty_program_1.rule_ids[0].cumulative = True
        self.loyalty_program_1.rule_ids += rule_3
        sale_order = self._create_sale_order(
            partner=self.partner_3,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        self.assertEqual(sale_order.order_line[0].loyalty_points, 33.0, "to_loyalty: Wrong calculate won points")
        self.assertEqual(sale_order.spendable_points, 0.0, "to_loyalty: Wrong calculate won points")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.spendable_points, 36.0, "to_loyalty: Wrong calculate won points")

    def test_1006_calculate_won_points(self):
        """All rules are matching, rule_1 not cumulative"""
        rule_3 = self.env['loyalty.rule'].create({
            'name': 'loyalty_rule_1',
            'rule_type': 'product',
            'product_id': self.product_1.product_variant_id.id,
            'cumulative': True,
            'pp_product': 8,
            'pp_currency': 0.000001
        })
        self.loyalty_program_1.rule_ids += rule_3
        sale_order = self._create_sale_order(
            partner=self.partner_3,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        self.assertEqual(sale_order.order_line[0].loyalty_points, 10.0, "to_loyalty: Wrong calculate won points")
        self.assertEqual(sale_order.spendable_points, 0.0, "to_loyalty: Wrong calculate won points")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.spendable_points, 13.0, "to_loyalty: Wrong calculate won points")

    def test_1007_calculate_won_points(self):
        """No mtach any rule"""
        product_new = self.env['product.product'].create({
            'name': 'product_new',
            'categ_id': self.product_category_1.id,
            'price': 5000000,
            'standard_price': 5000000,
        })
        sale_order = self._create_sale_order(
            partner=self.partner_3,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=product_new,
            product_uom_qty=1.0
        )
        self.assertEqual(sale_order.order_line[0].loyalty_points, 10.0, "to_loyalty: Wrong calculate won points")
        self.assertEqual(sale_order.spendable_points, 0.0, "to_loyalty: Wrong calculate won points")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.spendable_points, 13.0, "to_loyalty: Wrong calculate won points")

    def test_2001_calculate_spent_points(self):
        """partner_3's points small than all reward, reward_count = 0"""
        sale_order = self._create_sale_order(
            partner=self.partner_3,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        self.assertEqual(sale_order.reward_count, 0, "to_loyalty: Wrong calculate reward count")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.reward_count, 0, "to_loyalty: Wrong calculate reward count")

    def test_2002_calculate_spent_points(self):
        """ partner_1's points biger than mini points of reward_1, reward_count = 1
            after confirm partner_1's points biger than mini points of reward_2, reward_count = 2"""
        sale_order = self._create_sale_order(
            partner=self.partner_1,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        self.assertEqual(sale_order.reward_count, 1, "to_loyalty: Wrong calculate reward count")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.reward_count, 2, "to_loyalty: Wrong calculate reward count")

    def test_2003_calculate_spent_points(self):
        """If partner_1's point biger than mini points of reward_1, partner_1 can reward exchange"""
        sale_order = self._create_sale_order(
            partner=self.partner_1,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        reward_wizard = self.env['reward.wizard'].create({
            'sale_order_id': sale_order.id,
            'reward_id': self.loyalty_program_1.reward_ids[0].id
        })
        reward_wizard.action_choose()
        self.assertEqual(sale_order.order_line[1].loyalty_points, -20.0, "to_loyalty: Wrong calculate spent points")
        self.assertEqual(sale_order.spendable_points, 80.0, "to_loyalty: Wrong calculate spent points")
        sale_order.action_confirm()
        sale_order._compute_loyalty()
        self.assertEqual(sale_order.spendable_points, 93.0, "to_loyalty: Wrong calculate spent points")

    def test_2004_calculate_spent_points(self):
        """If partner_1's point smaller than mini points of reward_2, partner_1 can't reward exchange"""
        sale_order = self._create_sale_order(
            partner=self.partner_1,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        reward_wizard = self.env['reward.wizard'].create({
            'sale_order_id': sale_order.id,
            'reward_id': self.loyalty_program_1.reward_ids[1].id
        })
        with self.assertRaises(ValidationError):
            reward_wizard.action_choose()

    def test_2005_calculate_spent_points(self):
        """ Add 1 point for partner_1,
            partner_1 matching reward_1, reward_2,
            partner_1 reward exchange reward_1
            Now partner_1's points smaller than mini points of reward_2,
            So partner_1 can't reward exchange reward_2"""
        # add 1 point for partner_1
        self._create_loyalty_point_given(
            points=1,
            partner=self.partner_1,
            program=self.loyalty_program_1,
            manual_adjustment=True
        )
        sale_order = self._create_sale_order(
            partner=self.partner_1,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        reward_wizard_1 = self.env['reward.wizard'].create({
            'sale_order_id': sale_order.id,
            'reward_id': self.loyalty_program_1.reward_ids[0].id
        })
        reward_wizard_1.action_choose()
        reward_wizard = self.env['reward.wizard'].create({
            'sale_order_id': sale_order.id,
            'reward_id': self.loyalty_program_1.reward_ids[1].id
        })
        with self.assertRaises(ValidationError):
            reward_wizard.action_choose()

    def test_2006_calculate_spent_points(self):
        """Customer can't reward exchange of another program """
        sale_order = self._create_sale_order(
            partner=self.partner_1,
            pricelist=self.pricelist_usd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        another_reward = self.env['loyalty.reward'].create({
            'name': 'another_reward',
            'reward_type': 'gift',
            'gift_product_id': self.gift_1.id,
            'point_cost': 20,
            'minimum_points': 50,
        })
        reward_wizard = self.env['reward.wizard'].create({
            'sale_order_id': sale_order.id,
            'reward_id': another_reward.id
        })
        with self.assertRaises(ValidationError):
            reward_wizard.action_choose()

    def test_2007_calculate_spent_points(self):
        """Convert currency"""
        sale_order = self._create_sale_order(
            partner=self.partner_2,
            pricelist=self.pricelist_vnd,
            loyalty_program=self.loyalty_program_1,
            product=self.product_1,
            product_uom_qty=1.0
        )
        reward_wizard = self.env['reward.wizard'].create({
            'sale_order_id': sale_order.id,
            'reward_id': self.loyalty_program_1.reward_ids[1].id
        })
        reward_wizard.action_choose()
        sale_order.order_line[1].loyalty_points
        self.assertEqual(sale_order.order_line[1].loyalty_points, -15000000, "to_loyalty: Wrong calculate spent points")
        self.assertEqual(sale_order.order_line[1].price_subtotal, -7521747662.0, "to_loyalty: Wrong calculate spent points")

    def _create_sale_order(self, partner, pricelist, loyalty_program, product, product_uom_qty, product_uom=False):
        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'pricelist_id': pricelist.id,
            'loyalty_id': loyalty_program.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'name': product.name,
                'product_uom_qty': product_uom_qty,
                'tax_id': False,
                'product_uom': product_uom or product.uom_id.id,
            })]
        })
        return sale_order
