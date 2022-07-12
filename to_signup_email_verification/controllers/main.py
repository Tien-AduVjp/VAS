import logging
import validators

from odoo import _
from odoo.http import request, route
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.exceptions import UserError
from odoo.addons.base.models.ir_mail_server import MailDeliveryException

_logger = logging.getLogger(__name__)


class VerifyEmail(AuthSignupHome):

    @route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            values = request.params
            login = values.get('login', '')
            password = values.get('password', '')
            if login:
                # Validate email
                email_valid = validators.email(login)
                if not email_valid:
                    qcontext["error"] = _("Please enter a valid email address which will be used to activate your account later.")
                    return request.render("auth_signup.signup", qcontext)
                # Check if user email exist
                if request.env["res.users"].sudo().search([('login', '=', login)]):
                    qcontext["error"] = _("This email address has been registered. Please choose another one.")
                    return request.render("auth_signup.signup", qcontext)

            if login and not password:
                # Prepare values
                if not values.get("email"):
                    values["email"] = login
                values['lang'] = request.lang.code

                # Signup user
                try:
                    SudoUsers = request.env["res.users"].with_context(create_user=True).sudo()
                    for k in values.copy():
                        if not hasattr(SudoUsers, k):
                            values.pop(k, None)

                    SudoUsers.signup(values, qcontext.get("token"))
                    SudoUsers.reset_password(values.get("login"))
                    qcontext["message"] = _("Registration completed. Please check your inbox to activate your account.")
                    return request.render("auth_signup.reset_password", qcontext)
                except UserError as error:
                    qcontext["error"] = error.args[0]
                    return request.render("auth_signup.signup", qcontext)
                except MailDeliveryException as error:
                    _logger.exception(error)
                    qcontext["error"] = "%s %s" % (
                        error.args[0],
                        _("Please try again later or report this issue to our administrators as this could be a server error.")
                        )
                    return request.render("auth_signup.signup", qcontext)
                except Exception as error:
                    _logger.exception(error)
                    qcontext["error"] = _("Something went wrong, please try again later or contact us.")
                    return request.render("auth_signup.signup", qcontext)

        return super(VerifyEmail, self).web_auth_signup(*args, **kw)
