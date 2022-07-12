from odoo.tests.common import tagged
from odoo.addons.to_loyalty.tests.common import LoyaltyCommon


@tagged('post_install', '-at_install', 'access_rights')
class TestPosSecurity(LoyaltyCommon):
    @classmethod
    def setUpClass(cls):
        super(TestPosSecurity, cls).setUpClass()
        cls.setup_sale_team()
        cls.setup_given_points()

    def test_01_group_pos_user(self):
        """ user_1 has group_pos_user
            user_1 can create loyalty point
            user_1 can read only all document"""
        group_pos_user = self.env.ref('point_of_sale.group_pos_user').id
        self.user_1.write({'groups_id': [(6, 0, [group_pos_user])]})

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

    def test_02_group_pos_manager(self):
        """ user_1 has group_pos_manager
            user_1 has full permission with all document of loyalty"""
        group_pos_manager = self.env.ref('point_of_sale.group_pos_manager').id
        self.user_1.write({'groups_id': [(6, 0, [group_pos_manager])]})

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
