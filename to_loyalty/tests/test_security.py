from odoo.tests.common import tagged
from .common import LoyaltyCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestLoyaltySecurity(LoyaltyCommon):
    @classmethod
    def setUpClass(cls):
        super(TestLoyaltySecurity, cls).setUpClass()
        cls.setup_sale_team()
        cls.setup_given_points()

    def test_00_group_user(self):
        """ user_1 has default groups
            user_1 can read only all loyalty point, program
            user_1 can't read, write, unlink, create rule, reward"""
        group_user = self.env.ref('base.group_user').id
        self.user_1.write({'groups_id': [(6, 0, [group_user])]})

        self._can_read_document(self.user_1, self.loyalty_point_1)
        self._can_not_write_document(self.user_1, self.loyalty_point_1)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_1)

        self._can_read_document(self.user_1, self.loyalty_point_2)
        self._can_not_write_document(self.user_1, self.loyalty_point_2)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_2)

        self._can_read_document(self.user_1, self.loyalty_point_3)
        self._can_not_write_document(self.user_1, self.loyalty_point_3)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_3)

        self._can_not_create_document(
            self.user_1, self.env['loyalty.point'], self._loyalty_point_vals_new())

        self._can_read_document(self.user_1, self.loyalty_program_1)
        self._can_not_write_document(self.user_1, self.loyalty_program_1)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1)

        self._can_read_document(self.user_1, self.loyalty_program_2)
        self._can_not_write_document(self.user_1, self.loyalty_program_2)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_2)

        self._can_read_document(self.user_1, self.loyalty_program_3)
        self._can_not_write_document(self.user_1, self.loyalty_program_3)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_3)
        self._can_not_create_document(
            self.user_1, self.env['loyalty.program'], self._loyalty_program_vals_new())

        self._can_read_document(self.user_1, self.customer_level_1)
        self._can_not_write_document(self.user_1, self.customer_level_1)
        self._can_not_unlink_document(self.user_1, self.customer_level_1)
        self._can_not_create_document(
            self.user_1, self.env['customer.level'], {'name': 'level_444',
                                                      'points': 15000, })

        self._can_not_read_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_write_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_create_document(
            self.user_1, self.env['loyalty.rule'], self._loyalty_rule_vals_new())

        self._can_not_read_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_write_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_create_document(
            self.user_1, self.env['loyalty.reward'], self._loyalty_reward_vals_new())

        report_partner_1 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_1.id)])
        report_partner_2 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_2.id)])
        report_partner_3 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_3.id)])

        self._can_not_read_document(self.user_1, report_partner_1)
        self._can_not_write_document(self.user_1, report_partner_1)
        self._can_not_unlink_document(self.user_1, report_partner_1)

        self._can_not_read_document(self.user_1, report_partner_2)
        self._can_not_write_document(self.user_1, report_partner_2)
        self._can_not_unlink_document(self.user_1, report_partner_2)

        self._can_not_read_document(self.user_1, report_partner_3)
        self._can_not_write_document(self.user_1, report_partner_3)
        self._can_not_unlink_document(self.user_1, report_partner_3)

    def test_01_group_loyalty_user(self):
        """ user_1 has group_loyalty_user
            user_1 can create loyalty point
            user_1 can read only all document"""
        group_loyalty_user = self.env.ref('to_loyalty.group_loyalty_user').id
        self.user_1.write({'groups_id': [(6, 0, [group_loyalty_user])]})

        self._can_read_document(self.user_1, self.loyalty_point_1)
        self._can_not_write_document(self.user_1, self.loyalty_point_1)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_1)

        self._can_read_document(self.user_1, self.loyalty_point_2)
        self._can_not_write_document(self.user_1, self.loyalty_point_2)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_2)

        self._can_read_document(self.user_1, self.loyalty_point_3)
        self._can_not_write_document(self.user_1, self.loyalty_point_3)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_3)

        self._can_create_document(
            self.user_1, self.env['loyalty.point'], self._loyalty_point_vals_new())

        self._can_read_document(self.user_1, self.loyalty_program_1)
        self._can_not_write_document(self.user_1, self.loyalty_program_1)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1)

        self._can_read_document(self.user_1, self.loyalty_program_2)
        self._can_not_write_document(self.user_1, self.loyalty_program_2)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_2)

        self._can_read_document(self.user_1, self.loyalty_program_3)
        self._can_not_write_document(self.user_1, self.loyalty_program_3)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_3)
        self._can_not_create_document(
            self.user_1, self.env['loyalty.program'], self._loyalty_program_vals_new())

        self._can_read_document(self.user_1, self.customer_level_1)
        self._can_not_write_document(self.user_1, self.customer_level_1)
        self._can_not_unlink_document(self.user_1, self.customer_level_1)
        self._can_not_create_document(
            self.user_1, self.env['customer.level'], {'name': 'level_444',
                                                      'points': 15000, })

        self._can_read_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_write_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_create_document(
            self.user_1, self.env['loyalty.rule'], self._loyalty_rule_vals_new())

        self._can_read_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_write_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_create_document(
            self.user_1, self.env['loyalty.reward'], self._loyalty_reward_vals_new())

        report_partner_1 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_1.id)])
        report_partner_2 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_2.id)])
        report_partner_3 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_3.id)])

        self._can_read_document(self.user_1, report_partner_1)
        self._can_not_write_document(self.user_1, report_partner_1)
        self._can_not_unlink_document(self.user_1, report_partner_1)

        self._can_read_document(self.user_1, report_partner_2)
        self._can_not_write_document(self.user_1, report_partner_2)
        self._can_not_unlink_document(self.user_1, report_partner_2)

        self._can_read_document(self.user_1, report_partner_3)
        self._can_not_write_document(self.user_1, report_partner_3)
        self._can_not_unlink_document(self.user_1, report_partner_3)

    def test_02_group_loyalty_manager(self):
        """ user_1 has group_loyalty_manager
            user_1 has full permission with all document of loyalty"""
        group_loyalty_manager = self.env.ref('to_loyalty.group_loyalty_manager').id
        self.user_1.write({'groups_id': [(6, 0, [group_loyalty_manager])]})

        self._check_group_manager()

    def test_03_group_sale_salesman(self):
        """ user_1 has group_sale_salesman
            user_1 can read only loyalty point of team or loyalty point have no team
            user_1 can create loyalty point"""
        group_sale_salesman = self.env.ref('sales_team.group_sale_salesman').id
        self.user_1.write({'groups_id': [(6, 0, [group_sale_salesman])]})

        self._can_read_document(self.user_1, self.loyalty_point_1)
        self._can_not_write_document(self.user_1, self.loyalty_point_1)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_1)

        self._can_not_read_document(self.user_1, self.loyalty_point_2)
        self._can_not_write_document(self.user_1, self.loyalty_point_2)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_2)

        self._can_read_document(self.user_1, self.loyalty_point_3)
        self._can_not_write_document(self.user_1, self.loyalty_point_3)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_3)

        self._can_not_create_document(
            self.user_1, self.env['loyalty.point'], self._loyalty_point_vals_new())

        self._can_read_document(self.user_1, self.loyalty_program_1)
        self._can_not_write_document(self.user_1, self.loyalty_program_1)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1)

        self._can_read_document(self.user_1, self.loyalty_program_2)
        self._can_not_write_document(self.user_1, self.loyalty_program_2)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_2)

        self._can_read_document(self.user_1, self.loyalty_program_3)
        self._can_not_write_document(self.user_1, self.loyalty_program_3)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_3)
        self._can_not_create_document(
            self.user_1, self.env['loyalty.program'], self._loyalty_program_vals_new())

        self._can_read_document(self.user_1, self.customer_level_1)
        self._can_not_write_document(self.user_1, self.customer_level_1)
        self._can_not_unlink_document(self.user_1, self.customer_level_1)
        self._can_not_create_document(
            self.user_1, self.env['customer.level'], {'name': 'level_444',
                                                      'points': 15000, })

        self._can_read_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_write_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_create_document(
            self.user_1, self.env['loyalty.rule'], self._loyalty_rule_vals_new())

        self._can_read_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_write_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_create_document(
            self.user_1, self.env['loyalty.reward'], self._loyalty_reward_vals_new())

        report_partner_1 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_1.id)])
        report_partner_2 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_2.id)])
        report_partner_3 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_3.id)])

        self._can_read_document(self.user_1, report_partner_1)
        self._can_not_write_document(self.user_1, report_partner_1)
        self._can_not_unlink_document(self.user_1, report_partner_1)

        self._can_not_read_document(self.user_1, report_partner_2)
        self._can_not_write_document(self.user_1, report_partner_2)
        self._can_not_unlink_document(self.user_1, report_partner_2)

        self._can_read_document(self.user_1, report_partner_3)
        self._can_not_write_document(self.user_1, report_partner_3)
        self._can_not_unlink_document(self.user_1, report_partner_3)

    def test_04_group_sale_manager(self):
        """ user_1 has group_loyalty_manager
            user_1 has full permission with all document of loyalty"""
        group_sale_manager = self.env.ref('sales_team.group_sale_manager').id
        self.user_1.write({'groups_id': [(6, 0, [group_sale_manager])]})
        self._check_group_manager()

    def test_05_group_sale_salesman_all_leads(self):
        """ user_1 has group_sale_salesman_all_leads
            user_1 read all documents"""
        group_sale_salesman_all_leads = self.env.ref('sales_team.group_sale_salesman_all_leads').id
        self.user_1.write({'groups_id': [(6, 0, [group_sale_salesman_all_leads])]})

        self._can_read_document(self.user_1, self.loyalty_point_1)
        self._can_not_write_document(self.user_1, self.loyalty_point_1)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_1)

        self._can_read_document(self.user_1, self.loyalty_point_2)
        self._can_not_write_document(self.user_1, self.loyalty_point_2)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_2)

        self._can_read_document(self.user_1, self.loyalty_point_3)
        self._can_not_write_document(self.user_1, self.loyalty_point_3)
        self._can_not_unlink_document(self.user_1, self.loyalty_point_3)

        self._can_create_document(
            self.user_1, self.env['loyalty.point'], self._loyalty_point_vals_new())

        self._can_read_document(self.user_1, self.loyalty_program_1)
        self._can_not_write_document(self.user_1, self.loyalty_program_1)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1)

        self._can_read_document(self.user_1, self.loyalty_program_2)
        self._can_not_write_document(self.user_1, self.loyalty_program_2)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_2)

        self._can_read_document(self.user_1, self.loyalty_program_3)
        self._can_not_write_document(self.user_1, self.loyalty_program_3)
        self._can_not_unlink_document(self.user_1, self.loyalty_program_3)
        self._can_not_create_document(
            self.user_1, self.env['loyalty.program'], self._loyalty_program_vals_new())

        self._can_read_document(self.user_1, self.customer_level_1)
        self._can_not_write_document(self.user_1, self.customer_level_1)
        self._can_not_unlink_document(self.user_1, self.customer_level_1)
        self._can_not_create_document(
            self.user_1, self.env['customer.level'], {'name': 'level_444',
                                                      'points': 15000, })

        self._can_read_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_write_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_not_create_document(
            self.user_1, self.env['loyalty.rule'], self._loyalty_rule_vals_new())

        self._can_read_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_write_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_unlink_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_not_create_document(
            self.user_1, self.env['loyalty.reward'], self._loyalty_reward_vals_new())

        report_partner_1 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_1.id)])
        report_partner_2 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_2.id)])
        report_partner_3 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_3.id)])

        self._can_read_document(self.user_1, report_partner_1)
        self._can_not_write_document(self.user_1, report_partner_1)
        self._can_not_unlink_document(self.user_1, report_partner_1)

        self._can_read_document(self.user_1, report_partner_2)
        self._can_not_write_document(self.user_1, report_partner_2)
        self._can_not_unlink_document(self.user_1, report_partner_2)

        self._can_read_document(self.user_1, report_partner_3)
        self._can_not_write_document(self.user_1, report_partner_3)
        self._can_not_unlink_document(self.user_1, report_partner_3)

    def _check_group_manager(self):
        self._can_read_document(self.user_1, self.loyalty_point_1)
        self._can_write_document(self.user_1, self.loyalty_point_1)
        self._can_unlink_document(self.user_1, self.loyalty_point_1)

        self._can_read_document(self.user_1, self.loyalty_point_2)
        self._can_write_document(self.user_1, self.loyalty_point_2)
        self._can_unlink_document(self.user_1, self.loyalty_point_2)

        self._can_read_document(self.user_1, self.loyalty_point_3)
        self._can_write_document(self.user_1, self.loyalty_point_3)
        self._can_unlink_document(self.user_1, self.loyalty_point_3)

        self._can_create_document(
            self.user_1, self.env['loyalty.point'], self._loyalty_point_vals_new())

        self._can_read_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_write_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_unlink_document(self.user_1, self.loyalty_program_1.rule_ids[0])
        self._can_create_document(
            self.user_1, self.env['loyalty.rule'], self._loyalty_rule_vals_new())

        self._can_read_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_write_document(self.user_1, self.loyalty_program_1.reward_ids[0])
        self._can_unlink_document(self.user_1, self.loyalty_program_1.reward_ids[0])

        self._can_create_document(
            self.user_1, self.env['loyalty.reward'], self._loyalty_reward_vals_new())

        self.env['loyalty.point'].search([
            ('loyalty_program_id', 'in', [self.loyalty_program_1.id, self.loyalty_program_2.id, self.loyalty_program_3.id])]).unlink()
        self._can_read_document(self.user_1, self.loyalty_program_1)
        self._can_write_document(self.user_1, self.loyalty_program_1)
        self._can_unlink_document(self.user_1, self.loyalty_program_1)

        self._can_read_document(self.user_1, self.loyalty_program_2)
        self._can_write_document(self.user_1, self.loyalty_program_2)
        self._can_unlink_document(self.user_1, self.loyalty_program_2)

        self._can_read_document(self.user_1, self.loyalty_program_3)
        self._can_write_document(self.user_1, self.loyalty_program_3)
        self._can_unlink_document(self.user_1, self.loyalty_program_3)
        self._can_create_document(
            self.user_1, self.env['loyalty.program'], self._loyalty_program_vals_new())

        self._can_read_document(self.user_1, self.customer_level_1)
        self._can_write_document(self.user_1, self.customer_level_1)
        self._can_unlink_document(self.user_1, self.customer_level_1)
        self._can_create_document(
            self.user_1, self.env['customer.level'], {'name': 'level_444',
                                                      'points': 15000, })

        report_partner_1 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_1.id)])
        report_partner_2 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_2.id)])
        report_partner_3 = self.env['loyalty.points.report'].search([('partner_id', '=', self.partner_3.id)])

        self._can_read_document(self.user_1, report_partner_1)
        self._can_write_document(self.user_1, report_partner_1)
        self._can_unlink_document(self.user_1, report_partner_1)

        self._can_read_document(self.user_1, report_partner_2)
        self._can_write_document(self.user_1, report_partner_2)
        self._can_unlink_document(self.user_1, report_partner_2)

        self._can_read_document(self.user_1, report_partner_3)
        self._can_write_document(self.user_1, report_partner_3)
        self._can_unlink_document(self.user_1, report_partner_3)
