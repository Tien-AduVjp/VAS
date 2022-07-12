import requests
from odoo import models


class SocialLinkedinApi(models.AbstractModel):
    _name = 'social.linkedin.api'
    _inherit = 'social.mixin'
    _description = 'Social Linkedin Api'

    def get_person_info(self, person_id, access_token):
        url = 'https://api.linkedin.com/v2/people/id=%s&?oauth2_access_token=%s' % (person_id, access_token)
        res = requests.get(url)
        self.raise_http_error(res, url)
        return res.json()

    def get_person_name(self, person_id, access_token):
        person_data = self.get_person_info(person_id, access_token)
        return person_data['localizedFirstName'] + person_data['localizedLastName']

    def get_page_info(self, organization_id, access_token):
        url = 'https://api.linkedin.com/v2/organizations/%s?oauth2_access_token=%s' % (organization_id, access_token)
        res = requests.get(url)
        self.raise_http_error(res, url)
        return res.json()

    def get_page_name(self, organization_id, access_token):
        return self.get_page_info(organization_id, access_token)['localizedName']
