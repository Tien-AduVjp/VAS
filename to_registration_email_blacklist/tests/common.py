from lxml import html

from odoo.tests import HttpCase


class TestSignUpCommon(HttpCase):

    def setUp(self):
        super(TestSignUpCommon, self).setUp()
        self.env['ir.config_parameter'].sudo().set_param('block_blacklisted_registration_emails', True)
        self.ensure_free_signup_enabled()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.signup_url = base_url + '/web/signup'

    def ensure_free_signup_enabled(self):
        """
        When website and its related modules are installed, free signup may not be enabled
        This method ensure free signup is allowed
        """
        self.env['res.config.settings'].create({
            'auth_signup_uninvited': 'b2c',  # free sign up
        }).execute()

    def _prepare_signup_vals(self, email, csrf_token):
        return {'login': email,
                'name': 'Example 2',
                'password': '123456789',
                'confirm_password': '123456789',
                'csrf_token': csrf_token,
                }

    def _get_csrf_token(self):
        res = self.opener.get(self.signup_url)
        dom = html.fromstring(res.content)
        csrf_token = dom.xpath("//input[@name='csrf_token']")[0].value

        return csrf_token

    def _sign_up(self, email, csrf_token):
        data = self._prepare_signup_vals(email, csrf_token)
        res = self.opener.post(self.signup_url, data=data)

        return res
