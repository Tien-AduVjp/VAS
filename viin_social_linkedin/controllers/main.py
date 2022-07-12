import hmac
import hashlib
import json

import requests
from datetime import datetime, timedelta
import werkzeug.utils

from odoo import http, _
from odoo.http import request, Response


class MainController(http.Controller):

    @http.route('/linkedin_callback', type='http', auth='user')
    def get_access_token(self, **kwargs):
        code = kwargs.get('code', False)
        if not code:
            return "Error: 'code' not found in request <br>Parameters:<br> %s" % kwargs

        domain = request.env['ir.config_parameter'].sudo().get_param('web.base.url').split("//")[1]
        grant_type = "grant_type=authorization_code"
        code = "&code=%s" % code
        client_id = "&client_id=%s" % request.env.company.linkedin_app_id
        redirect_uri = "&redirect_uri=" + "https://" + domain + "/linkedin_callback"
        client_secret = "&client_secret=%s" % request.env.company.linkedin_client_secret

        url = "https://www.linkedin.com/oauth/v2/accessToken?" + grant_type + code + client_id + redirect_uri + client_secret
        res = requests.post(url)
        data = res.json()
        if not res.ok:
            return "Error: <br> %s" % data

        linkedin_access_token = data.get('access_token', False)
        expires_in = data.get('expires_in', False)
        linkedin_refresh_token = data.get('refresh_token', False)
        refresh_token_expires_in = data.get('refresh_token_expires_in', False)
        date_end = datetime.now() + timedelta(seconds=expires_in)
        refresh_date_end = datetime.now() + timedelta(seconds=refresh_token_expires_in)

        Media = request.env['social.media'].search([('social_provider', '=', 'linkedin')])
        Media.write({
            'linkedin_access_token': linkedin_access_token,
            'linkedin_refresh_token': linkedin_refresh_token,
            'token_expired_date': date_end,
            'linkedin_refresh_date_expired': refresh_date_end
        })
        try:
            Media._synchronized()
            url = '/web#action=%s' % request.env.ref('viin_social.social_page_action').id
        except Exception as e:
            return str(e)
        return werkzeug.utils.redirect(url)

    @http.route('/linkedin_webhook', type='http', auth='public',  methods=['GET'])
    def verify_webhook_linkedin(self, **kwargs):
        print(kwargs)
        linkedin_client_secret = request.env.company.linkedin_client_secret
        challenge_code = kwargs.get('challengeCode', None)
        if challenge_code:
            return Response(json.dumps({
                'challengeCode': kwargs.get('challengeCode', None),
                'challengeResponse': hmac.new(linkedin_client_secret.encode(), challenge_code.encode(), hashlib.sha256).hexdigest()
            }), headers={"Content-Type": "application/json"}, status=200)


    @http.route('/linkedin_webhook', type='json', auth='public',  methods=['POST'])
    def get_data_webhook(self, **kwargs):
        data = request.jsonrequest
        linkedin_access_token = request.env.ref('viin_social_linkedin.social_media_linkedin').sudo().linkedin_access_token
        LinkedinApi = request.env['social.linkedin.api']

        social_notice_vals = []
        for n in data.get('notifications', []):
            if n['subscriber'] == 'urn:li:person:foo':
                return

            if n['action'] in ['COMMENT', 'ADMIN_COMMENT']:
                data = {
                    'linkedin_notification_id': n['notificationId'],
                    'type': 'comment',
                    'social_post_id': n['decoratedSourcePost']['entity'],
                    'social_page_id': n['decoratedSourcePost']['owner'].split(':')[-1],
                    'social_message': n['decoratedGeneratedActivity']['comment']['text'],
                }
                if n['action'] == 'COMMENT':
                    user_comment_id = n['decoratedGeneratedActivity']['comment']['owner'].split(':')[-1]
                    data.update({'social_user_name': LinkedinApi.get_person_name(user_comment_id, linkedin_access_token)})
                elif n['action'] == 'ADMIN_COMMENT':
                    organization_id = n['organizationalEntity'].split(':')[-1]
                    data.update({'social_user_name': LinkedinApi.get_page_name(organization_id, linkedin_access_token)})
                social_notice_vals.append(data)
            elif n['action'] == 'LIKE':
                social_notice_vals.append({
                    'linkedin_notification_id': n['notificationId'],
                    'type': 'reaction',
                    'reaction_type': 'like',
                    'social_user_name': _('A user'),  #Linkedin does not return id or name
                    'social_post_id': n['decoratedSourcePost']['entity'],
                    'social_page_id': n['decoratedSourcePost']['owner'].split(':')[-1]
                })

        request.env['social.notice'].sudo()._create_notice(social_notice_vals)
        return Response(status=200)
