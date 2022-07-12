import requests
from odoo import models, fields, _
from odoo.exceptions import AccessError


organizations = "https://api.linkedin.com/v2/organizations"
organizationalEntityAcls = "https://api.linkedin.com/v2/organizationalEntityAcls"
networkSizes = "https://api.linkedin.com/v2/networkSizes"
organizationPageStatistics = "https://api.linkedin.com/v2/organizationPageStatistics"
organizationalEntityShareStatistics = "https://api.linkedin.com/v2/organizationalEntityShareStatistics"
organizationShares = "https://api.linkedin.com/v2/shares"
ugcPosts = "https://api.linkedin.com/v2/ugcPosts"


class SocialPage(models.Model):
    _inherit = 'social.page'

    linkedin_page_urn = fields.Char(string="LinkedIn organization URN", readonly=True)
    linkedin_page_admin_urn = fields.Char(string="LinkedIn organization Admin", readonly=True)

    def action_sinchronized_posts(self):
        """
        Type : ugcPosst : include : article, images, videos
        """
        if self.media_id.social_provider != 'linkedin':
            return super(SocialPage, self).action_sinchronized_posts()

        # get all Post
        url = ugcPosts + "?q=authors&count=100&sortBy=CREATED&authors=List(urn%3Ali%3Aorganization%3A" + self.social_page_id + ")"
        headers = {
            'authorization': 'Bearer %s' % self.media_id.linkedin_access_token,
            'X-Restli-Protocol-Version': '2.0.0'
        }
        res = requests.get(url, headers=headers)
        self.raise_http_error(res, url)
        data_dict_json = res.json()

        post_list = data_dict_json.get('elements', False)
        if post_list:
            post_insights = self.env['social.post']._get_linkedin_post_insights(
                post_list,
                self.linkedin_page_urn,
                self.media_id.linkedin_access_token
            )
            self.env['social.post'].with_context(page_id=self.id)._update_linkedin_post_list(post_insights, self.id)
            return super(SocialPage, self).action_sinchronized_posts()

    def action_sinchronized_page(self):
        self.ensure_one()
        if self.media_id.social_provider != 'linkedin':
            return super(SocialPage, self).action_sinchronized_page()

        if self.env.user.has_group('viin_social.viin_social_group_editor'):
            self.media_id.sudo()._synchronized()
        else:
            raise AccessError("You have no rights to this action.")
        return super(SocialPage, self).action_sinchronized_page()

    def _update_linkedin_page_list(self, page_list, media_id):
        """ Create/update linkedin pages ('social.page') """
        social_pages = self.env['social.page'].with_context(active_test=False).search([('media_id', '=', media_id)])
        social_page_ids = social_pages.mapped('linkedin_page_urn')

        page_urn_new = []
        page_ids_create = []
        page_ids_update = []
        for page in page_list:
            page_urn_new.append(page['organizationalTarget'])
            data = self._prepare_linkedin_page_data(page)
            if page['organizationalTarget'] not in social_page_ids:
                data['media_id'] = self._context.get('media_id', False)
                page_ids_create.append(data)
            else:
                data['active'] = True
                page_ids_update.append(data)

        # Page list for Create
        if page_ids_create:
            self.env['social.page'].create(page_ids_create)

        # Page list for update
        for page in page_ids_update:
            page_update = social_pages.filtered(lambda r: r.linkedin_page_urn == page['linkedin_page_urn'])
            if page_update:
                page_update.write(page)

        # Page list for inactive
        pages_for_inactive = social_pages.filtered(lambda r: r.linkedin_page_urn not in page_urn_new)
        if pages_for_inactive:
            pages_for_inactive.write({'active': False})

    def _get_linkedin_page_full_info(self, social_page_urn, linkedin_access_token):
        """ Call the api to get the data of a linkedin page """
        page_id = social_page_urn.replace('urn:li:organization:', '')

        # Page Info
        name, description = self._get_linkedin_page_info(social_page_urn, linkedin_access_token)
        # Followers
        follower_count = self._get_linkedin_page_follower(social_page_urn, linkedin_access_token)
        # Views
        view_count = self._get_linkedin_page_views(social_page_urn, linkedin_access_token)
        # Interact page : likes, comments, shares, clicks
        click_count,like_count,comment_count,share_count = self._get_linkedin_page_interact(social_page_urn, linkedin_access_token)

        logo_url = self._get_linkedin_page_logo_url(page_id, linkedin_access_token)
        page_logo = False
        if logo_url:
            page_logo = self._read_image_from_url(logo_url)

        return {
            'name': name,
            'description': description,
            'follower_count': follower_count,
            'view_count': view_count,
            'click_count': click_count,
            'comment_count': comment_count,
            'like_count': like_count,
            'share_count': share_count,
            'image':  page_logo
        }

    def _get_linkedin_page_logo_url(self, page_id, linkedin_access_token):
        url = organizations + '/' + page_id + '?projection=(logoV2(original~:playableStreams))&oauth2_access_token=' + linkedin_access_token
        res = requests.get(url)
        self.raise_http_error(res, url)
        data = res.json()

        try:
            return data['logoV2']['original~']['elements'][0]['identifiers'][0]['identifier']
        except:
            return False

    def _get_linkedin_page_info(self, social_page_urn, linkedin_access_token):
        page_id = social_page_urn.replace('urn:li:organization:',"")
        url = organizations + "/" + page_id + "?oauth2_access_token=%s" % linkedin_access_token

        res = requests.get(url)
        self.raise_http_error(res, url)
        data_dict_json = res.json()

        name = description = "New"
        localized_name = data_dict_json['name']['localized']
        if localized_name.get('en_US', False):
            name = localized_name['en_US']
        localized_description = data_dict_json.get('description', {}).get('localized', {})
        if localized_description.get('en_US', False):
            description = localized_name['en_US']

        return name,description

    def _get_linkedin_page_follower(self, social_page_urn, linkedin_access_token):
        url = networkSizes + "/" + social_page_urn + "?edgeType=CompanyFollowedByMember&oauth2_access_token=%s" % linkedin_access_token

        res = requests.get(url)
        self.raise_http_error(res, url)
        data_dict_json = res.json()
        return data_dict_json.get('firstDegreeSize', False)

    def _get_linkedin_page_views(self, social_page_urn, linkedin_access_token):
        url = organizationPageStatistics + "?q=organization&organization=%s&oauth2_access_token=%s" \
                                            % (social_page_urn, linkedin_access_token)

        res = requests.get(url)
        self.raise_http_error(res, url)
        data_dict_json = res.json()

        all_page_views = False
        total_page_statistics = data_dict_json['elements'][0].get('totalPageStatistics', False)
        if total_page_statistics and total_page_statistics.get('view', False):
            all_page_views = total_page_statistics['view'].get('allPageViews', False)
        return all_page_views

    def _get_linkedin_page_interact(self, social_page_urn, linkedin_access_token):
        url = organizationalEntityShareStatistics + "?q=organizationalEntity&organizationalEntity=%s&oauth2_access_token=%s" \
                                                    % (social_page_urn, linkedin_access_token)
        res = requests.get(url)
        self.raise_http_error(res, url)
        data = res.json()

        click_count = like_count = comment_count = share_count = False
        total_share_statistics = data['elements'][0].get('totalShareStatistics', False)
        if total_share_statistics:
            click_count = total_share_statistics.get('clickCount', False)
            like_count = total_share_statistics.get('likeCount', False)
            comment_count = total_share_statistics.get('commentCount', False)
            share_count = total_share_statistics.get('shareCount', False)
        return click_count, like_count, comment_count, share_count

    def _prepare_linkedin_page_data(self, page):
        """ Select the necessary data to create/update 'social.page' from a page (data returned from linkedin)
            :param <dict> page: data of a page (from linkedin)
            :return <dict>: data to create/update 'social.page'
        """
        page_id = page['organizationalTarget'].replace('urn:li:organization:',"")
        return {
            'name': page['name'],
            'description': page['description'],
            'social_page_id': page_id,
            'linkedin_page_urn': page['organizationalTarget'],
            'linkedin_page_admin_urn': page['roleAssignee'],
            'follower_count': page['follower_count'],
            'engagement_count': page['like_count'] + page['comment_count'] + page['share_count'],
            'view_count': page['view_count'],
            'like_count': page['like_count'],
            'comment_count': page['comment_count'],
            'share_count': page['share_count'],
            'click_count': page['click_count'],
            'social_provider': 'linkedin',
            'social_page_url': "https://www.linkedin.com/company/%s" % page_id,
            'image': page['image']
        }
