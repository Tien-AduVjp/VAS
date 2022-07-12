from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessError
import requests
from datetime import datetime, timedelta
import werkzeug.utils

class MainController(http.Controller):
    @http.route('/linkedin_callback', type='http', auth='user')
    def get_access_token(self, **kwargs):
        code = kwargs.get('code',False)
        if code:
            domain = request.env['ir.config_parameter'].sudo().get_param('web.base.url').split("//")[1]
            grant_type = "grant_type=authorization_code"
            code = "&code=%s"%(code)
            client_id = "&client_id=%s"%(request.env.company.linkedin_app_id)
            redirect_uri = "&redirect_uri=" + "https://" + domain + "/linkedin_callback"
            client_secret = "&client_secret=%s"%(request.env.company.linkedin_client_secret)

            url = "https://www.linkedin.com/oauth/v2/accessToken?" + grant_type + code + client_id + redirect_uri + client_secret
            req = requests.post(url)  
            req.raise_for_status()
            data_dict_json = req.json()
            
            linkedin_access_token = data_dict_json.get('access_token', False)
            expires_in = data_dict_json.get('expires_in', False)
            linkedin_refresh_token = data_dict_json.get('refresh_token', False)
            refresh_token_expires_in = data_dict_json.get('refresh_token_expires_in', False)  
            date_end = datetime.now() + timedelta(seconds=expires_in)
            refresh_date_end = datetime.now() + timedelta(seconds=refresh_token_expires_in)
            
            Media = request.env['social.media'].search([('social_provider', '=', 'linkedin')])
            Media.write({'linkedin_access_token': linkedin_access_token,
                         'linkedin_refresh_token': linkedin_refresh_token,
                         'linkedin_date_expired' : date_end,
                         'linkedin_refresh_date_expired': refresh_date_end})
            Media._synchronized()
            url = '/web#action=%s'%(request.env.ref('viin_social.social_page_action').id)
            return werkzeug.utils.redirect(url)
        else:
            raise AccessError(_("Connection failed, please try again later"))
