from odoo import models, fields, api, _
import requests
from datetime import datetime
from dateutil.parser import parse
from odoo.exceptions import UserError

host = "https://graph.facebook.com"

class SocialPage(models.Model):
    _inherit = 'social.page'

    facebook_page_about = fields.Char(string=" About Facebook Page", readonly=True)
    facebook_page_access_token = fields.Text(string="Access Token", help="Access Token of Facebook Page" , readonly=True)
    review_ids = fields.One2many('social.review', 'page_id', string='All Reviews')
    
    users_can_message = fields.Boolean(string='Users Can Message?')
    users_can_post = fields.Boolean(string='Users Can Post?')
    review_posts_by_other = fields.Boolean(string='Review Post By Other?')
    users_can_post_photos = fields.Boolean(string='Users Can Post Photos?')
    users_can_tag_photos = fields.Boolean(string='Users Can Tag Photos?')
    profanity_filter = fields.Selection([('Off', 'Off'), ('Medium', 'Medium'), ('Strong', 'Strong')], string='Profanity Filter?',default='Strong', required=True)
    is_published = fields.Boolean(string='Is Published?')
    
    engaged_current = fields.Integer(string='Engagements - in 30 days', readonly=True, help='The number of engagements within 30 days')
    views_current = fields.Integer(string='Views - in 30 days', readonly=True, help='The number of views within 30 days')
    engaged_pre = fields.Integer(string='Engagements - between 30 and 60 days ago',readonly=True, help='The number of engagements  from 30 to 60 days ago')
    views_pre = fields.Integer(string='Views - between 30 and 60 days ago',readonly=True, help='The number of views from 30 to 60 days ago')
    engaged_rate = fields.Float(compute="_compute_rate", digits=(10,2), help='(%) The rate of engagements between two time intervals')
    views_rate = fields.Float(compute="_compute_rate", digits=(10,2), help='(%) - The rate of views between two time intervals')

    @api.depends('engaged_current', 'views_current', 'engaged_pre', 'views_pre')
    def _compute_rate(self):
        for r in self:
            r.engaged_rate = ((r.engaged_current - r.engaged_pre) / r.engaged_pre)*100 if r.engaged_pre else False
            r.views_rate = ((r.views_current - r.views_pre) / r.views_pre)*100 if r.views_pre else False
                
    @api.onchange('users_can_message', 'users_can_post', 'review_posts_by_other', 'users_can_post_photos', 'users_can_tag_photos', 'profanity_filter', 'is_published')
    def _onchange_setting(self):
        option = ''
        page_old = self._origin
        if page_old.users_can_message != self.users_can_message:
            option = '{USERS_CAN_MESSAGE: true}' if self.users_can_message else '{USERS_CAN_MESSAGE: false}'
        elif page_old.users_can_post != self.users_can_post:
            option = '{USERS_CAN_POST: true}' if self.users_can_post else '{USERS_CAN_POST: false}'
        elif page_old.review_posts_by_other != self.review_posts_by_other:
            option = '{REVIEW_POSTS_BY_OTHER: true}' if self.review_posts_by_other else '{REVIEW_POSTS_BY_OTHER: false}'
        elif page_old.users_can_post_photos != self.users_can_post_photos:
            option = '{USERS_CAN_POST_PHOTOS: true}' if self.users_can_post_photos else '{USERS_CAN_POST_PHOTOS: false}'
        elif page_old.users_can_tag_photos != self.users_can_tag_photos:
            option = '{USERS_CAN_TAG_PHOTOS: true}' if self.users_can_tag_photos else '{USERS_CAN_TAG_PHOTOS: false}'
        elif page_old.profanity_filter != self.profanity_filter:
            option = "{PROFANITY_FILTER: '%s'}"%(self.profanity_filter)
        else:
            option = '{IS_PUBLISHED: true}' if self.is_published else '{IS_PUBLISHED: false}'     
        
        url = host + '/%s/settings?option=%s&access_token=%s'%(self.social_page_id, option, self.facebook_page_access_token)
        req = requests.post(url)
        req.raise_for_status()
        
        return {'warning':{
                            'title': _('Notice'),
                            'message': _('Update Page Setting Success')
                            }}

    def action_refresh_reviews(self):
        self.env['social.review']._get_all_reivews(self.id, self.social_page_id, self.facebook_page_access_token)
        
    def action_view_all_reviews(self):
        url = 'https://www.facebook.com/%s/reviews'%(self.social_page_id)
        return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new'
            }

    def action_sinchronized_post(self):
        if self.media_id.social_provider == 'facebook':
            url = host + "/%s/feed?fields=message,from,created_time,permalink_url,likes.summary(1),shares,comments.filter(stream).limit(1000000).summary(1),attachments&limit=100&access_token=%s"%(self.social_page_id, self.facebook_page_access_token)
            req = requests.get(url)
            req.raise_for_status()
            data_dict_json = req.json()
            
            post_list = data_dict_json.get('data', False)
            scheduled_post_list = self._synchronize_scheduled_post()
            post_list = post_list + scheduled_post_list
            social_post = self.env['social.post']
            if post_list:
                actual_post_list = []
                for post in post_list:
                    is_author = self._check_author_post(post,self.social_page_id)
                    if not post.get('is_schesdule_later', False) and is_author:
                        post_insights = social_post._get_facebook_post_insights(post['id'], self.facebook_page_access_token)
                        post.update(post_insights)
                        actual_post_list.append(post)
                social_post.with_context(page_id=self.id)._update_facebook_post_list(actual_post_list, self.id)
            self._synchronize_scheduled_post()
        else:
            return super(SocialPage, self).action_sinchronized_post()

    def _update_facebook_page_list(self, page_list, media_id):
        social_pages = self.env['social.page'].with_context(active_test=False).search([('media_id', '=', media_id)])
        social_page_ids = social_pages.mapped('social_page_id')
    
        page_ids_new = []
        page_ids_update = []
        page_ids_create = []
        for page in page_list:
            page_ids_new.append(page['id'])
            data = self._prepare_facebook_page_data(page)
            if page['id'] not in social_page_ids:
                data['media_id'] = self._context.get('media_id', False)
                page_ids_create.append(data)
            else:
                data['active'] = True
                page_ids_update.append(data)
        
        # Page list for Create
        if page_ids_create:
            self.env['social.page'].create(page_ids_create)

        # Page list for Update
        for page in page_ids_update:
            page_update = social_pages.filtered(lambda r:r.social_page_id == page['social_page_id'])
            if page_update:
                page_update.write(page)

        # Page list for Inactive
        pages_for_inactive = social_pages.filtered(lambda r:r.social_page_id not in page_ids_new)
        if pages_for_inactive:
            pages_for_inactive.write({'active': False})

    def _get_facebook_page_engagement(self, page_id, page_access_token):
        since, until = self._get_timestamp(60)
        until += 24*60*60
        url = host + "/%s/insights?metric=page_engaged_users,page_views_total&period=day&since=%s&until=%s&access_token=%s"%(page_id, since, until, page_access_token)
        req = requests.get(url)
        req.raise_for_status()
        data_dict = req.json()
        engagement_data = {}
        if data_dict.get('data', False):
            # list data :Sort by date asc
            for metric in data_dict['data']:
                values_30_before = sum([value['value'] for index, value in enumerate(metric.get('values', []), start=1) if index<=30])
                values_30_after = sum([value['value'] for index, value in enumerate(metric.get('values', []), start=1) if index>30])
                if metric.get('name','') == 'page_engaged_users':
                    engagement_data['engaged_pre'] = values_30_before
                    engagement_data['engaged_current'] = values_30_after
                if metric.get('name','') == 'page_views_total':
                    engagement_data['views_pre'] = values_30_before
                    engagement_data['views_current'] = values_30_after
        return engagement_data

    def _get_timestamp(self, days):
        timestamp = int(datetime.timestamp(datetime.now()))
        timestamp_ago = timestamp - days*24*60*60
        return timestamp_ago, timestamp

    def _prepare_facebook_page_data(self, page):
        image = self._read_image_from_url(page['picture']['data']['url'])
        return {
                'social_page_id': page['id'],
                'name': page['name'],
                'description': page.get('description', False),
                'follower_count': page.get('fan_count', False),
                'facebook_page_about': page.get('about', False),
                'facebook_page_access_token': page['access_token'],
                'social_provider': 'facebook',
                'social_page_url': "https://www.facebook.com/%s"%(page['id']),
                'image': image,
                'views_pre': page.get('views_pre', False),
                'views_current': page.get('views_current', False),
                'engaged_pre': page.get('engaged_pre', False),
                'engaged_current': page.get('engaged_current', False)
                }
    
    def _synchronize_scheduled_post(self):
        url = host + "/%s/scheduled_posts?fields=message,created_time,permalink_url,shares,attachments&limit=100&access_token=%s"%(self.social_page_id, self.facebook_page_access_token)
        req = requests.get(url)
        req.raise_for_status()
        data_dict_json = req.json()
        post_list = data_dict_json.get('data', [])
        for post in post_list:
            post.update({'is_schesdule_later': True})
        return post_list

    """
        Webhooks : auto check when synchronize all pages
        check page has registered for notification yet
         If not, then register for each page
            - feed : Describes nearly all changes to a Page's feed, such as Posts, shares, likes, etc.
                *https://developers.facebook.com/docs/graph-api/webhooks/reference/page/#feed
            - mention : Describes new mentions of a page, including mentions in comments, posts, etc. 
                        Some comment_id and post_id fields returned in mention webhooks may not be queried due to missing permissions including privacy issues.
                *https://developers.facebook.com/docs/graph-api/webhooks/reference/page/#mention
    """
    def _check_page_subscribed_apps(self):
        for r in self:
            url = host + "/%s/subscribed_apps?access_token=%s"%(r.social_page_id, r.facebook_page_access_token)
            req = requests.get(url)
            req.raise_for_status()
            data_list = req.json().get('data', [])
            for data in data_list:
                if data.get('id', '') == r.env.company.facebook_app_id:
                    fields = data.get('subscribed_fields', [])
                    if set(fields) >= {'feed', 'messages', 'message_mention'}:
                        self -= r
        if self:
            self._page_subscrib_apps()
    
    # https://developers.facebook.com/docs/graph-api/reference/page/subscribed_apps/#Reading 
    def _page_subscrib_apps(self):
        for r in self:
            url = host + "/%s/subscribed_apps?subscribed_fields=messages,message_mention,feed&access_token=%s"%(r.social_page_id, r.facebook_page_access_token)
            req = requests.post(url)
            req.raise_for_status()
    
    def action_cacncel_subscrib_appp(self):
        for r in self:
            url = host + "/%s/subscribed_apps?access_token=%s"%(r.social_page_id, r.facebook_page_access_token)
            req = requests.delete(url)
            req.raise_for_status()
    

    def _prepare_social_message_facebook_data(self, messages, old_conversation=False):
        if old_conversation:
            old_messages = old_conversation.channel_message_ids
        page_id = self.social_page_id
        message_datas = []
        attachments = []
        old_attachments = self.env['ir.attachment']
        messages.reverse()
        subtype_id = self.env.ref('mail.mt_comment').id
        for message in messages:
            old_message = False
            if old_conversation:
                old_message = old_messages.filtered(lambda m: m.social_message_id == message.get('id', False))
                old_message = old_message[0] if old_message else False
            if old_message and old_message.attachment_ids:
                old_attachments |= old_message.attachment_ids
            attachments = []
            message_attachments = message.get('attachments',False) and message.get('attachments',False).get('data',[]) or []
            for attachment in message_attachments:
                attachment_url = attachment.get('image_data',False) and attachment.get('image_data',False).get('url',False) or attachment.get('file_url',False)
                attachment = (0,0,{
                    'type': 'url',
                    'url': attachment_url,
                    'name': attachment.get('name',False),
                    'mimetype': attachment.get('mime_type',False)
                    })
                attachments.append(attachment)
            sticker_url = message.get('sticker',False)
            if sticker_url:
                attachment = (0,0,{
                    'type': 'url',
                    'url': sticker_url,
                    'name': 'social_sticker_facebook',
                    'mimetype': 'image/png'
                    })
                attachments.append(attachment)
            message_data = {'social_message_id': message.get('id', False),
                            'body': message.get('message', ''),
                            'subtype_id': subtype_id,
                            'attachment_ids': attachments
                            }
            author = message.get('from', False)
            if author and author.get('id', False) != page_id:
                message_data.update({
                    'author_id': False,
                    'email_from': author.get('name','abc@example.viindoo.com'),
                    })
            created_time = parse(message['created_time'])
            created_time = datetime.combine(created_time.date(), created_time.time())
            message_data.update({'date': created_time})
            if old_message:
                message_datas.append((1,old_message.id,message_data))
            else:
                message_data.update({
                    'message_type': 'comment'
                    })
                message_datas.append((0,0,message_data))
        if old_attachments:
            old_attachments.unlink()
        return message_datas

    def _prepare_social_conversation_facebook_data(self, conversation, old_conversation=False):
        self.ensure_one()
        conversation_data = {'channel_type': 'social_chat',
                             'public': 'private',
                             'email_send': False,
                             'channel_message_ids': self._prepare_social_message_facebook_data(messages=conversation.get('messages', False).get('data', []), old_conversation=old_conversation),
                             'social_conversation_id': conversation.get('id', False),
                             'social_page_id': self.id}
        if not old_conversation:
            default_members = [(6,0,[])]
            for partner in self.member_ids.partner_id:
                default_members.append((0,0,{'partner_id': partner.id}))
            conversation_data.update({'channel_last_seen_partner_ids': default_members})
        
        participants = conversation.get('participants', False) and conversation.get('participants', False).get('data', []) or []
        for participant in participants:
            if participant.get('id', False) != self.social_page_id:
                conversation_data.update({'name': "[%s] %s"%(self.name, participant.get('name', 'Facebook User')),
                                          'social_participant_id': participant.get('id', False),
                                          })
        return conversation_data

    def _get_social_page_message_facebook(self):
        conversation_create_datas = []
        MailChannel = self.env['mail.channel'].sudo()
        old_conversations = MailChannel.search([('social_page_id','=',self.id)])
        self.ensure_one()
        page_id = self.social_page_id
        page_access_token = self.facebook_page_access_token
        if page_id and page_access_token:
            url = host + "/%s/conversations?fields=participants,messages.limit(1000000){from,message,sticker,attachments,created_time}&access_token=%s"%(page_id, page_access_token)
            try:
                req = requests.get(url)
                req.raise_for_status()
                data_dict_json = req.json()
                data = data_dict_json.get('data', False)
                for conversation in data:
                    old_conversation = old_conversations.filtered_domain([('social_conversation_id', '=', conversation.get('id', False))])
                    if old_conversation:
                        old_conversation.write(self._prepare_social_conversation_facebook_data(conversation=conversation, old_conversation=old_conversation))
                    else:
                        conversation_create_datas.append(self._prepare_social_conversation_facebook_data(conversation))
                MailChannel.create(conversation_create_datas)
            except requests.HTTPError:
                raise UserError("An error occurred")

    @api.model
    def _check_author_post(self, post, social_page_id):
        author_id = post.get('from', {}).get('id', False) 
        return author_id == social_page_id
 