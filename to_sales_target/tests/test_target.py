from datetime import datetime
from psycopg2 import IntegrityError

from odoo.tools import mute_logger, float_compare
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .target_common import TargetCommon


@tagged('post_install', '-at_install')
class TestSalesTarget(TargetCommon):

    @classmethod
    def setUpClass(cls):
        super(TestSalesTarget, cls).setUpClass()

        # Create data Sale team's target and Sale personal target
        cls.SalesTarget = cls.env['team.sales.target']
        cls.team1_target = cls.form_create_team_target(cls.team1,
                                                       datetime(2020, 8, 16),
                                                       datetime(2020, 8, 18),
                                                       target=1000)

        cls.team2_target = cls.form_create_team_target(cls.team2,
                                                       datetime(2020, 8, 26),
                                                       datetime(2020, 8, 28))

    def test_overlapped_01_team_sales_target(self):
        SalesTarget1 = self.SalesTarget.with_context(default_crm_team_id=self.team1.id, default_target=10000)

        with self.assertRaises(ValidationError), self.cr.savepoint():
            SalesTarget1.create({'start_date': datetime(2020, 8, 16), 'end_date': datetime(2020, 8, 18)})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            SalesTarget1.create({'start_date': datetime(2020, 8, 14), 'end_date': datetime(2020, 8, 16)})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            SalesTarget1.create({'start_date': datetime(2020, 8, 14), 'end_date': datetime(2020, 8, 17)})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            SalesTarget1.create({'start_date': datetime(2020, 8, 17), 'end_date': datetime(2020, 8, 20)})

        SalesTarget1.create({
            'start_date': datetime(2020, 8, 10),
            'end_date': datetime(2020, 8, 15)
        })

    def test_overlapped_02_personal_sales_target(self):
        self.team2.member_ids = [self.user_salesman.id]

        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.form_create_team_target(self.team2, datetime(2020, 8, 16), datetime(2020, 8, 18))

        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.form_create_team_target(self.team2, datetime(2020, 8, 14), datetime(2020, 8, 16))

        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.form_create_team_target(self.team2, datetime(2020, 8, 14), datetime(2020, 8, 17))

        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.form_create_team_target(self.team2, datetime(2020, 8, 17), datetime(2020, 8, 20))

        self.form_create_team_target(self.team2, datetime(2020, 8, 19), datetime(2020, 8, 25))

    @mute_logger('odoo.sql_db')
    def test_overlapped_duplicate_personal_target_in_team_target(self):
        self.team1_target.state = 'draft'
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.team1_target.personal_target_ids[0].sale_person_id = self.team1_target.personal_target_ids[1].sale_person_id

    def test_divide_target_when_generate_sale_personal_target(self):
        divided_target = self.team1_target.target / len(self.team1_target.personal_target_ids)

        self.assertEqual(float_compare(self.team1_target.personal_target_ids[-1:].target, divided_target, 0.1), 0, "Sale personal target value is computed wrong when create sale team's target!")

    def test_approval_team_target(self):
        self.team1_target.action_confirm()
        with self.assertRaises(ValidationError):
            self.team1_target.with_user(self.user_leader).action_approve()
        self.team1_target.with_user(self.user_regional).action_approve()

    def test_state_personal_target_follow_state_team_target(self):
        team_target = self.team1_target
        personal_target = team_target.personal_target_ids[-1:]

        self.assertEqual(team_target.state, 'draft')
        self.assertEqual(personal_target.state, 'draft')

        team_target.action_confirm()

        self.assertEqual(team_target.state, 'confirmed')
        self.assertEqual(personal_target.state, 'confirmed')

        team_target.action_approve()

        self.assertEqual(team_target.state, 'approved')
        self.assertEqual(personal_target.state, 'approved')

        team_target.action_cancel()

        self.assertEqual(team_target.state, 'cancelled')
        self.assertEqual(personal_target.state, 'cancelled')

        team_target.action_draft()

        self.assertEqual(team_target.state, 'draft')
        self.assertEqual(personal_target.state, 'draft')

        team_target.action_confirm()
        team_target.action_refuse()

        self.assertEqual(team_target.state, 'refused')
        self.assertEqual(personal_target.state, 'refused')

    def test_function_get_target_by_date(self):
        # Prepare data for test func
        # Quarter 1
        # Month 1
        # Week 0
        team1_q1_m1_w0 = self.form_create_team_target(self.team1, datetime(2021, 1, 1), datetime(2021, 1, 1))
        self.form_create_team_target(self.team2, datetime(2021, 1, 1), datetime(2021, 1, 1))
        # Week 1,2
        team1_q1_m1_w12_1 = self.form_create_team_target(self.team1, datetime(2021, 1, 2), datetime(2021, 1, 5))
        self.form_create_team_target(self.team2, datetime(2021, 1, 2), datetime(2021, 1, 5))
        team1_q1_m1_w12_2 = self.form_create_team_target(self.team1, datetime(2021, 1, 6), datetime(2021, 1, 9))
        self.form_create_team_target(self.team2, datetime(2021, 1, 6), datetime(2021, 1, 9))
        # Month 1,2
        team1_q1_m12 = self.form_create_team_target(self.team1, datetime(2021, 1, 25), datetime(2021, 2, 24))
        # Month 2,3
        team1_q1_m23 = self.form_create_team_target(self.team1, datetime(2021, 2, 25), datetime(2021, 3, 15))
        self.form_create_team_target(self.team2, datetime(2021, 2, 25), datetime(2021, 3, 15))

        # Quarter 1,2
        # Month 3,4
        team1_q1_m34 = self.form_create_team_target(self.team1, datetime(2021, 3, 17), datetime(2021, 4, 12))

        # Quarter 4/2021, 1/2022
        team1_q4 = self.form_create_team_target(self.team1, datetime(2021, 12, 19), datetime(2022, 1, 18))
        self.form_create_team_target(self.team2, datetime(2021, 12, 19), datetime(2022, 1, 18))

        self.SalesTarget.search([]).write({'state': 'approved'})
        default_target = 100
        precision_rounding = 0.1

        # Test with target team
        sum_target, targets = self.team1.get_target_by_date(datetime(2021, 1, 1), period='day')
        self.assertEqual(sum_target, default_target, "func get_target_by_date compute sum_target day wrong for team")
        self.assertEqual(targets, team1_q1_m1_w0, "func get_target_by_date compute targetss day wrong for team")

        sum_target, targets = self.team1.get_target_by_date(datetime(2021, 1, 4), period='week')  # 2021/1/4 - 2021/1/10
        self.assertEqual(sum_target, default_target + 2 * (default_target / 4), "func get_target_by_date compute sum_target week wrong for team")
        self.assertEqual(targets, team1_q1_m1_w12_1 + team1_q1_m1_w12_2, "func get_target_by_date compute targets week wrong for team")

        sum_target, targets = self.team1.get_target_by_date(datetime(2021, 1, 15), period='month')
        self.assertEqual(float_compare(sum_target, default_target * 3 + 7 * (default_target / 31), precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target month wrong for team")
        self.assertEqual(targets, team1_q1_m1_w0 + team1_q1_m1_w12_1 + team1_q1_m1_w12_2 + team1_q1_m12, "func get_target_by_date compute targets month wrong for team")

        sum_target, targets = self.team1.get_target_by_date(datetime(2021, 3, 10), period='month')
        self.assertEqual(float_compare(sum_target, 15 * (default_target / 19) + 15 * (default_target / 27), precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target month wrong for team")
        self.assertEqual(targets, team1_q1_m23 + team1_q1_m34, "func get_target_by_date compute targets month wrong for team")

        sum_target, targets = self.team1.get_target_by_date(datetime(2021, 3, 1), period='quarter')
        self.assertEqual(float_compare(sum_target, default_target * 5 + 15 * (default_target / 27), precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target quarter wrong for team")
        self.assertEqual(targets, team1_q1_m1_w0 + team1_q1_m1_w12_1 + team1_q1_m1_w12_2 + team1_q1_m12 + team1_q1_m23 + team1_q1_m34, "func get_target_by_date compute targets quarter wrong for team")

        sum_target, targets = self.team1.get_target_by_date(datetime(2021, 3, 1), period='year')
        self.assertEqual(float_compare(sum_target, default_target * 6 + 13 * (default_target / 31), precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target year wrong for team")
        self.assertEqual(targets, team1_q1_m1_w0 + team1_q1_m1_w12_1 + team1_q1_m1_w12_2 + team1_q1_m12 + team1_q1_m23 + team1_q1_m34 + team1_q4, "func get_target_by_date compute targets year wrong for team")

        # Test with personal target
        default_target = 100 / len(self.team1.member_ids)
        self.env['personal.sales.target'].search([]).write({'state': 'approved'})

        get_rc_saleman = lambda r: r.filtered(lambda t: t.sale_person_id == self.user_salesman)

        sum_target, targets = self.user_salesman.get_target_by_date(datetime(2021, 1, 1), period='day')
        self.assertEqual(float_compare(sum_target, default_target, precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target day wrong for user")
        self.assertEqual(targets, get_rc_saleman(team1_q1_m1_w0.personal_target_ids), "func get_target_by_date compute targets day wrong for user")

        sum_target, targets = self.user_salesman.get_target_by_date(datetime(2021, 1, 4), period='week')  # 2021/1/4 - 2021/1/10
        self.assertEqual(float_compare(sum_target, default_target + 2 * (default_target / 4), precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target week wrong for user")
        self.assertEqual(targets, get_rc_saleman((team1_q1_m1_w12_1 + team1_q1_m1_w12_2).personal_target_ids), "func get_target_by_date compute targets week wrong for user")

        sum_target, targets = self.user_salesman.get_target_by_date(datetime(2021, 1, 15), period='month')
        self.assertEqual(float_compare(sum_target, default_target * 3 + 7 * (default_target / 31), precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target month wrong for user")
        self.assertEqual(targets, get_rc_saleman((team1_q1_m1_w0 + team1_q1_m1_w12_1 + team1_q1_m1_w12_2 + team1_q1_m12).personal_target_ids), "func get_target_by_date compute targets month wrong for user")

        sum_target, targets = self.user_salesman.get_target_by_date(datetime(2021, 3, 10), period='month')
        self.assertEqual(float_compare(sum_target, 15 * (default_target / 19) + 15 * (default_target / 27), precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target month wrong for user")
        self.assertEqual(targets, get_rc_saleman((team1_q1_m23 + team1_q1_m34).personal_target_ids), "func get_target_by_date compute targets month wrong for user")

        sum_target, targets = self.user_salesman.get_target_by_date(datetime(2021, 3, 1), period='quarter')
        self.assertEqual(float_compare(sum_target, default_target * 5 + 15 * (default_target / 27), precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target quarter wrong for user")
        self.assertEqual(targets, get_rc_saleman((team1_q1_m1_w0 + team1_q1_m1_w12_1 + team1_q1_m1_w12_2 + team1_q1_m12 + team1_q1_m23 + team1_q1_m34).personal_target_ids), "func get_target_by_date compute targets quarter wrong for user")

        sum_target, targets = self.user_salesman.get_target_by_date(datetime(2021, 3, 1), period='year')
        self.assertEqual(float_compare(sum_target, default_target * 6 + 13 * (default_target / 31), precision_rounding=precision_rounding), 0, "func get_target_by_date compute sum_target year wrong for user")
        self.assertEqual(targets, get_rc_saleman((team1_q1_m1_w0 + team1_q1_m1_w12_1 + team1_q1_m1_w12_2 + team1_q1_m12 + team1_q1_m23 + team1_q1_m34 + team1_q4).personal_target_ids), "func get_target_by_date compute targets year wrong for user")
