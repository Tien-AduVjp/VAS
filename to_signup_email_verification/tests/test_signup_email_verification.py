from lxml import html
from unittest.mock import patch

import odoo
from odoo.tests import HttpCase, tagged


def _send_mail_fake(self, res_id, force_send=False, raise_exception=False, email_values=None, notif_layout=False):
    return 1


@tagged('post_install', '-at_install')
class TestSignUpEmailVerification(HttpCase):

    def setUp(self):
        super(TestSignUpEmailVerification, self).setUp()
        self.ensure_free_signup_enabled()

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.signup_url = base_url + '/web/signup'

        res_base = self.opener.get(base_url)
        dom_base = html.fromstring(res_base.content)
        csrf_token = dom_base.xpath("//script[@id='web.layout.odooscript']")[0].\
                        text_content().split()[5].replace(',', '').replace('"', '')

        self.data_user = {
            'name': 'Test User',
            'login': '',
            'password': '',
            'csrf_token': csrf_token
        }

    def ensure_free_signup_enabled(self):
        """
        When website and its related modules are installed, free signup may not be enabled
        This method ensure free signup is allowed
        """
        self.env['res.config.settings'].create({
            'auth_signup_uninvited': 'b2c',  # free sign up
        }).execute()

    @patch.object(odoo.addons.mail.models.mail_template.MailTemplate, 'send_mail', _send_mail_fake)
    def test_signup_with_invalid_email(self):
        self.data_user['login'] = 'invalid_email_example'
        res_signup = self.opener.post(self.signup_url, data=self.data_user)
        dom_signup = html.fromstring(res_signup.content)

        actual_msg = dom_signup.xpath("//p[@role='alert']")[0].text.strip()
        expect_msg = 'Please enter a valid email address which will be used to activate your account later.'
        self.assertEqual(actual_msg, expect_msg, 'Test email already exists failed.')

    @patch.object(odoo.addons.mail.models.mail_template.MailTemplate, 'send_mail', _send_mail_fake)
    def test_signup_with_exist_email(self):
        self.env['res.users'].with_context({'no_reset_password': True}).create({
            'name': 'Test User',
            'login': 'email_already_exists@example.viindoo.com',
            'email': 'email_already_exists@example.viindoo.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })
        self.data_user['login'] = 'email_already_exists@example.viindoo.com'
        res_signup = self.opener.post(self.signup_url, data=self.data_user)
        dom_signup = html.fromstring(res_signup.content)

        actual_msg = dom_signup.xpath("//p[@role='alert']")[0].text.strip()
        expect_msg = 'This email address has been registered. Please choose another one.'
        self.assertEqual(actual_msg, expect_msg, 'Test email already exists failed.')

    @patch.object(odoo.addons.mail.models.mail_template.MailTemplate, 'send_mail', _send_mail_fake)
    def test_signup_with_valid_email(self):
        self.data_user['login'] = 'test12345@example.viindoo.com'
        res_signup = self.opener.post(self.signup_url, data=self.data_user)
        dom_signup = html.fromstring(res_signup.content)

        actual_msg = dom_signup.xpath("//p[@role='status']")[0].text.strip()
        expect_msg = 'Registration completed. Please check your inbox to activate your account.'
        self.assertEqual(actual_msg, expect_msg, 'Test valid email failed.')

    def test_signup_with_invalid_email_and_password(self):
        self.data_user['login'] = 'invalid'
        self.data_user['password'] = '123'
        self.data_user['confirm_password'] = '123'
        res_signup = self.opener.post(self.signup_url, data=self.data_user)
        user = self.env['res.users'].search([('login', '=', 'invalid')])
        self.assertFalse(user)
