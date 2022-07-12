from odoo import http
from odoo.http import request
import json


class WebsiteRecaptcha(http.Controller):
    
    @http.route(
        '/website/recaptcha/',
        type='http',
        auth='public',
        methods=['POST'],
        website=True,
        multilang=False,
    )
    def recaptcha_public(self, **kw):
        recaptcha_model = request.env['website.recaptcha'].sudo()
        creds = recaptcha_model._get_api_credentials(
            kw.get('version', 'v2'),
            request.website
        )
        return json.dumps({
            'site_key': creds['site_key']
        })


    
