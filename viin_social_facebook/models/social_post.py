from urllib.parse import urlencode

from odoo import models, fields, _
import requests
import datetime
from dateutil.parser import parse
from odoo.exceptions import UserError

HOST = "https://graph.facebook.com"

class SocialPost(models.Model):
    _inherit = 'social.post'
    
    schedule_later = fields.Boolean(related='article_id.schedule_later')
    schedule_date = fields.Datetime(related='article_id.schedule_date')
    
    def _update_facebook_post_list(self, post_list, page_id):
        social_posts = self.env['social.post'].with_context(active_test=False).search([('page_id', '=', page_id)])
        social_post_ids = social_posts.mapped('social_post_id')

        post_ids_new = []
        post_ids_create = []
        post_ids_update = []
        for post in post_list:
            post_ids_new.append(post['id'])
            data = self._prepare_facebook_post_data(post)
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
                post_update.with_context(check_right=False,fields_noupdate=True).write(post)

        # Post list for inactive
        posts_for_inactive = social_posts.filtered(lambda r:r.social_post_id not in post_ids_new)
        if posts_for_inactive:
            posts_for_inactive.with_context(check_right=False).write({'active': False})


    def _get_facebook_post_insights(self, post_id, page_access_token):
        url = HOST + "/%s?fields=likes.summary(1),shares,comments.filter(stream).limit(1000000).summary(1)&access_token=%s"%(post_id, page_access_token)
        req = requests.get(url)
        req.raise_for_status()
        data_dict_json = req.json()
        like_data = data_dict_json.get('likes', False) and data_dict_json.get('likes', False).get('summary', False)
        total_likes = like_data and like_data.get('total_count', False)
        comment_data = data_dict_json.get('comments', False) and data_dict_json.get('comments', False).get('summary', False)
        total_comments = comment_data and comment_data.get('total_count', False)
        share_data = data_dict_json.get('shares', False)
        total_shares = share_data and share_data.get('count', False)
        return {'total_likes': total_likes,
                'total_comments': total_comments,
                'total_shares': total_shares
                }
    
    def _prepare_facebook_post_data(self, post):
        date_posted = parse(post['created_time'])
        date_posted = datetime.datetime.combine(date_posted.date(), date_posted.time())
        state = 'scheduled' if post.get('is_schesdule_later', False) else 'posted'
        attachment = post.get('attachments', {}).get('data', False)
        attachment_link = attachment[0].get('url', False) if attachment and attachment[0].get('type', '') == 'share' else False
        attachment_link_title = attachment[0].get('title', False) if attachment and attachment[0].get('type', '') == 'share' else False
        
        like_data = post.get('likes', False) and post.get('likes', False).get('summary', False)
        total_likes = like_data and like_data.get('total_count', False) or 0
        comment_data = post.get('comments', False) and post.get('comments', False).get('summary', False) or 0
        total_comments = comment_data and comment_data.get('total_count', False)
        share_data = post.get('shares', False)
        total_shares = share_data and share_data.get('count', False) or 0
        
        return {
                'social_post_id': post['id'],
                'social_post_url': post.get('permalink_url', False),
                'message': post.get('message', False),
                'likes_count': total_likes,
                'comments_count': total_comments,
                'shares_count': total_shares,
                'state': state,
                'date_posted': date_posted,
                'attachment_link': attachment_link,
                'attachment_link_title': attachment_link_title
            }

    def _post_article(self):
        self.ensure_one()
        if self.media_id.social_provider == 'facebook':
            params = {'access_token': self.page_id.facebook_page_access_token,'message': self.message, 'link':self.attachment_link if self.attachment_link else ""}
            if self.schedule_later:
                self._check_schedule_date()
                timestamp = self._datetime_to_timestamp(self.schedule_date)
                params.update({'scheduled_publish_time': timestamp, 'published': 'false'})
            url = HOST + "/%s/feed"%self.page_id.social_page_id
            req = requests.post(url, params=params)
            req.raise_for_status()
            data = req.json()
            if data:
                page_post = data['id'].split("_")
                url = "https://www.facebook.com/permalink.php?story_fbid=%s&id=%s"%(page_post[1], page_post[0])
                update_post = self._prepare_data_after_post(data['id'], url)
                if self.schedule_later:
                    update_post['state'] = 'scheduled'
                    update_post['date_posted'] = self.schedule_date
                self.write(update_post)
        else:
            return super(SocialPost, self)._post_article()
    
    def _check_schedule_date(self):
        self.ensure_one()
        dt_now = datetime.datetime.now()
        dt_scheduled = self.schedule_date
        timedelta = dt_scheduled - dt_now
        seconds = int(timedelta.total_seconds())
        # [1 hour : 70 days]
        if seconds < 3600 or seconds > 6048000:
            tz = self.env.user.tz
            dt_scheduled = self.env['to.base'].convert_utc_time_to_tz(dt_scheduled, tz_name=tz)
            dt_scheduled = dt_scheduled.strftime("%x %X")
            raise UserError(_("You need to schedule the post within the next 1 hour to 70 days (%s)")%(dt_scheduled))
    
    def _datetime_to_timestamp(self, date_time):
        return datetime.datetime.timestamp(date_time)

        
    def _post_file(self):
        self.ensure_one()
        if self.media_id.social_provider == 'facebook':
            url_list = self._get_url_image_list()
            image_ids = self._upload_images_facebook(url_list)
            self._post_article_images_facebook(image_ids)
        else:
            return super(SocialPost, self)._post_file()

    def _get_url_image_list(self):
        self.ensure_one()
        url_list = []
        for attachment in self.attachment_ids:
            base_url = attachment.get_base_url()
            address_image = '/web/image/%s'%(attachment.id)
            url_list.append(base_url + address_image)
        return url_list

    def _upload_images_facebook(self, url_list):
        self.ensure_one()
        image_ids = []
        for image_url in url_list:
            url = HOST + "/%s/photos?url=%s&published=false&temporary=true&access_token=%s"%(self.page_id.social_page_id, image_url, self.page_id.facebook_page_access_token)
            req = requests.post(url)
            req.raise_for_status()
            data_dict_json = req.json()
            image_id = data_dict_json.get('id', False)
            if image_id:
                image_ids.append(image_id)
        return image_ids
    
    def _post_article_images_facebook(self, image_ids):
        self.ensure_one()
        if image_ids:
            param_list = []
            for index, image in enumerate(image_ids):
                param_list.append('attached_media[%s]={"media_fbid":"%s"}'%(index, image))
            if self.schedule_later:
                self._check_schedule_date()
                timestamp = self._datetime_to_timestamp(self.schedule_date)
                param_list.extend(['scheduled_publish_time=%s'%timestamp, 'published=false'])
            
            str_attachments = '&'.join(param_list)
            
            url = HOST + "/%s/feed?access_token=%s&%s&"%(self.page_id.social_page_id, self.page_id.facebook_page_access_token, str_attachments) + urlencode({'message':self.message})
            req = requests.post(url)
            req.raise_for_status()
            data = req.json()
            if data:
                page_post = data['id'].split("_")
                url = "https://www.facebook.com/permalink.php?story_fbid=%s&id=%s"%(page_post[1], page_post[0])
                update_post = self._prepare_data_after_post(data['id'], url)
                if self.schedule_later:
                    update_post['state'] = 'scheduled'
                    update_post['date_posted'] = self.schedule_date
                self.write(update_post)

    def _delete_post_social(self):
        self.ensure_one()
        if self.media_id.social_provider == 'facebook':
            url = HOST + "/%s?access_token=%s"%(self.social_post_id, self.page_id.facebook_page_access_token)
            req = requests.delete(url)
            req.raise_for_status()
        else:
            return super(SocialPost, self)._delete_post_social()

    def _get_post_comments_facebook(self, post_or_comment_id, comment_type):
        self.ensure_one()
        data = []
        page_access_token = self.page_id.facebook_page_access_token
        order_by='reverse_chronological' if comment_type == 'comment' else 'chronological'
        if post_or_comment_id and page_access_token:
            url = HOST + "/%s/comments?fields=attachment,comment_count,like_count,user_likes,from{id,name,picture},created_time,message,is_hidden&order=%s&limit=20&access_token=%s"%(post_or_comment_id, order_by , page_access_token)
            try:
                req = requests.get(url)
                req.raise_for_status()
                data_dict_json = req.json()
                data = data_dict_json.get('data', False)
                for comment in data:
                    author = comment.get('from', False)
                    if author:
                        author_image = author.get('picture', False) and author.get('picture', False).get('data', False)
                        author.update({'author_image': author_image and author_image.get('url', False)})
                    else:
                        comment['from'] = {'id': False, 'name': '# User', 'author_image_src': '/viin_social_facebook/static/img/user_default.png'}
                    date_comment = parse(comment['created_time'])
                    date_comment = datetime.datetime.combine(date_comment.date(), date_comment.time())
                    date_comment = self._set_datetime(date_comment)
                    comment.update({'created_time': date_comment})
                    attachment = comment.get('attachment', False)
                    if attachment:
                        attachment_type = attachment.get('type', False)
                        if attachment_type == 'animated_image_share':
                            attachment_source = attachment.get('media', False).get('source', False)
                        else:
                            attachment_source = attachment.get('media', False).get('image', False).get('src', False)
                        comment.update({'attachment':{'type': attachment_type,
                                                      'src': attachment_source}})
            except requests.HTTPError:
                return data
        return data
    
    def _add_comment_facebook(self, comment_message, comment_id=False):
        self.ensure_one()
        self._check_right_comment()
        data = False
        comment_or_post_id = comment_id or self.social_post_id
        page_access_token = self.page_id.facebook_page_access_token
        if comment_or_post_id and comment_message and page_access_token:
            url = HOST + "/%s/comments?access_token=%s" % (comment_or_post_id, page_access_token)
            req = requests.post(url, data={'message': comment_message})
            req.raise_for_status()
            data = req.json()
            data = data.get('id',False)
        return data
    
    def _check_like_comment_facebook(self, comment_id, page_access_token):
        self.ensure_one()
        if comment_id and page_access_token:
            url = HOST + "/%s?fields=user_likes&access_token=%s"%(comment_id, page_access_token)
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()
            if data.get('user_likes', False):
                return True
        return False

    def _like_comment_facebook(self, comment_id):
        self.ensure_one()
        self._check_right_comment()
        success_like = False
        page_access_token = self.page_id.facebook_page_access_token
        if comment_id and page_access_token:
            user_liked = self._check_like_comment_facebook(comment_id, page_access_token)
            if user_liked:
                return False
            url = HOST + "/%s/likes?access_token=%s"%(comment_id, page_access_token)
            try:
                req = requests.post(url)
                req.raise_for_status()
                data = req.json()
                if data.get('success', False):
                    success_like = True
            except requests.HTTPError:
                success_like = False
        return success_like

    def _unlike_comment_facebook(self, comment_id):
        self.ensure_one()
        self._check_right_comment()
        success_unlike = False
        page_access_token = self.page_id.facebook_page_access_token
        if comment_id and page_access_token:
            url = HOST + "/%s/likes?access_token=%s"%(comment_id, page_access_token)
            try:
                req = requests.delete(url)
                req.raise_for_status()
                data = req.json()
                if data.get('success', False):
                    success_unlike = True
            except requests.HTTPError:
                success_unlike = False
        return success_unlike

    def _delete_comment_facebook(self, comment_id):
        self.ensure_one()
        self._check_right_comment()
        success_delete_comment = False
        page_access_token = self.page_id.facebook_page_access_token
        if comment_id and page_access_token:
            url = HOST + "/%s?access_token=%s"%(comment_id, page_access_token)
            try:
                req = requests.delete(url)
                req.raise_for_status()
                data = req.json()
                if data.get('success', False):
                    success_delete_comment = True
            except requests.HTTPError:
                success_delete_comment = False
        return success_delete_comment

    def _update_post_engagement_facebook(self):
        self.ensure_one()
        post_id = self.social_post_id
        page_access_token = self.page_id.facebook_page_access_token
        engagement = self._get_facebook_post_insights(post_id, page_access_token)
        if engagement:
            likes_count = engagement.get('total_likes', False) or self.likes_count
            comments_count = engagement.get('total_comments', False) or self.comments_count
            shares_count = engagement.get('total_shares', False) or self.shares_count
            self.write({
                'likes_count': likes_count,
                'comments_count': comments_count,
                'shares_count': shares_count
                })
        return {'comments_count': self.comments_count,
                'likes_count': self.likes_count,
                'shares_count': self.shares_count}

    def _get_post_attachment_facebook(self):
        self.ensure_one()
        attachments = []
        page_access_token = self.page_id.facebook_page_access_token
        post_id = self.social_post_id
        if post_id and page_access_token:
            url = HOST + "/%s/attachments?access_token=%s"%(post_id, page_access_token)
            try:
                req = requests.get(url)
                req.raise_for_status()
                data = req.json()
                for element in data.get('data', False):
                    if element.get('subattachments', False):
                        for attachment in element.get('subattachments', False).get('data', False):
                            attachment_type = attachment.get('type', False)
                            if attachment_type == 'animated_image_share':
                                attachment_source = attachment.get('media', False).get('source', False)
                            else:
                                attachment_source = attachment.get('media', False).get('image', False).get('src', False)
                            attachments.append({'type': attachment_type, 'src': attachment_source})
            except requests.HTTPError:
                attachments = []
        return attachments
