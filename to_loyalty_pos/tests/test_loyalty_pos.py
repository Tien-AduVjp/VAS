from odoo.tests.common import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestLoyaltyPos(HttpCase):
    def test_2001_loyalty_pos(self):
        env = self.env(user=self.env.ref('base.user_admin'))
        env.ref('product.product_delivery_01').write({
            'name': 'product_1',
            'categ_id': env.ref('product.product_category_1').id,
            'price': 5000000,
            'standard_price': 5000000,
            'available_in_pos': True,
            'pos_categ_id': env.ref('point_of_sale.pos_category_desks').id
        })
        env.ref('product.product_delivery_02').write({
            'name': 'product_2',
            'categ_id': env.ref('product.product_category_2').id,
            'price': 10000000,
            'standard_price': 10000000,
            'available_in_pos': True,
            'pos_categ_id': env.ref('point_of_sale.pos_category_chairs').id
        })
        env.ref('product.product_order_01').write({
            'name': 'product_3',
            'categ_id': env.ref('product.product_category_2').id,
            'price': 6000000,
            'standard_price': 6000000,
            'available_in_pos': True,
            'pos_categ_id': env.ref('point_of_sale.pos_category_chairs').id
        })

        env.ref('product.product_product_3').write({
            'name': 'gift_1',
            'price': 8000000,
            'standard_price': 8000000,
            'available_in_pos': True,
            'pos_categ_id': env.ref('point_of_sale.pos_category_desks').id
        })

        pos_config = env.ref('point_of_sale.pos_config_main')
        program_1 = env['loyalty.program'].create({
            'name': 'loyalty_program_1',
            'pp_currency': 0.000001,
            'pp_product': 5,
            'pp_order': 3,
            'currency_id': 2,
            'rule_ids': [(0, 0, {
                'name': 'loyalty_rule_1',
                'rule_type': 'product',
                'product_id': env.ref('product.product_delivery_01').product_variant_id.id,
                'cumulative': False,
                'pp_product': 5,
                'pp_currency': 0.000001
            }), (0, 0, {
                'name': 'loyalty_rule_2',
                'rule_type': 'product_category',
                'product_category_id': env.ref('product.product_category_2').id,
                'cumulative': False,
                'pp_product': 10,
                'pp_currency': 0.000010
            }),
                (0, 0, {
                    'name': 'loyalty_rule_pos',
                    'rule_type': 'product',
                    'rule_type': 'pos_category',
                    'pos_category_id': env.ref('point_of_sale.pos_category_desks').id,
                    'cumulative': False,
                    'pp_product': 8,
                    'pp_currency': 0.000001
                }),
            ],
            'reward_ids': [
                (0, 0, {
                    'name': 'loyalty_reward_1',
                    'reward_type': 'gift',
                    'gift_product_id': env.ref('product.product_product_3').id,
                    'point_cost': 20,
                    'minimum_points': 50,
                }),
                (0, 0, {
                    'name': 'loyalty_reward_2',
                    'reward_type': 'discount',
                    'discount': 10.0,
                    'discount_product_id': env.ref('product.product_delivery_01').product_variant_id.id,
                    'point_cost': 30,
                    'minimum_points': 101,
                })]
        })
        # loyalty_point_partner_1
        env['loyalty.point'].create({
            'partner_id': env.ref('base.res_partner_1').id,
            'loyalty_program_id': program_1.id,
            'points': 100,
        })
        # loyalty_point_partner_2
        env['loyalty.point'].create({
            'partner_id': env.ref('base.res_partner_2').id,
            'loyalty_program_id': program_1.id,
            'points': 5000000000000,
        })

        env['ir.module.module'].search([('name', '=', 'point_of_sale')], limit=1).state = 'installed'
        self.check_2001_calculate_won_points(env, pos_config)
        self.check_2002_calculate_won_points(env, pos_config, program_1)
        self.check_2003_calculate_won_points(env, pos_config, program_1)
        self.check_2004_calculate_won_points(env, pos_config, program_1)
        self.check_2005_calculate_won_points(env, pos_config)
        self.check_3004_calculate_spent_points(env, pos_config)
        self.check_3005_calculate_spent_points(env, pos_config)

    def check_2001_calculate_won_points(self, env, pos_config):
        """No rule"""
        program_no_rules = env['loyalty.program'].create({
            'name': 'loyalty_program_1',
            'pp_currency': 0.000001,
            'pp_product': 5,
            'pp_order': 3,
            'currency_id': env['res.currency'].browse(2).id,
        })
        pos_config.write({'loyalty_id': program_no_rules.id})
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, 'loyalty_pos_tour_product_1', login="admin")
        pos_order = env['pos.order'].search([('session_id', '=', pos_config.current_session_id.id)])
        self.assertEqual(pos_order.loyalty_points, 13.0, "to_loyalty_points: Wrong calculate won points")
        self.assertEqual(pos_order.lines[0].loyalty_points, 10.0, "to_loyalty_points: Wrong calculate won points")
        pos_config.current_session_id.action_pos_session_closing_control()

    def check_2002_calculate_won_points(self, env, pos_config, program_1):
        pos_config.write({'loyalty_id': program_1.id})
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, 'loyalty_pos_tour_product_1', login="admin")
        pos_order = env['pos.order'].search([('session_id', '=', pos_config.current_session_id.id)])
        self.assertEqual(pos_order.loyalty_points, 13.0, "to_loyalty_points: Wrong calculate won points")
        self.assertEqual(pos_order.lines[0].loyalty_points, 10.0, "to_loyalty_points: Wrong calculate won points")
        pos_config.current_session_id.action_pos_session_closing_control()

    def check_2003_calculate_won_points(self, env, pos_config, program_1):
        program_1.rule_ids[0].cumulative = True
        pos_config.write({'loyalty_id': program_1.id})
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, 'loyalty_pos_tour_product_1', login="admin")
        pos_order = env['pos.order'].search([('session_id', '=', pos_config.current_session_id.id)])
        self.assertEqual(pos_order.loyalty_points, 26.0, "to_loyalty_points: Wrong calculate won points")
        self.assertEqual(pos_order.lines[0].loyalty_points, 23.0, "to_loyalty_points: Wrong calculate won points")
        pos_config.current_session_id.action_pos_session_closing_control()

    def check_2004_calculate_won_points(self, env, pos_config, program_1):
        program_1.rule_ids[0].cumulative = False
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, 'loyalty_pos_tour_product_1', login="admin")
        pos_order = env['pos.order'].search([('session_id', '=', pos_config.current_session_id.id)])
        self.assertEqual(pos_order.loyalty_points, 13.0, "to_loyalty_points: Wrong calculate won points")
        self.assertEqual(pos_order.lines[0].loyalty_points, 10.0, "to_loyalty_points: Wrong calculate won points")
        pos_config.current_session_id.action_pos_session_closing_control()

    def check_2005_calculate_won_points(self, env, pos_config):
        """No matching rules"""
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, 'loyalty_pos_tour_product_3', login="admin")
        pos_order = env['pos.order'].search([('session_id', '=', pos_config.current_session_id.id)])
        self.assertEqual(pos_order.loyalty_points, 14.0, "to_loyalty_points: Wrong calculate won points")
        self.assertEqual(pos_order.lines[0].loyalty_points, 11.0, "to_loyalty_points: Wrong calculate won points")
        pos_config.current_session_id.action_pos_session_closing_control()

    def check_3004_calculate_spent_points(self, env, pos_config):
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, 'loyalty_pos_tour_spent_points_gift', login="admin")
        pos_order = env['pos.order'].search([('session_id', '=', pos_config.current_session_id.id)])
        self.assertEqual(pos_order.loyalty_points, -7, "to_loyalty_points: Wrong calculate won points")
        self.assertEqual(pos_order.lines[1].loyalty_points, -20.0, "to_loyalty_points: Wrong calculate spent points")
        pos_config.current_session_id.action_pos_session_closing_control()

    def check_3005_calculate_spent_points(self, env, pos_config):
        pos_config.open_session_cb()
        self.start_tour("/pos/web?config_id=%d" % pos_config.id, 'loyalty_pos_tour_spent_points_discount', login="admin")
        pos_order = env['pos.order'].search([('session_id', '=', pos_config.current_session_id.id)])
        self.assertEqual(pos_order.loyalty_points, -14999987.0, "to_loyalty_points: Wrong calculate won points")
        self.assertEqual(pos_order.lines[1].loyalty_points, -15000000.0, "to_loyalty_points: Wrong calculate spent points")
        pos_config.current_session_id.action_pos_session_closing_control()
