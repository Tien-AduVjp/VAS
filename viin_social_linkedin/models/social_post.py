from odoo import models, fields
import requests, json
from datetime import datetime

EntityShareStatistics = "https://api.linkedin.com/v2/organizationalEntityShareStatistics"
organizationShares = "https://api.linkedin.com/v2/shares"
ugcPosts = "https://api.linkedin.com/v2/ugcPosts"
assets = "https://api.linkedin.com/v2/assets"
HOST = "https://api.linkedin.com/v2"

class SocialPost(models.Model):
    _inherit = 'social.post'

    rate_engagement = fields.Float(string='Engagement Rate', digits=(4,2),readonly=True,
                                help="Rate of total likes, comments, shares, clicks compared to views")
    click_count = fields.Integer(string='Total Clicks', readonly=True)
    
    def _update_linkedin_post_list(self, post_list, page_id):
        social_posts = self.env['social.post'].with_context(active_test=False).search([('page_id', '=', page_id)])
        social_post_ids = social_posts.mapped('social_post_id')

        post_ids_new = []
        post_ids_create = []
        post_ids_update = []
        for post in post_list:
            post_ids_new.append(post['id'])
            data = self._prepare_linkedin_post_data(post)
            if post['id'] not in social_post_ids:
                data['page_id'] = self._context.get('page_id', False)
                post_ids_create.append(data)
            else:
                data['active'] = True
                post_ids_update.append(data)
         
        # Post list for Create
        if post_ids_create:
            self.env['social.post'].create(post_ids_create)
     
        # Post list for Update
        for post in post_ids_update:
            post_update = social_posts.filtered(lambda r:r.social_post_id == post['social_post_id'])
            if post_update:
                post_update.with_context(check_right=False).write(post)
 
        # Post list for inactive
        posts_for_inactive = social_posts.filtered(lambda r:r.social_post_id not in post_ids_new)
        if posts_for_inactive:
            posts_for_inactive.with_context(check_right=False).write({'active': False})


    def _get_linkedin_post_insights(self, post_list, page_urn, access_token):
        # shares : for text, link, images
        # ugcPost : for video
        post_list_params = []
        post_list_params_ugc = []
        index1 = index2 = 0
        shares_list = []
        ugcPost_list = []
        for post in post_list:
            if 'ugcPost' in post['id']:
                ugcPost_list.append(post)
                post_list_params_ugc.append("ugcPosts[%s]=%s"%(index1, post['id']))
                index1 += 1
            else:
                shares_list.append(post)
                post_list_params.append("shares[%s]=%s"%(index2, post['id']))
                index2 += 1
        str_params = '&'.join(post_list_params)
        str_params_ugc = '&'.join(post_list_params_ugc)
        
        # shares insights
        if shares_list:
            url = EntityShareStatistics + "?q=organizationalEntity&organizationalEntity=%s&%s&oauth2_access_token=%s"%(page_urn, str_params, access_token)
            req = requests.get(url)
            req.raise_for_status()
            data_dict_json = req.json()
            shares = data_dict_json.get('elements', False)
            if shares:              
                # the returned data list is sorted randomly
                for post in shares_list:
                    for share in shares:
                        if post['id'] == share['share']:
                            post.update({
                                'shareCount': share['totalShareStatistics']['shareCount'],
                                'likeCount': share['totalShareStatistics']['likeCount'],
                                'commentCount': share['totalShareStatistics']['commentCount'],
                                'impressionCount': share['totalShareStatistics']['impressionCount'],    # views
                                'engagement': share['totalShareStatistics']['engagement'],              # rate
                                'clickCount': share['totalShareStatistics']['clickCount'],
                                })
                            shares.remove(share)
                            break
        
        # ugcPost insights
        if ugcPost_list:
            url = EntityShareStatistics + "?q=organizationalEntity&organizationalEntity=%s&%s&oauth2_access_token=%s"%(page_urn, str_params_ugc, access_token)
            req = requests.get(url)
            req.raise_for_status()
            data_dict_json = req.json()
            ugcposts = data_dict_json.get('elements', False)
            if ugcposts:
                # the returned data list is sorted randomly
                for post in ugcPost_list:
                    for ugcpost in ugcposts:
                        if post['id'] == ugcpost['ugcPost']:
                            post.update({
                                'shareCount': ugcpost['totalShareStatistics']['shareCount'],
                                'likeCount': ugcpost['totalShareStatistics']['likeCount'],
                                'commentCount': ugcpost['totalShareStatistics']['commentCount'],
                                'impressionCount': ugcpost['totalShareStatistics']['impressionCount'],    # views
                                'engagement': ugcpost['totalShareStatistics']['engagement'],              # rate
                                'clickCount': ugcpost['totalShareStatistics']['clickCount'],
                                })
                            ugcposts.remove(ugcpost)
                            break
        post_list = shares_list + ugcPost_list
        return post_list

    def _prepare_linkedin_post_data(self, post):
        attachment_link = False
        attachment_link_title = False
        shares_content = post['specificContent']['com.linkedin.ugc.ShareContent']
        if shares_content.get('media', False):
            if shares_content.get('shareMediaCategory', False) == 'IMAGE':
                pass
            elif shares_content.get('shareMediaCategory', False) == 'ARTICLE':
                attachment_data = shares_content['media'][0]
                attachment_link = attachment_data.get('originalUrl', False)
                attachment_link_title = attachment_data.get('title', {}).get('text', False) or attachment_data.get('description', {}).get('text', False)
            
        date_posted_timestamp = post['created']['time']
        date_posted = datetime.fromtimestamp(int(date_posted_timestamp/1000))
        return {
                'social_post_id': post['id'],
                'social_post_url': "https://www.linkedin.com/feed/update/%s"%(post['id']),
                'message': shares_content['shareCommentary']['text'],
                'likes_count': post.get('likeCount', 0),
                'comments_count': post.get('commentCount', 0),
                'shares_count': post.get('shareCount', 0),
                'views_count': post.get('impressionCount', 0),
                'rate_engagement': post.get('engagement', 0) * 100,
                'click_count': post.get('clickCount', 0),
                'attachment_link': attachment_link,
                'attachment_link_title': attachment_link_title,
                'state': 'posted',
                'date_posted': date_posted
                }

    def _post_article(self):
        if self.media_id.social_provider == 'linkedin':
            message = self.message
            url = organizationShares + "?oauth2_access_token=%s"%(self.media_id.linkedin_access_token)
            data={
                "distribution": { # Required
                    "linkedInDistributionTarget": {}
                    },
                "owner": self.page_id.linkedin_page_urn,
                "subject": "Text-Article",
                "text": {
                    "text": message
                    }
                }
            if self.attachment_link:
                value_link = {"content": {
                                "contentEntities": [
                                {
                                    "entityLocation": self.attachment_link,
                                }]
                                }
                            }
                if self.attachment_link_title:
                    value_link['content']['title'] = self.attachment_link_title
                data.update(value_link)
            req = requests.post(url, json=data)
            req.raise_for_status()
            data = req.json()
            if data:
                self._update_post_linkedin(data)
        else:
            return super(SocialPost, self)._post_article()

    def _update_post_linkedin(self, data, is_video=False):
            update_post = {}
            if is_video:
                url = "https://www.linkedin.com/feed/update/%s"%(data['id'])
                update_post = self._prepare_data_after_post(data['id'], url)
            else:
                url = "https://www.linkedin.com/feed/update/%s"%(data['activity'])
                update_post = self._prepare_data_after_post("urn:li:share:%s"%(data['id']), url)
            self.write(update_post)

    def _post_file(self):
        if self.media_id.social_provider == 'linkedin':
            path_list, is_video = self._get_path_list()
            self._post_article_images(self.message, path_list, self.media_id.linkedin_access_token, is_video)
        else:
            return super(SocialPost, self)._post_file()
    
    """
    Get full path of image
    """
    def _get_path_list(self):
        path_list = []
        is_video = False
        for file in self.attachment_ids:
            path_list.append(file._full_path(file.store_fname))
            if file.mimetype == 'video/mp4':
                is_video = True
        return path_list, is_video

    def _post_article_images(self, message, path_list, access_token, is_video):
        media_asset_list = []
        for path in path_list:
            media_asset = self._registerUpload(path, access_token, is_video)
            media_asset_list.append(media_asset)
        if media_asset_list:
            if is_video:
                self._post_text_video(message, media_asset_list[0], access_token)
            else:
                self._post_text_image(message, media_asset_list, access_token)

    """
    Register to allow uploading photos and videos to linkdein.
    Different values are returned each call
    """
    def _registerUpload(self, path, access_token, is_video):
        url = assets + "?action=registerUpload&oauth2_access_token=%s"%(access_token)
        data = {
            "registerUploadRequest": {
                "owner": self.page_id.linkedin_page_urn,
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "serviceRelationships": [{
                        "identifier": "urn:li:userGeneratedContent",
                        "relationshipType": "OWNER"
                    }]
                }
            }
        if is_video:
            data['registerUploadRequest']['recipes'] = ["urn:li:digitalmediaRecipe:feedshare-video"]
        
        req = requests.post(url, json=data)
        req.raise_for_status()
        data_dict_json = req.json()
        value = data_dict_json.get('value', False)
        if value:
            uploadUrl = value['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
            mediaAsset = value['asset']
            if is_video:
                self._upload_video(uploadUrl, path)
            else:
                self._upload_image(uploadUrl, path, access_token)
            return mediaAsset

    def _upload_image(self, uploadUrl, path, access_token):
        url = uploadUrl
        data = open(path, 'rb')
        headers = {'authorization': 'Bearer %s'%(access_token)}
        req = requests.put(url, data=data, headers=headers)
        req.raise_for_status()

    def _upload_video(self, uploadUrl, path):
        url = uploadUrl
        data = open(path, 'rb')
        headers = {'Content-Type': 'application/octet-stream'}
        req = requests.put(url, data=data, headers=headers)
        req.raise_for_status()

    def _post_text_image(self, message, media_asset_list, access_token):
        if media_asset_list:
            # image list
            contentEntities = []
            for media_asset in media_asset_list:
                contentEntities.append({"entity": media_asset})

            url = organizationShares + "?oauth2_access_token=%s"%(access_token)
            data={
                "distribution": { # Required
                    "linkedInDistributionTarget": {}
                    },
                "owner": self.page_id.linkedin_page_urn,
                "subject": "Post: content with image",
                "text": {
                    "text": message
                    },
                "content": {
                    "contentEntities": contentEntities,
                    "title": "IMAGE",
                    "shareMediaCategory": "IMAGE"
                    }
                }
            req = requests.post(url, json=data)
            req.raise_for_status()
            data = req.json()
            if data:
                self._update_post_linkedin(data)
    
    def _post_text_video(self, message, media_asset, access_token):  
            url = ugcPosts + "?oauth2_access_token=%s"%(access_token)
            data={
                "author": self.page_id.linkedin_page_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent":{
                    "com.linkedin.ugc.ShareContent": {
                        "media": [{
                                "media": media_asset,
                                "status": "READY",
                                "title": {
                                    "attributes": [],
                                    "text": ""} # video title
                                }],
                        "shareCommentary": {
                            "attributes": [],
                            "text": message},
                        "shareMediaCategory": "VIDEO"}
                    },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                    }
                }
            req = requests.post(url, json=data)
            req.raise_for_status()
            data = req.json()
            if data:
                self._update_post_linkedin(data, is_video=True)

    def _delete_post_social(self):
        if self.media_id.social_provider == 'linkedin':
            url = ugcPosts + "/%s?oauth2_access_token=%s"%(self.social_post_id, self.media_id.linkedin_access_token)
            req = requests.delete(url)
            req.raise_for_status()
        else:
            return super(SocialPost, self)._delete_post_social()

#     def _reshare(self):
    #     """
    #     TEST: oke
    #     - Feature : Reshare this post.
    #     - Developed later
    #     """
#         url = organizationShares + "?oauth2_access_token=%s"%(self.media_id.linkedin_access_token)
#         data={
#             "distribution": {
#                 "linkedInDistributionTarget": {}
#                 },
#             "originalShare": "urn:li:share:6742294367530164224",
#             "resharedShare": "urn:li:share:6742294367530164224",
#             "text": {
#                 "text": "Test Reshare!"
#                     },
#             "owner": self.linkedin_page_urn
#             }
#         req = requests.post(url, json=data)
#         req.raise_for_status()
#         data_dict_json = req.json()

    def _get_post_comments_linkedin(self, post_or_comment_urn, comment_type=False):
        data = []
        access_token = self.media_id.linkedin_access_token
        if post_or_comment_urn and access_token:
            url = HOST + "/socialActions/%s/comments?projection=(elements(*(*,actor~(*,profilePicture(displayImage~:playableStreams)))))&oauth2_access_token=%s"%(post_or_comment_urn, access_token)
            try:
                req = requests.get(url)
                req.raise_for_status()
                data_dict_json = req.json()
                elements = data_dict_json.get('elements', False)
                for element in elements:
                    comment = {}
                    comment['id'] = element.get('$URN', False)
                    author_name = 'Commenter'
                    if element.get('actor~', False) and element.get('actor~', False).get('localizedName', False):
                        author_name = element.get('actor~', False).get('localizedName', False)
                    if element.get('actor~', False) and element.get('actor~', False).get('localizedFirstName', False) and element.get('actor~', False).get('localizedLastName', False):
                        author_name = element.get('actor~', False).get('localizedFirstName', False) + " " + element.get('actor~', False).get('localizedLastName', False)
                    comment.update({
                        'from': {
                            'author_urn': element.get('actor', False),
                            'name': author_name}})
                    date_comment = element.get('lastModified', False) and element.get('lastModified', False).get('time', False)
                    if date_comment:
                        date_comment = datetime.fromtimestamp(int(date_comment/1000))
                        date_comment = self._set_datetime(date_comment)
                        comment['created_time'] = date_comment
                    comment['message'] = element.get('message', False) and element.get('message', False).get('text', False)
                    like_count = element.get('likesSummary', False) and element.get('likesSummary', False).get('totalLikes', False)
                    comment['like_count'] = like_count or 0
                    comment_count = element.get('commentsSummary', False) and element.get('commentsSummary', False).get('totalFirstLevelComments', False)
                    comment['comment_count'] = comment_count or 0
                    attachment = element.get('content', False)
                    if attachment:
                        attachment_type = attachment[0].get('type', False)
                        if attachment_type and attachment_type == 'IMAGE':
                            comment.update({'attachment': {
                                'type': 'photo',
                                'src': attachment[0].get('url', False)
                                }})
                    data.append(comment)
            except requests.HTTPError:
                data = data
        return data

    def _add_comment_linkedin(self, comment_messsage, comment_urn=False):
        self.ensure_one()
        self._check_right_comment()
        data = False
        access_token = self.media_id.linkedin_access_token
        post_urn = self.social_post_id
        if post_urn and comment_messsage:
            url = HOST + "/socialActions/%s/comments?oauth2_access_token=%s"%(post_urn, access_token)
            request_data = {"actor": self.page_id.linkedin_page_urn,
                            "object":post_urn,
                            "message":{
                                "text":comment_messsage
                                }
                            }
            if comment_urn:
                request_data.update({
                    'parentComment': comment_urn})
            req = requests.post(url,
                data=json.dumps(request_data))
            req.raise_for_status()
            data = req.json()
            data = data.get('$URN',False)
        return data

    def _like_comment_linkedin(self, comment_urn):
        self.ensure_one()
        self._check_right_comment()
        success_like = False
        post_urn = self.social_post_id
        access_token = self.media_id.linkedin_access_token
        if post_urn and access_token:
            url = HOST + "/socialActions/%s/likes?oauth2_access_token=%s"%(comment_urn, access_token)
            request_data = {"actor": self.page_id.linkedin_page_urn,
                            "object":post_urn
                            }
            try:
                req = requests.post(url,
                    data=json.dumps(request_data))
                req.raise_for_status()
                data = req.json()
                if data.get('$URN', False):
                    success_like = True
            except requests.HTTPError:
                success_like = False
        return success_like

    def _unlike_comment_linkedin(self, comment_urn):
        self.ensure_one()
        self._check_right_comment()
        success_unlike = True
        page_urn = self.page_id.linkedin_page_urn
        access_token = self.media_id.linkedin_access_token
        if comment_urn and access_token:
            url = HOST + "/socialActions/%s/likes/%s?actor=%s&oauth2_access_token=%s"%(comment_urn, page_urn, page_urn, access_token)
            try:
                req = requests.delete(url)
                req.raise_for_status()
                try:
                    data = False
                    data = req.json()
                    if data and data.get('message', False):
                        success_unlike = False
                except:
                    success_unlike = True
            except:
                success_unlike = False
        return success_unlike

    def _delete_comment_linkedin(self, comment_urn):
        self.ensure_one()
        self._check_right_comment()
        success_delete_comment = True
        page_urn = self.page_id.linkedin_page_urn
        post_urn = self.social_post_id
        access_token = self.media_id.linkedin_access_token
        comma_postition = comment_urn.find(',')
        comment_id = comment_urn[comma_postition + 1:-1]
        if comment_id and page_urn and post_urn and access_token:
            url = HOST + "/socialActions/%s/comments/%s?actor=%s&oauth2_access_token=%s"%(post_urn, comment_id, page_urn, access_token)
            try:
                req = requests.delete(url)
                req.raise_for_status()
                try:
                    data = False
                    data = req.json()
                    if data and data.get('message', False):
                        success_delete_comment = False
                except:
                    success_delete_comment = True
            except:
                success_delete_comment = False
        return success_delete_comment

    def _update_post_engagement_linkedin(self):
        self.ensure_one()
        post_list = [{'id': self.social_post_id}]
        access_token = self.media_id.linkedin_access_token
        page_urn = self.page_id.linkedin_page_urn
        engagement = self._get_linkedin_post_insights(post_list, page_urn, access_token)
        if engagement:
            likes_count = engagement[0].get('likeCount', False) or self.likes_count
            comments_count = engagement[0].get('commentCount', False) or self.comments_count
            shares_count = engagement[0].get('shareCount', False) or self.shares_count
            self.write({
                'likes_count': likes_count,
                'comments_count': comments_count,
                'shares_count': shares_count
                })
        return {'comments_count': self.comments_count,
                'likes_count': self.likes_count,
                'shares_count': self.shares_count}

    def _get_post_attachment_linkedin(self):
        attachments = []
        access_token = self.media_id.linkedin_access_token
        post_urn = self.social_post_id
        if post_urn and access_token:
            url = HOST + "/ugcPosts/%s?oauth2_access_token=%s"%(post_urn, access_token)
            try:
                req = requests.get(url)
                req.raise_for_status()
                data = req.json()
                ShareContent = data.get('specificContent', {}).get('com.linkedin.ugc.ShareContent', False)
                if ShareContent:
                    if ShareContent.get('shareMediaCategory', False) == 'IMAGE':
                        medias = ShareContent.get('media', False)
                        if medias:
                            for media in medias:
                                attachments.append({
                                    'type': 'photo',
                                    'src': media.get('originalUrl', False),
                                    })
            except requests.HTTPError:
                attachments = []
        return attachments
