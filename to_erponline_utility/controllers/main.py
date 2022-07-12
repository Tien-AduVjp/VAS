from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied


class LoginAuth(http.Controller):
    @http.route('/web/default-login', type='http', auth='none')
    def default_login(self, **kwargs):
        try:
            # auto login with user and password is admin
            request.session.authenticate(request.session.db, 'admin', 'admin')
            return http.redirect_with_hash('/web')
        except AccessDenied as e:
            return http.redirect_with_hash('/web/login')
