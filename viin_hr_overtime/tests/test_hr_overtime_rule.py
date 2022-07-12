from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tools import mute_logger
from odoo.exceptions import UserError

from .common import Common


@tagged('post_install', '-at_install')
class TestHrOvertimeRule(Common):

    def setUp(self):
        super(TestHrOvertimeRule, self).setUp()

    @mute_logger('odoo.sql_db')
    def test_01_overtime_rule_period(self):
        """
            Case: Test overtime rule period in case hour_from is greater than hour_to.
            Expect: Failed to create new rule, show user error.
        """
        with self.assertRaises(IntegrityError):
            self.monday_evening_ot_rule.hour_from = 23.0

    @mute_logger('odoo.sql_db')
    def test_02_overtime_rule_period(self):
        """
            Case: Test overtime rule period in case hour_from = hour_to.
            Expect: Failed to create new rule, show user error.
        """
        with self.assertRaises(IntegrityError):
            self.monday_evening_ot_rule.hour_from = 22.0

    def test_03_format_hour_from_hour_to(self):
        """
            Case: Test hour from / hour to in case input is not float value.
            Expect: Show validation error.
        """
        with self.assertRaises(ValueError):
            self.monday_evening_ot_rule.hour_from = '4hour'
        with self.assertRaises(ValueError):
            self.monday_evening_ot_rule.hour_to = '4hour'

    @mute_logger('odoo.sql_db')
    def test_04_format_hour_from_hour_to(self):
        """
            Case: Test hour from / hour to in case input is negative float value.
            Expect: Show validation error.
        """
        with self.assertRaises(IntegrityError):
            self.monday_evening_ot_rule.hour_from = '-2.0'
            self.monday_evening_ot_rule.hour_to = '-1.0'

    @mute_logger('odoo.sql_db')
    def test_05_format_hour_hour_to(self):
        """
            Case: Test hour from / hour to in case input is greater than 24.
            Expect: Show validation error.
        """
        with self.assertRaises(IntegrityError):
            self.monday_evening_ot_rule.hour_from = '24.0'
            self.monday_evening_ot_rule.hour_to = '25.0'

    def test_06_overlap_overtime_rule(self):
        """
            Case: Test difference overtime rule input same hour_from and hour_to.
            Expect: Failed to create new rule, show user error.
        """
        with self.assertRaises(UserError):
            self.env['hr.overtime.rule'].create({
                'name':'Monday Night Extra',
                'weekday': '0',
                'code_id':self.env.ref('viin_hr_overtime.rule_code_ot2224').id,
                'hour_from': 22.0,
                'hour_to': 24.0
                })

    def test_07_overlap_overtime_rule(self):
        """
            Case: Test overtime rule have period same an other rule.
            *eg:Already exist a Overtime Rule with period.
                hour_from: 18.0
                hour_to  : 22.0
            Expect: Failed to create new rule with time in period 18.0 -> 22.0, show user error.
        """
        with self.assertRaises(UserError):
            self.env['hr.overtime.rule'].create({
                'name':'Monday Evening Extra',
                'weekday': '0',
                'code_id': self.env.ref('viin_hr_overtime.rule_code_ot2224').id,
                'hour_from': 18.0,
                'hour_to': 20.0
                })

    def test_08_overlap_overtime_rule(self):
        """
            Case: Test edit an overtime rule, which has period overlap other rules.
            Expect: Failed to edit, show user error.
        """
        with self.assertRaises(UserError):
            self.monday_evening_ot_rule.hour_from = '16.0'

    @mute_logger('odoo.sql_db')
    def test_09_overlap_overtime_rule(self):
        """
            Case: Test duplicate overtime rule.
            Expect: Failed to duplicated, show user error.
        """
        with self.assertRaises(UserError):
            self.monday_evening_ot_rule.copy()

    def test_10_compute_pay_rate_holiday(self):
        """
            Case: test compute pay_rate / holiday of overtime rule in case change other rule code.
            Expect: Value of pay_rate / holiday of rule will change with value of pay_rate / holiday in rule code.
        """
        self.monday_evening_ot_rule.code_id = self.env.ref('viin_hr_overtime.rule_code_othol0006').id
        self.assertEqual(self.monday_evening_ot_rule.pay_rate, self.env.ref('viin_hr_overtime.rule_code_othol0006').pay_rate)
        self.assertEqual(self.monday_evening_ot_rule.holiday, self.env.ref('viin_hr_overtime.rule_code_othol0006').holiday)

    def test_11_compute_pay_rate_holiday(self):
        """
            Case: Test compute pay_rate / holiday of overtime rule in case edit pay rate / holiday of current rule code.
            Expect: Value of pay_rate / holiday of rule will change with new rule code.
        """
        self.env.ref('viin_hr_overtime.rule_code_ot1822').pay_rate = 1000
        self.env.ref('viin_hr_overtime.rule_code_ot1822').holiday = True
        self.assertEqual(self.monday_evening_ot_rule.pay_rate, 1000)
        self.assertTrue(self.monday_evening_ot_rule.holiday, True)
