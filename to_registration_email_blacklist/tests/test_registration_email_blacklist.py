from odoo.tests import tagged
from .common import TestSignUpCommon


@tagged('post_install', '-at_install')
class TestSignUp(TestSignUpCommon):

    def test_02_signup_error(self):
        """
            Test sign up email in blacklisted
        """
        # Email to test
        email = 'example@75hosting.com'

        rule = self.env['email.blacklist.rule'].search([('name', '=', '75hosting.com')], limit=1)
        self.assertTrue(bool(rule), "Domain email not in blacklist")

        # Sign up
        res = self._sign_up(email=email, csrf_token=self._get_csrf_token())

        error = 'Your registration email was blacklisted and blocked by our administrations.' in str(res.content)
        self.assertTrue(
            error or res.headers.get('X-Frame-Options','').lower() == 'deny',
            "Sign up with email in blacklist should not be successful."
        )

    def test_03_signup_success(self):
        """
            Test domain email not in blacklist
        """
        # Email to test
        email = 'example@example.viindoo.com'

        rule = self.env['email.blacklist.rule'].search([('name', '=', 'gmail.com')], limit=1)
        self.assertFalse(bool(rule), "Domain email in blacklist")

        # Test overlap email
        login = self.env['res.users'].search([('login', '=', email)], limit=1)
        self.assertFalse(bool(login), "Sign up with email already exists")

        # Sign up
        res = self._sign_up(email=email, csrf_token=self._get_csrf_token())

        error = 'Your registration email was blacklisted and blocked by our administrations.' not in str(res.content)

        self.assertTrue(error, "Sign up with email not in blacklist should be successful.")
