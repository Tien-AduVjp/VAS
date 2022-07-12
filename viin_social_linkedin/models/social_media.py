import requests
from odoo import models, fields, _
from odoo.exceptions import UserError

organizationalEntityAcls = "https://api.linkedin.com/v2/organizationalEntityAcls"
authorization = "https://www.linkedin.com/oauth/v2/authorization"


class SocialMedia(models.Model):
    _inherit = 'social.media'

    social_provider = fields.Selection(selection_add=[('linkedin', 'LinkedIn')], ondelete={'linkedin': 'set default'})
    linkedin_access_token = fields.Text(string="LinkedIn Access Token", readonly=True)
    linkedin_refresh_token = fields.Text(string="LinkedIn Refresh Token", readonly=True)
    linkedin_refresh_date_expired = fields.Datetime(string="Refresh Expired Date",
                                                    help="Expiration date of refresh access token", readonly=True)
    linkedin_developer_application = fields.Char(string='Linkedin Developer Application ID',
                                                 help="Linkedin 'developerApplication'. Get the value from the url of "
                                                      "the app in the developer application portal")

    def action_link_account(self):
        self.ensure_one()
        if self.social_provider != 'linkedin':
            return super(SocialMedia, self).action_link_account()

        response_type = "?response_type=code"
        client_id = "&client_id=%s" % self.env.company.linkedin_app_id
        domain = self.get_base_url().split("//")[1]
        redirect_uri = "&redirect_uri=https://%s/linkedin_callback" % domain
        scope = "&scope=r_organization_social,r_emailaddress,rw_organization_admin,r_liteprofile,r_basicprofile," \
                "w_member_social,w_organization_social,r_1st_connections_size,r_ads_reporting,r_ads"

        url = authorization + response_type + client_id + redirect_uri + scope
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }

    def action_synchronized(self):
        """ Synchronize Linkedin pages data """
        self.ensure_one()
        if self.social_provider == 'linkedin' and not self.linkedin_access_token:
            raise UserError(_("Cannot sync because Linkedin Access Token has no value."))
        return super(SocialMedia, self).action_synchronized()

    def _synchronized(self):
        """ Synchronize Linkedin pages data """
        self.ensure_one()
        if self.social_provider != 'linkedin':
            return super(SocialMedia, self)._synchronized()

        url = organizationalEntityAcls + "?q=roleAssignee&role=ADMINISTRATOR&state=APPROVED&oauth2_access_token=%s" \
                                         % self.linkedin_access_token
        res = requests.get(url)
        self.raise_http_error(res, url)
        data_dict_json = res.json()
        page_list = data_dict_json.get('elements', False)

        if page_list:
            for page in page_list:
                page_info = self.env['social.page']._get_linkedin_page_full_info(page['organizationalTarget'], self.linkedin_access_token)
                page.update(page_info)
            self.env['social.page'].with_context(media_id=self.id)._update_linkedin_page_list(page_list, self.id)

    def _cron_synchronized_all_datas_linkedin(self):
        self.ensure_one()
        if not self.linkedin_access_token:
            raise UserError(_("Cannot sync because Linkedin Access Token has no value."))
        self._synchronized()

    def action_create_webhook_subscriptions_linkedin(self):
        self.ensure_one()
        if not self.linkedin_developer_application:
            raise UserError(_("You must enter a value for the 'Linkedin Developer Application ID' field first"))

        pages = self.env['social.page'].search([('social_provider', '=', 'linkedin')])
        for page in pages:
            linkedin_page_admin_urn = page.linkedin_page_admin_urn.replace(':', '%3A')
            linkedin_page_urn = page.linkedin_page_urn.replace(':', '%3A')
            linkedin_developer_application = 'urn%3Ali%3AdeveloperApplication%3A' + self.linkedin_developer_application

            url = 'https://api.linkedin.com/v2/eventSubscriptions/(developerApplication:%s,user:%s,entity:%s' \
                  ',eventType:ORGANIZATION_SOCIAL_ACTION_NOTIFICATIONS)?oauth2_access_token=%s' \
                  % (linkedin_developer_application, linkedin_page_admin_urn, linkedin_page_urn,
                     self.linkedin_access_token)
            headers = {
                'X-Restli-Protocol-Version': '2.0.0'
            }
            webhook_url = self.get_base_url() + '/linkedin_webhook'
            res = requests.put(url, headers=headers, json={'webhook': webhook_url})
            self.raise_http_error(res, url, body=webhook_url)

            res = requests.get(url, headers=headers)
            self.raise_http_error(res, url)
        return self.notify(message=_("Create webhook subscriptions successful."))
