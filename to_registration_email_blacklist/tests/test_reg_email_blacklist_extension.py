import psycopg2
try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    UniqueViolation = psycopg2.IntegrityError

from odoo.tests import tagged
from odoo.exceptions import UserError
from odoo.tools import mute_logger
from .common import TestSignUpCommon

@tagged('post_install', '-at_install')
class TestSignUpExtension(TestSignUpCommon):

    def _create_rule(self, rule):
        new_rule = self.env['email.blacklist.rule'].with_context(tracking_disable=True).create({
            'name': rule,
            'reason_id': self.env.ref('to_registration_email_blacklist.block_reason_common').id
        })
        return new_rule

    # ***************************** TEST CASES ****************************** #

    def test_01_without_setting(self):
        """
            Setting Email Registration Blacklisting is off
        """
        self.env['ir.config_parameter'].sudo().set_param('block_blacklisted_registration_emails', False)

        # Email to test
        email = 'test_example@75hosting.com'

        # Sign up
        res = self._sign_up(email=email, csrf_token=self._get_csrf_token())

        self.assertTrue(
            'Your registration email was blacklisted and blocked by our administrations.' not in str(res.content),
            "Sign up with email not in blacklist should be successful."
        )

    def test_04_sql_constrain_unique_rule_name(self):
        """
            domain "75hosting.com" is already existed in the database
            Add a new rule that has exactly the same name
            Expect:
                Can't create the new rule
        """
        with self.assertRaises(UniqueViolation), mute_logger('odoo.sql_db'):
            self._create_rule(rule='75hosting.com')

    def test_05_sql_constrain_archieved_record(self):
        """
            domain "baxomale.ht.cx" is already existed in the database
            Add a new rule that has exactly the same name
            Expect:
                Can't create the new rule
        """
        test_rule = self.env.ref('to_registration_email_blacklist.baxomale_ht_cx')
        test_rule.write({'active': False})

        with self.assertRaises(UniqueViolation), mute_logger('odoo.sql_db'):
            self._create_rule(rule='baxomale.ht.cx')

    def test_06_07_08_09_10_test_api_constrains(self):
        """
            Input:
                1) Create a new rule: *@*
                2) Create a new rule:  @*
                3) Create a new rule: *@
                4) Create a new rule: n@*
                    where n = any number of whiteplace
                5) Create a new rule: domaintestcom
                    where the rule includes no "." (dot)
            Expect:
                Can't create this rule
        """
        with self.assertRaises(UserError):
            # Create rule
            self._create_rule(rule='*@*')

        with self.assertRaises(UserError):
            # Create rule
            self._create_rule(rule='@*')

        with self.assertRaises(UserError):
            # Create rule
            self._create_rule(rule='*@')

        with self.assertRaises(UserError):
            # Create rule
            self._create_rule(rule='      @*')

        with self.assertRaises(UserError):
            # Create rule
            self._create_rule(rule='domaintestcom')

    def test_11_test_split_email(self):
        """
            Input
                Create a new rule: test@local@domaintest.com
            Expect
                A new rule created with name = domaintest.com
        """
        email = 'test@local@domaintest.com'
        test_rule = self._create_rule(rule=email)
        self.assertEqual(test_rule.name, email)

        local, domain = test_rule._split_email(email)
        self.assertEqual(local, 'test@local')
        self.assertEqual(domain, 'domaintest.com')

    def test_12_test_domain_signup_error(self):
        """
            Input:
                rule      *.onepiece.com
                email:    test@pirate.onepiece.com
        """
        # Create rule
        self._create_rule(rule='*.onepiece.com')
        # Email to test
        email = 'test@pirate.onepiece.com'

        # Sign up
        res = self._sign_up(email=email, csrf_token=self._get_csrf_token())

        error = 'Your registration email was blacklisted and blocked by our administrations.' in str(res.content)
        self.assertTrue(
            error or res.headers.get('X-Frame-Options','').lower() == 'deny',
            "Sign up with email in blacklist should not be successful."
        )

    def test_13_test_domain_signup_error(self):
        """
            Input:
                rule:    luffy@onepiece.com
                email:   luffy@onepiece.com
        """
        # Create rule
        self._create_rule(rule='luffy@onepiece.com')
        # Email to test
        email = 'luffy@onepiece.com'

        # Sign up
        res = self._sign_up(email=email, csrf_token=self._get_csrf_token())

        error = 'Your registration email was blacklisted and blocked by our administrations.' in str(res.content)
        self.assertTrue(
            error or res.headers.get('X-Frame-Options','').lower() == 'deny',
            "Sign up with email in blacklist should not be successful."
        )

    def test_14_test_domain_signup_error(self):
        """
            Input:
                rule:    *luffy*@*.onepiece.com
                email:   monkeyDluffy_king@pirate.onepiece.com
        """
        # Create rule
        self._create_rule(rule='*luffy*@*.onepiece.com')
        # Email to test
        email = 'monkeyDluffy_king@pirate.onepiece.com'

        # Sign up
        res = self._sign_up(email=email, csrf_token=self._get_csrf_token())

        error = 'Your registration email was blacklisted and blocked by our administrations.' in str(res.content)
        self.assertTrue(
            error or res.headers.get('X-Frame-Options','').lower() == 'deny',
            "Sign up with email in blacklist should not be successful."
        )

    def test_15_test_domain_signup_error(self):
        """
            Input:
                rule:    discardmail.* (already existed as demo data)
                email:   test@discardmail.piratemail
        """
        # Email to test
        email = 'test@discardmail.spamformat'

        # Sign up
        res = self._sign_up(email=email, csrf_token=self._get_csrf_token())

        error = 'Your registration email was blacklisted and blocked by our administrations.' in str(res.content)
        self.assertTrue(
            error or res.headers.get('X-Frame-Options','').lower() == 'deny',
            "Sign up with email in blacklist should not be successful."
        )

    def test_16_test_domain_signup_error(self):
        """
            Input:
                rule:    *.onepiece.*
                email:   test@hello.onepiece.piratemail
        """
        # Create rule
        self._create_rule(rule='*.onepiece.*')
        # Email to test
        email = 'test@hello.onepiece.piratemail'

        # Sign up
        res = self._sign_up(email=email, csrf_token=self._get_csrf_token())

        error = 'Your registration email was blacklisted and blocked by our administrations.' in str(res.content)
        self.assertTrue(
            error or res.headers.get('X-Frame-Options','').lower() == 'deny',
            "Sign up with email in blacklist should not be successful."
        )
