from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import base64


class SocialPage(models.Model):
    _name = 'social.page'
    _description = 'Social Page'

    def _default_domain_user(self):
        group_approve = self.env.ref('viin_social.viin_social_group_editor', raise_if_not_found=False)
        group_approve = group_approve and [group_approve.id] or []
        user_ids = self.env['res.users'].search([('groups_id.id', 'in', group_approve)])
        return [('id', 'in', user_ids.ids)]

    def _default_members(self):
        users = self.env['res.users'].search([('groups_id.id', '=', self.env.ref('viin_social.viin_social_group_admin').id)])
        return users.ids

    name = fields.Char(string='Name', required=True,readonly=True, help="Name of this page on Social Media")
    description = fields.Text(string='Description',readonly=True, help="Description of this page on Social Media")
    media_id = fields.Many2one('social.media', string='Social Media', help="The Social Media which this page belongs", readonly=True)
    social_provider = fields.Char(readonly=True,help="Use to hide fields of other social")
    image = fields.Binary(string='Avatar', help="Avatar of this page", attachment=False)
    post_ids = fields.One2many('social.post', 'page_id', string='Posts', help="Posts on this page")
    article_ids = fields.Many2many('social.article', string='Articles', help="Sources of the posts on this page")
    social_page_id = fields.Char(string="Page Id on Social", readonly=True)
    social_page_url = fields.Char(string="URL of Social", readonly=True)
    assign_id = fields.Many2one('res.users', string='Approver', domain=_default_domain_user, 
                                help="User has rights to all posts of this page on social networks")
    active = fields.Boolean(string="Active",readonly=True, default=True)
    follower_count = fields.Integer(string='Total followers', readonly=True)
    engagement_count = fields.Integer(string='Total Engagements', readonly=True)
    view_count = fields.Integer(string='Total Views', readonly=True)
    like_count = fields.Integer(string='Total Likes', readonly=True)
    comment_count = fields.Integer(string='Total Comments', readonly=True)
    share_count = fields.Integer(string='Total Shares', readonly=True)
    click_count = fields.Integer(string='Total Clicks', readonly=True)
    member_ids = fields.Many2many('res.users', string='Members', domain=_default_domain_user, default=_default_members,
                                  compute='_compute_member_ids', store=True, readonly=False,
                                help="All members can: Receive Notifications, Reply/Delete Comments, and are default members on social conversation.")
    
    @api.depends('assign_id','media_id.assign_id')
    def _compute_member_ids(self):
        for r in self:
            members = r.member_ids
            if r.assign_id not in members:
                members += r.assign_id
            if r.media_id.assign_id not in members:
                members += r.media_id.assign_id
            r.member_ids = members
    
    def name_get(self):
        return self.mapped(lambda r: (r.id,"[%s] %s" %(r.media_id.name, r.name)))
    
    def write(self, vals):
        user = self.env.user
        if not user.has_group('viin_social.viin_social_group_admin'):
            for r in self:
                if 'member_ids' in vals.keys():
                    if user not in r.assign_id + r.media_id.assign_id:
                        raise UserError(_("Only the assigned user or Manager can edit members"))
        return super(SocialPage, self).write(vals)
    
    def action_sinchronized_post(self):
        # for inherit
        pass

    def _read_image_from_url(self, url):
        image_data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
        return image_data
        
    def action_get_social_page_message(self):
        self._get_social_page_message()

    def _get_social_page_message(self):
        user = self.env.user
        for r in self:
            users = r.assign_id + r.media_id.assign_id
            if not user.has_group('viin_social.viin_social_group_admin') and user not in users:
                raise UserError(_("Only the assigned user on Page/Media or Manager can synch message"))
            
            if r.media_id.social_provider != 'none':
                custom_get_social_page_message_method = '_get_social_page_message_%s' % r.media_id.social_provider
                if hasattr(self, custom_get_social_page_message_method):
                    getattr(r, custom_get_social_page_message_method)()
