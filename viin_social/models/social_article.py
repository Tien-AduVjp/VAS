from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests


class SocialArticle(models.Model):
    _name = 'social.article'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Social Article'
    _order = 'create_date desc'

    def _default_domain_user(self):
        if self.env.user.has_group('viin_social.viin_social_group_approve'):
            return []
        return [('id', '=', self.env.user.id)]

    name = fields.Char(string="Title", required=True)
    post_ids = fields.One2many('social.post', 'article_id', string='Posts', help="Posts from this article")
    page_ids = fields.Many2many('social.page', string='Post on', readonly=True, states={'draft': [('readonly', False)]})
    message = fields.Text(string='Message', help="Content of this article", required=True)
    message_view_more = fields.Text(string='Message More', help="Showing 1 piece of content in addition to the kanban", compute="_compute_message_view_more")
    attachment_type = fields.Selection([('none', "None"), 
                                        ('file', "Attach Files")], default='none', string="Attachment Type", help="Files: Image or Videos")
    attachment_ids = fields.Many2many(comodel_name='ir.attachment', relation='social_article_ir_attachment_image_rel', string='Attach Images/Videos')
    attachment_link = fields.Char(string='Attach Link')
    attachment_link_title = fields.Char(string='Attach Link Title')
    author_id = fields.Many2one('res.users', string='Author', default=lambda self: self.env.user, readonly=True)
    assign_id = fields.Many2one('res.users', string='Assign to', default=lambda self: self.env.user, domain=_default_domain_user, tracking=True, help="User has right to this article")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirmed'),
                              ('cancelled', 'Cancelled')], string='State', default='draft', tracking=True)
    post_count = fields.Integer(string="Total posts posted", compute='_compute_post_count')
    media_ids = fields.Many2many('social.media', string='Post on Media', compute='_compute_media_ids')
    can_cancel = fields.Boolean(string='Can Cancel', compute='_compute_can_cancel')
    
    def _compute_can_cancel(self):
        for r in self:
            current_user = self.env.user
            if self.state == 'confirmed' and (current_user == r.assign_id and current_user.has_group('viin_social.viin_social_group_approve') or current_user.has_group('viin_social.viin_social_group_admin')):
                r.can_cancel = True
            else: 
                r.can_cancel = False
    
    @api.depends('page_ids')
    def _compute_media_ids(self):
        for r in self:
            r.media_ids = r.page_ids.media_id

    @api.depends('post_ids', 'post_ids.state')
    def _compute_post_count(self):
        articles_data = self.env['social.post'].read_group([('article_id', 'in', self.ids)], ['article_id'], ['article_id'])
        mapped_data = dict([(a['article_id'][0], a['article_id_count']) for a in articles_data]) 
        for r in self:
            r.post_count = mapped_data.get(r.id, 0)
    
    @api.depends('message')
    def _compute_message_view_more(self):
        for r in self:
            if r.message and len(r.message) > 140:
                r.message_view_more = r.message[0:140]
            else:
                r.message_view_more = False

    @api.onchange('attachment_link')
    def _onchange_attachment_link(self):
        self._check_attachment_link()

    def _update_attachment(self):
        for r in self:
            r.attachment_ids.write({'res_id': r.id})

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SocialArticle, self).create(vals_list)
        res._update_attachment()
        return res

    def write(self, vals):
        for r in self:
            state_list = r.post_ids.mapped('state')
            if set(('posted','scheduled')) & set(state_list):
                raise UserError(_("You cannot edit Article %s because Article already have at least 1 post is posted (include the scheduled post)")%(r.name))
            if 'message' in vals.keys():
                r.post_ids.with_context(check_right=False).write({'message': vals.get('message', False)})
        res = super(SocialArticle, self).write(vals)
        self._update_attachment()
        return res
    
    def unlink(self):
        for r in self:
            if r.state == 'confirmed':
                raise UserError(_("You cannot delete Article %s when state is 'Confirmed'")%r.name)
        return super(SocialArticle, self).unlink()

    def action_draft(self):
        self.write({'state': 'draft'})
        
    def action_confirm(self):
        self.ensure_one()
        if not self.page_ids:
            raise UserError(_("You need to choose at least one page"))
        if self.attachment_type == 'file':
            if not self.attachment_ids:
                raise UserError(_("When choosing 'Attach Files', you need to upload a photo or video file"))
        self.attachment_ids.write({'public': True})
        # create post list
        post_list = []
        for page in self.page_ids:
            post_data = {
                'article_id': self.id,
                'page_id': page.id,
                'message': self.message,
                'attachment_link': self.attachment_link,
                'attachment_link_title': self.attachment_link_title
                }
            post_list.append(post_data) 
        posts = self.env['social.post'].create(post_list)
        self.state = 'confirmed'
        link_posts = ["<a href=# data-oe-model=social.post data-oe-id=%s>%s</a>"%(post.id, post.page_id.display_name) for post in posts]
        self.message_post(body=_("<ul class='o_mail_thread_message_tracking'> \
                            <li>%s Post have created: %s </li> \
                        </ul>")%(len(link_posts), ", ".join(link_posts)))

    def action_cancel(self):
        self.ensure_one()
        if not self.post_ids.filtered(lambda r:r.state in ('posted', 'scheduled')) and self.env.user == self.assign_id:
            self.post_ids.with_context(check_right=False).action_delete_post()
        else:
            if not self.env.user.has_group('viin_social.viin_social_group_approve'):
                raise UserError(_("You cannot delete posts already posted. You need to be in the Approve group and have permissions with the respective Posts"))
            self.post_ids.with_context(delete_on_social=True).action_delete_post()
        self.state = 'cancelled'

    def action_view_posts(self):
        action = self.env.ref('viin_social.social_post_action')
        result = action.read()[0]
        if self.post_count != 1:
            result['domain'] = "[('article_id', '=', %s)]"%(self.id)
        elif self.post_count == 1:
            res = self.env.ref('viin_social.social_post_view_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.post_ids.id
        return result
    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        # add partners to Followers list when mentioning
        if self.user_has_groups('viin_social.viin_social_group_editor'):
            return super(SocialArticle, self.sudo().with_context(mail_post_autofollow=True)).message_post(**kwargs)
        return super(SocialArticle, self).message_post(**kwargs)

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        if self.user_has_groups('viin_social.viin_social_group_editor'):
            return super(SocialArticle, self.sudo()).message_subscribe(partner_ids, channel_ids, subtype_ids)
        return super(SocialArticle, self).message_subscribe(partner_ids, channel_ids, subtype_ids)

    def _check_attachment_link(self):
        for r in self.filtered(lambda r: r.attachment_link):
            try:
                req = requests.get(r.attachment_link)
                req.raise_for_status()
            except:
                raise UserError(_("URL Unsupported or was not found"))
