from odoo import models, fields, _
import requests
from datetime import datetime, timedelta
from odoo.exceptions import UserError


host = "https://graph.facebook.com"
authorize = "https://graph.facebook.com/oauth/authorize"
oauth_access_token = "https://graph.facebook.com/v9.0/oauth/access_token"
scope = "&scope=public_profile,email,pages_read_user_content,pages_manage_posts,pages_show_list,pages_manage_metadata,pages_manage_engagement,read_insights,pages_read_engagement,publish_video,pages_messaging"

class SocialMedia(models.Model):
    _inherit = 'social.media'

    social_provider = fields.Selection(selection_add=[('facebook','Facebook')])
    facebook_user_id = fields.Char(string="User Id of Facebook", readonly=True)
    facebook_access_token = fields.Text(string="User Access Token of Facebook", readonly=True)
    # TODO: master/14+ move this `facebook_date_expired` to the module `viin_social` and rename it into `token_expired_date`
    # so that it can be shared with multiple providers
    facebook_date_expired = fields.Datetime(string="Facebook Token Expired Date", help="Expiration date of access token", readonly=True)

    def action_link_account(self):
        self.ensure_one()
        domain = self.get_base_url().split("//")[1]
        if self.social_provider == 'facebook':
            response_type = "?response_type=code"
            client_id = "&client_id=%s"%(self.env.company.facebook_app_id)
            redirect_uri = "&redirect_uri=https://%s/facebook_callback_user_access_token"%domain   
            url = authorize + response_type + client_id + redirect_uri + scope
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new'
            }
        else:
            return super(SocialMedia, self).action_link_account()

    def _synchronized(self):
        self.ensure_one()
        if self.social_provider == 'facebook':
            url = host + "/%s/accounts?fields=id,name,about,description,picture,fan_count,access_token&access_token=%s"%(self.facebook_user_id, self.facebook_access_token)
            req = requests.get(url)
            req.raise_for_status()
            data_dict_json = req.json()
            page_list = data_dict_json.get('data', False)
            
            social_page = self.env['social.page']
            if page_list:
                for page in page_list:
                    page_info = social_page._get_facebook_page_engagement(page['id'], page['access_token'])
                    page.update(page_info)
                social_page.with_context(media_id=self.id)._update_facebook_page_list(page_list, self.id)
            social_page.search([('social_provider', '=', 'facebook')])._check_page_subscribed_apps()
        else: 
            return super(SocialMedia, self)._synchronized()

    def _fb_exchange_code(self, fb_exchange_code):
        """
        Convert code to Convert Short-lived Token
        """
        if fb_exchange_code:
            client_id = "?client_id=%s"%(self.env.company.facebook_app_id)
            client_secret = "&client_secret=%s"%(self.env.company.facebook_client_secret)
            domain = self.get_base_url().split("//")[1]
            redirect_uri = "&redirect_uri=https://%s/facebook_callback_user_access_token"%domain
            code = "&code=%s"%(fb_exchange_code)
            url = oauth_access_token + client_id + client_secret + redirect_uri + code
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()
            access_token = data.get('access_token', False)
            if access_token:
                self._fb_exchange_token(access_token)

    def _fb_exchange_token(self, fb_exchange_token):
        """
        Convert Short-lived Token to Long-lived Token
        """
        if fb_exchange_token:
            client_id = self.env.company.facebook_app_id
            client_secret = self.env.company.facebook_client_secret
            
            url1 = host + '/me?access_token=%s'%(fb_exchange_token)
            req = requests.get(url1)
            req.raise_for_status()
            user = req.json()
            user_id = user.get('id', False)
            url2 = host + '/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'%(client_id, client_secret, fb_exchange_token)
            req = requests.get(url2)
            req.raise_for_status()
            data_dict_json = req.json()
            if data_dict_json.get('token_type',False) == 'bearer':
                expires_in = 5180000 # ~60 days
                date_end = datetime.now() + timedelta(seconds=expires_in)
                self.write({
                        'facebook_user_id': user_id,
                        'facebook_access_token': data_dict_json.get('access_token',False),
                        'facebook_date_expired': date_end
                    })
        else:
            raise UserError(_("Short-lived Token is missing, please enter this field"))

    def _cron_synchronized_all_datas_facebook(self):
        self._synchronized()
