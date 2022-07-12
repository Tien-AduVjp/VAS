from odoo import api, fields, models
from ..tools import bypass_karma_check_and_execute


class ForumForum(models.Model):
    _inherit = 'forum.forum'

    moderator_ids = fields.Many2many('res.users', string='Moderators',
                                     domain="[('share', '=', False)]",
                                     help='These users will have full permissions on this forum, '
                                          'without having to reach the minimum required karma.')
    is_moderator = fields.Boolean('Current User Is Moderator', compute='_compute_is_moderator')

    @api.depends_context('uid')
    def _compute_is_moderator(self):
        user = self.env.user
        is_forum_moderator = user.has_group('viin_website_forum_security_groups.group_forum_moderator')
        for r in self:
            r.is_moderator = is_forum_moderator or user in r.moderator_ids

    def _tag_to_write_vals(self, tags=''):
        if self.is_moderator:
            user = self.env.user
            if user.exists() and user.karma < self.karma_tag_create:
                method = super(ForumForum, self)._tag_to_write_vals
                return bypass_karma_check_and_execute(user, self.karma_tag_create, method, [tags])
        return super(ForumForum, self)._tag_to_write_vals(tags)
