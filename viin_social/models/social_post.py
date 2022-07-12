from odoo import models, fields, api, _
from odoo.tools.image import image_data_uri
from odoo.exceptions import UserError

class SocialPost(models.Model):
    _name = 'social.post'
    _description = 'Social Post'
    _order = 'date_posted desc'

    article_id = fields.Many2one('social.article', string='Article', help="Source of this post", readonly=True)
    page_id = fields.Many2one('social.page', string='Page', required=True, readonly=True)
    message = fields.Text(string='Message', help="Content of this post", readonly=True)
    message_view_more = fields.Text(string='Message More', help="Showing 1 piece of content in addition to the kanban", compute="_compute_message_view_more")
    attachment_type = fields.Selection(related='article_id.attachment_type', store=True)
    attachment_ids = fields.Many2many(related='article_id.attachment_ids')
    attachment_link = fields.Char(string='Attach Link', readonly=True)
    attachment_link_title = fields.Char(string='Attach Link Title', readonly=True)
    media_id = fields.Many2one('social.media', related='page_id.media_id', store=True)
    likes_count = fields.Integer(string='Total Likes', readonly=True)
    comments_count = fields.Integer(string='Total Comments', readonly=True)
    shares_count = fields.Integer(string='Total Shares', readonly=True)
    views_count = fields.Integer(string='Total Views', readonly=True)
    social_post_id = fields.Char(string='Social Post ID', help="ID of this post on Social Media", readonly=True)
    social_post_url = fields.Char(string='Social Post URL', help="URL of this post on Social Media", readonly=True)
    state = fields.Selection([('ready', 'Ready'),
                              ('scheduled', 'Scheduled'),
                              ('posted', 'Posted'),
                              ('cancelled', 'Cancelled')], string='State', default='ready', readonly=True, tracking=True)
    active = fields.Boolean(string="Active", default=True)
    date_posted = fields.Datetime(string="Date Posted", readonly=True)
    user_posted = fields.Many2one('res.users', string='Posted by', readonly=True)

    @api.depends('message')
    def _compute_message_view_more(self):
        for r in self:
            if r.message and len(r.message) > 140:
                r.message_view_more = r.message[0:140]
            else:
                r.message_view_more = False

    def write(self, vals):
        if self._context.get('check_right', True):
            self._check_access_on_post()
        if vals.get('state', False):
            origin_state = dict(self._fields['state'].selection).get(self.state, False)
            new_state = dict(self._fields['state'].selection).get(vals['state'], False)
            for r in self:
                if r.article_id:
                    r.article_id.message_post(body=_("<ul class='o_mail_thread_message_tracking'> \
                                                            <li>%s' Post State: %s \
                                                                <span class='fa fa-long-arrow-right' role='img' aria-label='Changed' title='Changed'></span> %s \
                                                            </li> \
                                                        </ul>")%(r.page_id.display_name,origin_state,new_state))
        return super(SocialPost, self).write(vals)
    
    def unlink(self):
        if self._context.get('check_right', True):
            self._check_access_on_post()
        for article in self.article_id:
            posts_remove = self.filtered(lambda record: record.article_id == article)
            article.message_post(body=_("<ul class='o_mail_thread_message_tracking'> \
                                        <li>%s Post is removed: %s</li> \
                                    </ul>")%(len(posts_remove),", ".join(posts_remove.mapped('page_id.display_name'))))
        return super(SocialPost, self).unlink()
    
    def action_post_article(self):
        self.ensure_one()
        user = self.env.user
        check_access = user in self.page_id.assign_id + self.media_id.assign_id
        if user.has_group('viin_social.viin_social_group_admin') or user.has_group('viin_social.viin_social_group_approve') and check_access:
            if self.attachment_type == 'file':
                self._post_file()
            else:
                self._post_article()
        else:
            raise UserError(_("You don't have rights post article to the page"))

    def action_cancel_post(self):
        self.write({'state': 'cancelled'})
    
    def action_set_ready_post(self):
        self.write({'state': 'ready'})
    
    def action_delete_post(self):
        if self._context.get('check_right',True):
            self._check_access_on_post()
        posted = self.filtered(lambda r:r.state in ('posted', 'scheduled'))
        for r in posted:
            r._delete_post_social()
        self.unlink()

    def action_view_post(self):
        self.ensure_one()
        if self.social_post_url:
            return {
                    'type': 'ir.actions.act_url',
                    'url': self.social_post_url,
                    'target': 'new'
                }

    def action_edit_post(self):
        self._check_access_on_post()
        ctx = {
            'default_post_id': self.id,
            'default_message': self.message
            }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'social.post.action.edit.post',
            'view_mode': 'form',
            'view_id': self.env.ref('viin_social.social_post_action_edit_post_view_form').id,
            'target': 'new',    
            'context': ctx,
            }

    def action_synchronize_all_post(self):
        pages = self.env['social.page'].sudo().search([])
        for page in pages:
            page.action_sinchronized_post()
        
    def _post_article(self):
        # for inherit
        pass
    
    def _post_file(self):
        # for inherit
        pass

    def _delete_post_social(self):
        # for inherit
        pass

    def _prepare_data_after_post(self, social_post_id, post_url):
        return {
            'social_post_id': social_post_id,
            'social_post_url': post_url,
            'date_posted': fields.Datetime.now(),
            'user_posted': self.env.user.id,
            'state': 'posted'}
    
    def _check_access_on_post(self):
        user = self.env.user
        for r in self:
            check_access = user in r.page_id.assign_id + r.media_id.assign_id
            check_raise= False
            if not user.has_group('viin_social.viin_social_group_admin') and not check_access:
                    check_raise = True
            if r.state in ('posted','scheduled'):
                if not user.has_group('viin_social.viin_social_group_approve'):
                    check_raise = True
            if check_raise:
                raise UserError(_("You don't have rights on the post: %s")%r)

    def _get_post_comments(self, comment_or_post_id, comment_type):
        comments = []
        if self.media_id.social_provider != 'none':
            custom_get_post_comments_method = '_get_post_comments_%s' % self.media_id.social_provider
            if hasattr(self, custom_get_post_comments_method):
                comments = getattr(self, custom_get_post_comments_method)(comment_or_post_id, comment_type)
        return comments

    def get_post_content(self):
        self.ensure_one()
        comments = []
        if self.state == 'posted':
            social_post_id = self.social_post_id
            comment_type = 'comment'
            comments = self._get_post_comments(social_post_id, comment_type)
        attachments = []
        for attachment in self.attachment_ids:
            base_url = attachment.get_base_url()
            address_image = '/web/image/%s'%(attachment.id)
            attachments.append({
                'type': 'photo',
                'src': base_url + address_image
                })
        if not self.attachment_ids:
            attachments = self._get_post_attachment()
        post_data = {
            'post_id': self.id,
            'page_name': self.page_id.name,
            'page_image': image_data_uri(self.page_id.image) if self.page_id.image else False,
            'post_message': self.message,
            'post_like_count' : self.likes_count,
            'post_comment_count' : self.comments_count,
            'first_level_comment_count': len(comments),
            'post_share_count' : self.shares_count,
            'social_media_name' : self.media_id.name,
            'attachments': attachments,
            'attachment_link': self.attachment_link,
            'attachment_link_title': self.attachment_link_title,
            'media': self.media_id,
            'comments': comments,
            'state': self.state,
            }
        return post_data

    def get_reply_comments(self, comment_id):
        comment_type = 'reply'
        reply_data = {'replys': self._get_post_comments(comment_id, comment_type)}
        return reply_data

    def _add_comment(self, comment_message, comment_id=False):
        return_comment_id = False
        if self.media_id.social_provider != 'none':
            custom_add_comment_method = '_add_comment_%s' % self.media_id.social_provider
            if hasattr(self, custom_add_comment_method):
                return_comment_id = getattr(self, custom_add_comment_method)(comment_message, comment_id)
        return return_comment_id

    def add_comment(self, comment_message, comment_id=False):
        self.ensure_one()
        self._check_posted()
        return_comment_id = self._add_comment(comment_message, comment_id)
        comment_data = False
        if return_comment_id:
            data = {
                'id': return_comment_id,
                'comment_count': 0,
                'like_count': 0,
                'message': comment_message,
                'created_time': self._set_datetime(fields.Datetime.now()),
                'from':{
                    'name': self.page_id.name,
                    'page_image': self.page_id.image and image_data_uri(self.page_id.image) or False
                    }
                }
            if comment_id:
                comment_data = {
                    'replys': [data]
                    }
            else:
                comment_data  = {
                    'page_image': self.page_id.image and image_data_uri(self.page_id.image) or False,
                    'comments': [data]
                    }
        return comment_data

    def _like_comment(self, comment_id, unlike=False):
        success_like = False
        if self.media_id.social_provider != 'none':
            custom_like_comment_method = unlike and '_unlike_comment_%s' or '_like_comment_%s'
            custom_like_comment_method %= self.media_id.social_provider
            if hasattr(self, custom_like_comment_method):
                success_like = getattr(self, custom_like_comment_method)(comment_id)
        return success_like

    def like_comment(self, comment_id):
        self.ensure_one()
        if self._like_comment(comment_id):
            return 1
        elif self._like_comment(comment_id, unlike=True):
            return -1   
        else:
            return 0
    
    def _delete_comment(self, comment_id):
        self._check_right_comment()
        success_delete_comment = False
        if self.media_id.social_provider != 'none':
            custom_delete_comment_method = '_delete_comment_%s' % self.media_id.social_provider
            if hasattr(self, custom_delete_comment_method):
                success_delete_comment = getattr(self, custom_delete_comment_method)(comment_id)
        return success_delete_comment

    def delete_comment(self, comment_id):
        return self._delete_comment(comment_id)

    def _update_post_engagement(self):
        self.ensure_one()
        if self.media_id.social_provider != 'none':
            custom_update_post_engagement_method = '_update_post_engagement_%s' % self.media_id.social_provider
            if hasattr(self, custom_update_post_engagement_method):
                data = getattr(self.with_context(check_right=False), custom_update_post_engagement_method)()
                return data

    def _check_posted(self):
        for r in self:
            if r.state != 'posted':
                raise UserError(_("The post has not been posted."))
        
    def update_post_engagement(self):
        self.ensure_one()
        self._check_posted()
        return self._update_post_engagement()

    def _update_post_from_notice(self, social_post_id):
        post = self.env['social.post'].sudo().search([('social_post_id', '=', social_post_id)], limit=1)
        if post:
            post._update_post_engagement()

    def _get_post_attachment(self):
        attachment = []
        if self.media_id.social_provider != 'none':
            custom_get_post_attachment_method = '_get_post_attachment_%s' % self.media_id.social_provider
            if hasattr(self, custom_get_post_attachment_method):
                attachment = getattr(self, custom_get_post_attachment_method)()
        return attachment
    
    def _check_right_comment(self):
        self.ensure_one()
        user = self.env.user
        admins = self.env['res.users'].search([('groups_id.id', '=', self.env.ref("viin_social.viin_social_group_admin").id)])
        users = self.page_id.member_ids + self.page_id.assign_id + self.page_id.media_id.assign_id + admins
        if user not in users:
            raise UserError(_("you don't have permission on the post"))
    
    def _set_datetime(self, datetime):
        user_tz = self.env.user.tz
        return self.env['to.base'].convert_utc_time_to_tz(datetime, tz_name=user_tz)
