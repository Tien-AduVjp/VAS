from odoo.tests.common import SavepointCase
from odoo.exceptions import AccessError


class LoyaltyCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(LoyaltyCommon, cls).setUpClass()
        cls.currency_vnd = cls.env.ref('base.VND')
        cls.currency_usd = cls.env.ref('base.USD')
        cls.currency_vnd.rate_ids[0].write({
            'rate': 23000
        })
        cls.partner_1 = cls.env.ref('base.res_partner_1')
        cls.partner_2 = cls.env.ref('base.res_partner_2')
        cls.partner_3 = cls.env.ref('base.res_partner_3')

        cls.product_category_1 = cls.env.ref('product.product_category_1')
        cls.product_category_2 = cls.env.ref('product.product_category_2')

        cls.product_1 = cls.env.ref('product.product_delivery_01')
        cls.product_1.write({
            'categ_id': cls.product_category_1.id,
            'price': 5000000,
        })
        cls.product_2 = cls.env.ref('product.product_delivery_02')
        cls.product_2.write({
            'categ_id': cls.product_category_2.id,
            'price': 10000000,
        })
        cls.gift_1 = cls.env.ref('product.product_order_01')
        cls.gift_1.write({
            'price': 8000000,
        })

        cls.customer_level_1 = cls._create_loyalty_customer_level('level_1', 15)
        cls.customer_level_2 = cls._create_loyalty_customer_level('level_2', 40)

        cls.loyalty_program_1 = cls.env['loyalty.program'].create({
            'name': 'loyalty_program_1',
            'pp_currency': 0.000001,
            'pp_product': 5,
            'pp_order': 3,
            'currency_id': cls.currency_usd.id,
        })
        cls.loyalty_program_1.rule_ids += cls._create_loyalty_rule_product(
            cls.product_1,
            cls.loyalty_program_1.id
        )
        cls.loyalty_program_1.rule_ids += cls._create_loyalty_rule_product_category(
            cls.product_category_2,
            cls.loyalty_program_1.id
        )
        cls.loyalty_program_1.reward_ids += cls._create_loyalty_reward_gift(
            cls.gift_1,
            cls.loyalty_program_1.id
        )
        cls.loyalty_program_1.reward_ids += cls._create_loyalty_reward_discount(
            cls.product_1,
            cls.loyalty_program_1.id
        )

    @classmethod
    def setup_sale_team(cls):
        cls.user_1 = cls.env.ref('base.user_admin')
        cls.user_2 = cls.env.ref('base.user_demo')
        cls.user_3 = cls.env.ref('base.demo_user0')
        cls.loyalty_program_2 = cls.loyalty_program_1.copy()
        cls.loyalty_program_3 = cls.loyalty_program_2.copy()
        cls.team_1 = cls.env.ref('sales_team.team_sales_department')
        cls.team_2 = cls.env.ref('sales_team.salesteam_website_sales')

        cls.team_1.write({
            'member_ids': [(6, 0, [cls.user_1.id, cls.user_2.id])],
            'loyalty_id': cls.loyalty_program_1.id
        })
        cls.team_2.write({
            'member_ids': [(6, 0, [cls.user_3.id])],
            'loyalty_id': cls.loyalty_program_2.id
        })

        cls.loyalty_program_1.write({
            'team_ids': [(6, 0, [cls.team_1.id])]
        })
        cls.loyalty_program_2.write({
            'team_ids': [(6, 0, [cls.team_2.id])]
        })

    @classmethod
    def setup_given_points(cls):
        cls.loyalty_point_1 = cls._create_loyalty_point_given(
            product=cls.product_1,
            product_qty=1,
            points=10,
            partner=cls.partner_1,
            program=cls.loyalty_program_1,
            salesperson_id=cls.user_1.id,
            team_id=cls.team_1.id
        )
        cls.loyalty_point_2 = cls._create_loyalty_point_given(
            product=cls.product_2,
            product_qty=1,
            points=110,
            partner=cls.partner_2,
            program=cls.loyalty_program_2,
            salesperson_id=cls.user_3.id,
            team_id=cls.team_2.id
        )
        cls.loyalty_point_3 = cls._create_loyalty_point_given(
            product=cls.product_1,
            product_qty=3,
            points=30,
            partner=cls.partner_3,
            program=cls.loyalty_program_1,
        )

    @classmethod
    def setup_spent_points(cls):
        cls.env['loyalty.point'].create({
            'name': 'loyalty_point_reward_1',
            'partner_id': cls.partner_2.id,
            'loyalty_program_id': cls.loyalty_program_1.id,
            'points': -20,
            'reward_id': cls.loyalty_program_1.reward_ids[0].id,
            'product_id': cls.gift_1.id,
            'product_qty': 1,
            'price_total': 8000000,
            'salesperson_id': cls.user_1.id,
            'team_id': cls.team_1.id,
            'manual_adjustment': False,
        })

        cls.loyalty_point_reward_2 = cls.env['loyalty.point'].create({
            'name': 'loyalty_point_reward_1',
            'partner_id': cls.partner_2.id,
            'loyalty_program_id': cls.loyalty_program_1.id,
            'points': -5,
            'reward_id': cls.loyalty_program_1.reward_ids[1].id,
            'product_id': cls.product_1.id,
            'product_qty': 1,
            'price_total': 5,
            'salesperson_id': cls.user_1.id,
            'team_id': cls.team_1.id,
            'manual_adjustment': False,
        })

    @classmethod
    def _create_loyalty_customer_level(cls, level_name, min_point):
        return cls.env['customer.level'].create({
            'name': level_name,
            'points': min_point,
        })

    @classmethod
    def _create_loyalty_rule_product(cls, product, loyalty_program_id=False):
        return cls.env['loyalty.rule'].create({
            'name': 'loyalty_rule_1',
            'rule_type': 'product',
            'product_id': product.product_variant_id.id,
            'cumulative': False,
            'pp_product': 5,
            'pp_currency': 0.000001,
            'loyalty_program_id': loyalty_program_id,
        })

    @classmethod
    def _create_loyalty_rule_product_category(cls, product_category, loyalty_program_id=False):
        return cls.env['loyalty.rule'].create({
            'name': 'loyalty_rule_2',
            'rule_type': 'product_category',
            'product_category_id': product_category.id,
            'cumulative': False,
            'pp_product': 10,
            'pp_currency': 0.000010,
            'loyalty_program_id': loyalty_program_id,
        })

    @classmethod
    def _create_loyalty_reward_gift(cls, gift, loyalty_program_id=False):
        return cls.env['loyalty.reward'].create({
            'name': 'loyalty_reward_1',
                    'reward_type': 'gift',
                    'gift_product_id': gift.id,
                    'point_cost': 20,
                    'minimum_points': 50,
                    'loyalty_program_id': loyalty_program_id,
        })

    @classmethod
    def _create_loyalty_reward_discount(cls, product, loyalty_program_id=False):
        return cls.env['loyalty.reward'].create({
            'name': 'loyalty_reward_2',
            'reward_type': 'discount',
            'discount': 10.0,
            'discount_product_id': product.product_variant_id.id,
            'point_cost': 30,
            'minimum_points': 101,
            'loyalty_program_id': loyalty_program_id,
        })

    @classmethod
    def _create_loyalty_point_given(cls, points, partner, program, product=False, product_qty=1, salesperson_id=False, team_id=False, manual_adjustment=False):
        return cls.env['loyalty.point'].create({
            'name': 'loyalty_point_test',
            'partner_id': partner.id,
            'loyalty_program_id': program.id,
            'points': points,
            'product_id': product.id if product else False,
            'product_qty': product_qty,
            'price_total': product.lst_price * product_qty if product else 0,
            'manual_adjustment': manual_adjustment,
            'salesperson_id': salesperson_id,
            'team_id': team_id
        })

    def _can_read_document(self, user, document):
        document.with_user(user).read(['id'])

    def _can_not_read_document(self, user, document):
        self.assertRaises(AccessError, document.with_user(user).read, ['id'])

    def _can_write_document(self, user, document):
        document.with_user(user).write({'name': 'name_test'})

    def _can_not_write_document(self, user, document):
        self.assertRaises(AccessError, document.with_user(user).write, {'name': 'name_test'})

    def _can_unlink_document(self, user, document):
        document.with_user(user).unlink()

    def _can_not_unlink_document(self, user, document):
        self.assertRaises(AccessError, document.with_user(user).unlink)

    def _can_create_document(self, user, table, vals):
        table.with_user(user).create(vals)

    def _can_not_create_document(self, user, table, vals):
        self.assertRaises(AccessError, table.with_user(user).create, vals)

    def _loyalty_point_vals_new(self):
        return{
            'name': 'loyalty_point_test_new',
            'partner_id': self.partner_2.id,
            'loyalty_program_id': self.loyalty_program_1.id,
            'points': 10,
            'product_id': self.product_1.id,
            'product_qty': 1,
            'price_total': 5000000,
            'salesperson_id': self.user_3.id,
            'team_id': self.team_2.id,
            'manual_adjustment': False
        }

    def _loyalty_program_vals_new(self):
        return{'name': 'loyalty_program_new',
               'pp_currency': 0.000001,
               'pp_product': 5,
               'pp_order': 3,
               'currency_id': 23}

    def _loyalty_rule_vals_new(self):
        return {
            'name': 'loyalty_rule_new',
            'rule_type': 'product',
            'product_id': self.product_1.id,
            'cumulative': False,
            'pp_product': 5,
            'pp_currency': 0.000001}

    def _loyalty_reward_vals_new(self):
        return {
            'name': 'loyalty_reward_new',
            'reward_type': 'gift',
            'gift_product_id': self.gift_1.id,
            'point_cost': 20,
            'minimum_points': 50,
        }
