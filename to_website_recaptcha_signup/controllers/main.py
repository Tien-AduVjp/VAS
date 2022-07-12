from odoo import http, _
from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class AuthSignupHome(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        if request.httprequest.method == 'POST':
            recaptcha_model = request.env['website.recaptcha'].sudo()
            validated = recaptcha_model.validate_request()
            if not validated:
                qcontext = self.get_auth_signup_qcontext()
                qcontext['error'] = _("Please check the recaptcha.")
                response = request.render('auth_signup.signup', qcontext)
                response.headers['X-Frame-Options'] = 'DENY'
                return response
        return super(AuthSignupHome, self).web_auth_signup(*args, **kw)
