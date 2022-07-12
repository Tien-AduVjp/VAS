from odoo import http
from odoo.http import request
from odoo.exceptions import AccessDenied


class ControllerMobileLogin(http.Controller):
    @http.route('/mobile/login', type='json', auth="none")
    def mobile_login(self, login, password):
        database = http.db_list(True)
        if database:
            try:
                request.session.authenticate(database[0], login, password)
                return database
            except AccessDenied as accessDenied:
                return 'null'
        else:
            return 'null'
