from odoo import models, fields
import requests

organizationalEntityAcls = "https://api.linkedin.com/v2/organizationalEntityAcls"
authorization = "https://www.linkedin.com/oauth/v2/authorization"

class SocialMedia(models.Model):
    _inherit = 'social.media'

    social_provider = fields.Selection(selection_add=[('linkedin','LinkedIn')])
    linkedin_access_token = fields.Text(string="LinkedIn Access Token", readonly=True)
    linkedin_refresh_token = fields.Text(string="LinkedIn Refresh Token", readonly=True)
    # TODO: master/14+ move this `linkedin_date_expired` to the module `viin_social` and rename it into `token_expired_date`
    # so that it can be shared with multiple providers
    linkedin_date_expired = fields.Datetime(string="LinkedIn Token Expired Date", help="Expiration date of access token", readonly=True)
    linkedin_refresh_date_expired = fields.Datetime(string="Refresh Expired Date", help="Expiration date of refresh access token", readonly=True)

    def action_link_account(self):
        self.ensure_one()
        if self.social_provider == 'linkedin':
            response_type = "?response_type=code"
            client_id = "&client_id=%s"%(self.env.company.linkedin_app_id)
            domain = self.get_base_url().split("//")[1]
            redirect_uri = "&redirect_uri=https://%s/linkedin_callback"%domain
            scope = "&scope=r_organization_social,r_emailaddress,rw_organization_admin,r_liteprofile,r_basicprofile,w_member_social,w_organization_social,r_1st_connections_size,r_ads_reporting,r_ads"
   
            url = authorization + response_type + client_id + redirect_uri + scope
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new'
            }
        else:
            return super(SocialMedia, self).action_link_account()

    def _synchronized(self):
        self.ensure_one()
        if self.social_provider == 'linkedin':
            url = organizationalEntityAcls + "?q=roleAssignee&role=ADMINISTRATOR&state=APPROVED&oauth2_access_token=%s"%(self.linkedin_access_token)
            req = requests.get(url)
            req.raise_for_status()
            data_dict_json = req.json()
            page_list = data_dict_json.get('elements', False)
            
            social_page = self.env['social.page']
            if page_list:
                for page in page_list:
                    page_info = social_page._get_linkedin_page_full_info(page['organizationalTarget'], self.linkedin_access_token)
                    page.update(page_info)
                social_page.with_context(media_id=self.id)._update_linkedin_page_list(page_list, self.id)
        else:
            return super(SocialMedia, self)._synchronized()

    def _cron_synchronized_all_datas_linkedin(self):
        self._synchronized()
        pages = self.env['social.page'].search([])
        for page in pages:
            page.action_sinchronized_post()
